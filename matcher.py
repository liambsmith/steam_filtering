"""Title matching for CSV games to Steam games."""
from typing import List, Dict, Any, Optional
from rapidfuzz import fuzz, process
from models import SteamGame

# Roman numeral to integer mapping
ROMAN_TO_INT = {
    'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5,
    'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9, 'x': 10
}


def clean_title(title: str) -> str:
    """Clean and normalize a game title."""
    if not title:
        return ""
    # Lowercase, strip whitespace
    title = title.lower().strip()
    return title


def normalize_numbers(title: str) -> str:
    """
    Normalize Roman numerals and other number formats.
    
    Converts Roman numerals to digits for better matching.
    """
    import re
    
    # Replace Roman numerals with digits
    def replace_roman(match):
        roman = match.group(0).lower()
        return str(ROMAN_TO_INT.get(roman, roman))
    
    # Match Roman numerals in order from largest to smallest to avoid partial matches
    # This order ensures III is matched before I
    title = re.sub(r'\b(VIII|VII|VI|IV|IX|X|III|II)\b', replace_roman, title, flags=re.IGNORECASE)
    
    # Handle single I last
    title = re.sub(r'\bI\b', '1', title)
    
    return title


def word_match(csv_title: str, steam_title: str) -> bool:
    """
    Check if CSV title matches steam title as complete words.
    
    This ensures "Hades" matches "Hades" but not "Hades II".
    Also handles number normalization (3 vs III).
    """
    # Normalize numbers in both titles
    csv_normalized = normalize_numbers(csv_title)
    steam_normalized = normalize_numbers(steam_title)
    
    csv_words = set(csv_normalized.split())
    steam_words = set(steam_normalized.split())
    
    # All CSV words must be in steam title
    return csv_words.issubset(steam_words)


def exact_match(steam_results: List[Dict[str, Any]], csv_title: str) -> Optional[Dict[str, Any]]:
    """
    Find exact match (case-insensitive) in Steam results.
    
    Uses word-level matching to avoid false positives like
    "Hades" matching "Hades II".
    
    Args:
        steam_results: List of Steam game results
        csv_title: Title from CSV file
    
    Returns:
        Best match dictionary or None
    """
    cleaned_csv = clean_title(csv_title)
    
    for result in steam_results:
        steam_title = result.get("name", "").lower().strip()
        cleaned_steam = clean_title(steam_title)
        
        # Exact match after cleaning
        if cleaned_csv == cleaned_steam:
            return result
        
        # Word-level match: all words in CSV must appear in Steam title
        # This handles "Witcher 3" -> "The Witcher 3: Wild Hunt"
        if word_match(cleaned_csv, cleaned_steam):
            return result
        
        # Check if CSV title matches the base name (before suffixes like "- The Final Cut")
        # Split on common suffix indicators
        for suffix_sep in [" - ", " -–", ":", ","]:
            if suffix_sep in cleaned_steam:
                base_steam = cleaned_steam.split(suffix_sep)[0].strip()
                if cleaned_csv == base_steam:
                    return result
    
    return None


def fuzzy_match(steam_results: List[Dict[str, Any]], csv_title: str, threshold: int = 80) -> List[Dict[str, Any]]:
    """
    Find fuzzy matches using RapidFuzz.
    
    Args:
        steam_results: List of Steam game results
        csv_title: Title from CSV file
        threshold: Minimum match score (default 80 for reasonable matching)
    
    Returns:
        List of matches sorted by score (highest first)
    """
    cleaned_csv = clean_title(csv_title)
    
    # Extract titles from Steam results
    titles = [result.get("name", "") for result in steam_results]
    
    # Use process.extract to get multiple matches
    matches = process.extract(
        cleaned_csv,
        titles,
        scorer=fuzz.WRatio,
        limit=len(titles)
    )
    
    # Filter by threshold and add metadata
    results = []
    for title, score, index in matches:
        if score >= threshold:
            results.append({
                "result": steam_results[index],
                "score": score,
                "title": title,
                "is_exact": score >= 95,
                "is_low_confidence": 90 <= score < 95
            })
    
    return results


def match_games(steam_results: List[Dict[str, Any]], csv_title: str) -> SteamGame:
    """
    Match a CSV title to Steam games and return best match.
    
    Uses a multi-step approach:
    1. Try exact word-level match
    2. Check first 10 results for word-level matches
    3. Fall back to fuzzy matching with high threshold
    
    Args:
        steam_results: List of Steam game results
        csv_title: Title from CSV file
    
    Returns:
        SteamGame object with match information
    """
    # Try exact match first
    exact = exact_match(steam_results, csv_title)
    if exact:
        return _create_game(exact, csv_title, score=100.0, is_exact=True)
    
    # Check first 10 results for word-level matches
    # This handles cases like "Hades" where API returns "Hades II" first
    check_count = min(len(steam_results), 10)
    for result in steam_results[:check_count]:
        steam_name = result.get("name", "").lower()
        if word_match(clean_title(csv_title), clean_title(steam_name)):
            return _create_game(result, csv_title, score=100.0, is_exact=False)
    
    # Try fuzzy match on all results
    matches = fuzzy_match(steam_results, csv_title)
    
    if matches:
        best = matches[0]
        return _create_game(
            best["result"],
            csv_title,
            score=best["score"],
            is_exact=best["is_exact"],
            is_low_confidence=best["is_low_confidence"]
        )
    
    # No match found - return placeholder
    return SteamGame(
        original_title=csv_title,
        steam_title=csv_title,
        appid=0,
        url="",
        match_score=0.0,
        is_exact_match=False
    )


def _create_game(
    steam_result: Dict[str, Any],
    original_title: str,
    score: float,
    is_exact: bool = False,
    is_low_confidence: bool = False
) -> SteamGame:
    """Create a SteamGame object from Steam result."""
    appid = steam_result.get("appid", 0)
    name = steam_result.get("name", "")
    price_raw = steam_result.get("price_overview", {})
    
    # Extract price
    price = None
    discount = None
    if price_raw:
        initial = price_raw.get("initial", 0)
        final = price_raw.get("final", 0)
        discount = price_raw.get("discount_percent", 0)
        # Convert cents to dollars
        price = final / 100.0 if final > 0 else None
        discount = discount if discount > 0 else None
    
    # Extract review info
    review_score = steam_result.get("review_score", 0)
    review_desc = steam_result.get("review_score_desc", "")
    
    # Calculate positive/negative from review score if available
    positive = None
    negative = None
    if review_score and review_desc:
        # Estimate based on review score description
        positive = 100  # Placeholder
        negative = 0
    
    # Extract release date (can be string or dict)
    release_date = steam_result.get("release_date", "")
    if isinstance(release_date, dict):
        release_date = release_date.get("date", "")
    
    return SteamGame(
        original_title=original_title,
        steam_title=name,
        appid=appid,
        url=f"https://store.steampowered.com/app/{appid}/",
        match_score=score,
        is_exact_match=is_exact,
        price=price,
        discount=discount,
        positive_reviews=positive,
        negative_reviews=negative,
        review_score=review_score,
        review_score_desc=review_desc,
        released=release_date,
        top_tags=[],  # Will be filled by get_game_details
        genres=[],
        developer=None,
        publisher=None,
        description=None
    )
