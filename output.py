"""Output handlers for displaying and exporting results."""
import pandas as pd
from typing import List, Optional, Dict
from models import SteamGame


def print_table(games: List[SteamGame], max_tags: int = 3):
    """
    Print games in a formatted table.
    
    Args:
        games: List of SteamGame objects
        max_tags: Maximum tags to show per game
    """
    if not games:
        print("No games found.")
        return
    
    # Print header
    print("\n" + "=" * 120)
    print(f"{'ORIGINAL TITLE':<30} {'STEAM TITLE':<35} {'RATING':<12} {'MATCH':<8} {'TAGS'}")
    print("=" * 120)
    
    for game in games:
        # Format match indicator
        if game.is_exact_match:
            match_str = "✓ Exact"
        elif game.match_score < 70:
            match_str = "🔍 Fuzzy"
        else:
            match_str = "⚠ Subset"
        
        # Format rating
        if game.review_score:
            rating = f"{game.review_score}%"
        elif game.positive_reviews:
            total = game.positive_reviews + (game.negative_reviews or 0)
            rating = f"{int(game.positive_reviews / total * 100)}%" if total > 0 else "N/A"
        else:
            rating = "N/A"
        
        # Format tags
        tags = ", ".join(game.top_tags[:max_tags])
        if len(game.top_tags) > max_tags:
            tags += f" (+{len(game.top_tags) - max_tags})"
        
        # Truncate titles
        orig_title = (game.original_title[:27] + "...") if len(game.original_title) > 30 else game.original_title
        steam_title = (game.steam_title[:32] + "...") if len(game.steam_title) > 35 else game.steam_title
        
        print(f"{orig_title:<30} {steam_title:<35} {rating:<12} {match_str:<8} {tags}")
    
    print("=" * 120)
    
    # Summary
    exact = sum(1 for g in games if g.is_exact_match)
    subset = sum(1 for g in games if not g.is_exact_match and g.match_score >= 70)
    fuzzy = sum(1 for g in games if g.match_score < 70)
    print(f"\nSummary: {len(games)} games processed ({exact} exact, {subset} subset, {fuzzy} fuzzy)")


def export_csv(games: List[SteamGame], filepath: str):
    """
    Export games to CSV file.
    
    Args:
        games: List of SteamGame objects
        filepath: Output file path
    """
    # Convert to dict list
    data = []
    for game in games:
        data.append({
            "original_title": game.original_title,
            "steam_title": game.steam_title,
            "appid": game.appid,
            "url": game.url,
            "match_score": game.match_score,
            "is_exact_match": game.is_exact_match,
            "price": game.price,
            "discount": game.discount,
            "positive_reviews": game.positive_reviews,
            "negative_reviews": game.negative_reviews,
            "review_score": game.review_score,
            "review_score_desc": game.review_score_desc,
            "released": game.released,
            "top_tags": "; ".join(game.top_tags),
            "genres": "; ".join(game.genres),
            "developer": game.developer,
            "publisher": game.publisher,
            "description": game.description
        })
    
    # Create DataFrame and save
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    print(f"\nExported {len(games)} games to {filepath}")


def export_json(games: List[SteamGame], filepath: str, stats: Optional[Dict] = None):
    """
    Export games to JSON file.
    
    Args:
        games: List of SteamGame objects
        filepath: Output file path
        stats: Optional processing statistics
    """
    import json
    
    # Convert to dict list
    data = []
    for game in games:
        data.append(game.model_dump())
    
    # Add stats if provided
    output = {
        "games": data,
        "total": len(games)
    }
    
    if stats:
        output["stats"] = stats
    
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nExported {len(games)} games to {filepath}")
