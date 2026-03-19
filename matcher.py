"""Title matching for CSV games to Steam games."""
from typing import List, Dict, Any, Optional
from rapidfuzz import fuzz, process
from models import SteamGame


def clean_title(title: str) -> str:
    """Clean and normalize a game title."""
    if not title:
        return ""
    # Lowercase, strip whitespace
    title = title.lower().strip()
    return title


def exact_match(steam_results: List[Dict[str, Any]], csv_title: str) -> Optional[Dict[str, Any]]:
    """
    Find exact match (case-insensitive) in Steam results.
    
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
    
    return None


def subset_match(steam_results: List[Dict[str, Any]], csv_title: str) -> Optional[Dict[str, Any]]:
    """
    Find match where CSV title is a substring of Steam title.
    
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
        
        # Check if CSV title is a substring of Steam title
        # This handles "Dark Souls III" -> "Dark Souls III Deluxe Edition"
        if cleaned_csv in cleaned_steam:
            return result
    
    return None


def fuzzy_match(steam_results: List[Dict[str, Any]], csv_title: str, threshold: int = 70) -> List[Dict[str, Any]]:
    """
    Find fuzzy matches using RapidFuzz.
    
    Args:
        steam_results: List of Steam game results
        csv_title: Title from CSV file
        threshold: Minimum match score (default 70 for reasonable matching)
    
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
                "is_low_confidence": 70 <= score < 95
            })
    
    return results


def match_games(steam_results: List[Dict[str, Any]], csv_title: str) -> SteamGame:
    """
    Match a CSV title to Steam games and return best match.
    
    Uses a multi-step approach:
    1. Try exact match
    2. Try subset match (CSV title is substring of Steam title)
    3. Fall back to first result with fuzzy warning
    
    Args:
        steam_results: List of Steam game results
        csv_title: Title from CSV file
    
    Returns:
        SteamGame object with match information
    """
    # Step 1: Try exact match
    exact = exact_match(steam_results, csv_title)
    if exact:
        return _create_game(exact, csv_title, score=100.0, is_exact=True)
    
    # Step 2: Try subset match (e.g., "Dark Souls III" -> "Dark Souls III Deluxe Edition")
    subset = subset_match(steam_results, csv_title)
    if subset:
        return _create_game(subset, csv_title, score=100.0, is_exact=False)
    
    # Step 3: Fallback to first result with warning
    # Steam API returns results in relevance order, so first result is usually best
    if steam_results:
        first = steam_results[0]
        # Calculate fuzzy score for user warning
        from rapidfuzz import fuzz
        score = fuzz.WRatio(clean_title(csv_title), first.get("name", "").lower())
        return _create_game(first, csv_title, score=score, is_exact=False)
    
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
