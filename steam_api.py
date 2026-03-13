"""Steam Web API client."""
import requests
from typing import List, Dict, Any, Optional
from config import STEAM_COUNTRY, STEAM_LANGUAGE, STEAM_CC


class SteamAPIError(Exception):
    """Exception raised for Steam API errors."""
    pass


def search_games(title: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search for games on Steam by title.
    
    Args:
        title: Game title to search for
        limit: Maximum number of results (default 20)
    
    Returns:
        List of game dictionaries with appid, name, price, discount, etc.
    
    Raises:
        SteamAPIError: If the API request fails
    """
    url = "http://store.steampowered.com/api/storesearch/"
    params = {
        "term": title,
        "country": STEAM_COUNTRY,
        "language": STEAM_LANGUAGE,
        "cc": STEAM_CC,
        "count": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("items", [])
    except requests.exceptions.RequestException as e:
        raise SteamAPIError(f"Failed to search Steam API: {e}")


def get_game_details(appid: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a Steam game.
    
    Args:
        appid: Steam AppID
    
    Returns:
        Dictionary with game details or None if not found
    
    Raises:
        SteamAPIError: If the API request fails
    """
    url = "http://store.steampowered.com/api/appdetails"
    params = {
        "appids": appid,
        "cc": STEAM_CC,
        "l": STEAM_LANGUAGE
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if str(appid) not in result:
            return None
        
        app_data = result[str(appid)]
        
        if not app_data.get("success"):
            return None
        
        return app_data.get("data", {})
    except requests.exceptions.RequestException as e:
        raise SteamAPIError(f"Failed to get game details for AppID {appid}: {e}")


def get_game_reviews(appid: int) -> Optional[Dict[str, Any]]:
    """
    Get review summary for a Steam game.
    
    Args:
        appid: Steam AppID
    
    Returns:
        Dictionary with review information or None if not found
    """
    details = get_game_details(appid)
    if not details:
        return None
    
    # Try to get review info from details
    reviews = details.get("reviews", {})
    if reviews and isinstance(reviews, str):
        try:
            reviews = __import__('json').loads(reviews)
        except:
            pass
    
    return {
        "positive": reviews.get("total_positive", 0) if isinstance(reviews, dict) else 0,
        "negative": reviews.get("total_negative", 0) if isinstance(reviews, dict) else 0,
        "summary": reviews.get("summary", "") if isinstance(reviews, dict) else ""
    }
