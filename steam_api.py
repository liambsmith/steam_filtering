"""Steam Web API client."""
import requests
from typing import List, Dict, Any, Optional
from config import STEAM_COUNTRY, STEAM_LANGUAGE, STEAM_CC, STEAM_API_KEY


class SteamAPIError(Exception):
    """Exception raised for Steam API errors."""
    pass


def search_games(title: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search for games on Steam by title using ISteamStore API with fallback to store API.
    
    Args:
        title: Game title to search for
        limit: Maximum number of results (default 20)
    
    Returns:
        List of game dictionaries with appid, name, price, etc.
    
    Raises:
        SteamAPIError: If the API request fails
    """
    # Try ISteamStore API first (with API key if available)
    if STEAM_API_KEY:
        try:
            url = "https://api.steampowered.com/ISteamStore/searchAllApps/v1/"
            params = {
                "term": title,
                "country": STEAM_COUNTRY,
                "language": STEAM_LANGUAGE,
                "count": limit,
                "key": STEAM_API_KEY
            }
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("response"):
                return _normalize_search_results(data.get("response", []))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [401, 403]:
                # API key invalid or unauthorized, fall through to store API
                pass
            elif e.response.status_code == 404:
                # Endpoint not found, fall through to store API
                pass
            else:
                raise
    
    # Fallback to store.steampowered.com API
    return _search_with_store_api(title, limit)


def _normalize_search_results(items: List[Dict]) -> List[Dict[str, Any]]:
    """Normalize ISteamStore API response to our expected format."""
    results = []
    for item in items:
        # Extract metascore (may be string or int)
        metascore = item.get("metascore", 0)
        if isinstance(metascore, str):
            try:
                metascore = int(metascore)
            except (ValueError, TypeError):
                metascore = 0
        
        # Extract price data
        price_data = item.get("price", {})
        if not price_data:
            price_data = {
                "initial": item.get("original_price", 0),
                "final": item.get("final_price", 0),
                "discount_percent": item.get("discount_percent", 0)
            }
        
        results.append({
            "appid": item.get("id", 0),
            "name": item.get("name", ""),
            "price_overview": {
                "initial": price_data.get("initial", 0),
                "final": price_data.get("final", 0),
                "discount_percent": price_data.get("discount_percent", 0)
            },
            "metascore": metascore,
            "platforms": {
                "windows": item.get("windows_available", False),
                "mac": item.get("mac_available", False),
                "linux": item.get("linux_available", False)
            },
            "review_score": metascore,
            "review_score_desc": "Very Positive" if metascore > 80 else "Mixed"
        })
    return results


def _search_with_store_api(title: str, limit: int) -> List[Dict[str, Any]]:
    """Fallback search using store.steampowered.com API."""
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
        data = response.json()
        
        # Normalize response to expected format
        results = []
        for item in data.get("items", []):
            metascore = item.get("metascore", 0)
            if isinstance(metascore, str):
                try:
                    metascore = int(metascore)
                except (ValueError, TypeError):
                    metascore = 0
            
            price_data = item.get("price", {})
            if not price_data:
                price_data = {
                    "initial": item.get("original_price", 0),
                    "final": item.get("final_price", 0),
                    "discount_percent": item.get("discount_percent", 0)
                }
            
            results.append({
                "appid": item.get("id", 0),
                "name": item.get("name", ""),
                "price_overview": {
                    "initial": price_data.get("initial", 0),
                    "final": price_data.get("final", 0),
                    "discount_percent": price_data.get("discount_percent", 0)
                },
                "metascore": metascore,
                "platforms": {
                    "windows": item.get("windows_available", False),
                    "mac": item.get("mac_available", False),
                    "linux": item.get("linux_available", False)
                },
                "review_score": metascore,
                "review_score_desc": "Very Positive" if metascore > 80 else "Mixed"
            })
        return results
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
