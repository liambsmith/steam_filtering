# Steam API Research Report

**Date:** March 2026  
**Purpose:** Comprehensive guide to Steam APIs for game matching tool

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Official Steam Web API](#official-steam-web-api)
3. [Steam Store Search API](#steam-store-search-api)
4. [Alternative APIs](#alternative-apis)
5. [Game Lookup Strategies](#game-lookup-strategies)
6. [Data Available](#data-available)
7. [Recommendations](#recommendations)
8. [Sample Code](#sample-code)

---

## Executive Summary

This report provides a detailed analysis of Steam APIs for building a game matching tool that matches CSV game titles to Steam games.

### Key Findings

| API | Cost | Rate Limit | Best For |
|-----|------|------------|----------|
| ISteamStore/searchAllApps | Free | 100k/hour | Game search by name |
| ISteamStore/appdetails | Free | 100k/hour | Game details |
| store.steampowered.com/storesearch | Free | 200/5min | Store-specific search |
| SteamApis | Free tier | Varies | Alternative when official APIs fail |
| Apify | Paid | Varies | Large-scale scraping |

**Recommended Approach:** Use storefront API with caching and fuzzy matching

**Note:** This project uses `store.steampowered.com/api/storesearch/` as the primary API because:
- No API key required
- Works reliably for game search
- Adequate for personal tool usage
- Official Web API endpoints often require API keys

For more details on API usage terms, see [STEAM_API_TERMS.md](STEAM_API_TERMS.md).

---

## API Terms of Use Summary

### Rate Limits
- **Store API:** ~200 requests/5 minutes
- **Web API:** 100,000 calls/day (requires API key)

### Key Requirements
1. **No Marketing Use:** Cannot use API for unsolicited marketing
2. **API Key Confidentiality:** If using API key, must keep confidential
3. **Privacy Policy:** Required if storing user data
4. **"As Is" Terms:** No warranties provided by Valve
5. **Attribution:** Should include Steam/Valve attribution
6. **Jurisdiction:** Washington State, USA

### What This Means for Steam Filter
- ✅ Personal use is fine (no privacy policy needed)
- ✅ Caching implemented to minimize API calls
- ✅ Will add Steam attribution in output
- ✅ Accept "as is" data terms

See [STEAM_API_TERMS.md](STEAM_API_TERMS.md) for full details.

---

## Official Steam Web API

### 1.1 Available Endpoints for Searching Games

| Interface | Endpoint | Purpose | Requires API Key |
|-----------|----------|---------|------------------|
| ISteamApps | `ISteamApps/GetAppList/v0002/` | Get list of all Steam apps | Yes |
| ISteamApps | `ISteamApps/GetAppList/v2/` | Get list of all Steam apps | Yes |
| ISteamStore | `ISteamStore/searchAllApps/v1/` | Search all apps by name | No |
| ISteamStore | `ISteamStore/getAllDeals/v1/` | Get all deals | No |
| ISteamStore | `ISteamStore/getRecommendations/v1/` | Get recommendations | No |

**Search Endpoint:**
```
https://api.steampowered.com/ISteamStore/searchAllApps/v1/?term=your_search_term&country=US&language=en&count=10
```

**Response Example:**
```json
{
  "items": [
    {
      "type": "game",
      "id": 123456,
      "name": "Game Name",
      "discounted": false,
      "discount_percent": 0,
      "original_price": 1999,
      "final_price": 1999,
      "currency": "USD",
      "windows_available": true,
      "mac_available": true,
      "linux_available": false,
      "header_image": "https://..."
    }
  ]
}
```

### 1.2 Endpoints for Getting Game Details

**App Details Endpoint:**
```
https://store.steampowered.com/api/appdetails/?appids=123456&l=en
```

**Response Example:**
```json
{
  "123456": {
    "success": true,
    "data": {
      "type": "game",
      "name": "Game Name",
      "steam_appid": 123456,
      "is_free": false,
      "short_description": "...",
      "developers": ["Developer Name"],
      "publishers": ["Publisher Name"],
      "price_overview": {
        "currency": "USD",
        "initial": 1999,
        "final": 1999,
        "discount_percent": 0
      },
      "platforms": {"windows": true, "mac": true, "linux": false},
      "metacritic": {"score": 85, "url": "..."},
      "categories": [{"id": 2, "description": "Single-player"}],
      "genres": [{"id": "1", "description": "Action"}],
      "release_date": {"coming_soon": false, "date": "Aug 12, 2024"},
      "tags": [
        {"id": 122, "count": 12345, "name": "Action"},
        {"id": 1684, "count": 8901, "name": "Indie"}
      ],
      "review_score": 9,
      "review_score_desc": "Overwhelmingly Positive",
      "total_positive": 45678,
      "total_negative": 1234
    }
  }
}
```

### 1.3 Authentication Requirements

- **API Key Required:** For most ISteamStore and ISteamApps endpoints
- **How to Get:** https://steamcommunity.com/dev/apikey
- **Key is Free:** No cost, unlimited for reasonable use
- **Key Format:** 32-character hexadecimal string

**Important Finding (2026):** Many ISteamStore endpoints require an API key to function. The `searchAllApps` endpoint tested returned 404 without a key.

### 1.4 Rate Limits

| Endpoint | Rate Limit | Notes |
|----------|------------|-------|
| ISteamStore | 100,000 requests/hour | Per IP address (with API key) |
| ISteamApps | 100,000 requests/hour | Per IP address (with API key) |
| Store endpoints | 200 requests/5 minutes | No API key required |

**Important:** The `GetAppList` API was deprecated in November 2025 because "it can no longer scale to the number of items available on Steam."

---

## Steam Store Search API

### 2.1 Available Parameters

```
https://store.steampowered.com/api/storesearch/

Parameters:
- search: string (required) - Search query term
- type: string - Filter by type (game, software, dlc, addon, movie, music)
- count: int - Number of results (default: 10, max: 200)
- start: int - Pagination offset (default: 0)
- country: string - Country code (default: US)
- currency: string - Currency code (default: USD)
- language: string - Language code (default: en)
- price_filter: string - Price filter (maxprice=X, minprice=X)
- discount_filter: string - Discount filter (discount=X)
- cc: string - Country code alias for currency
- l: string - Language alias
- format: string - Response format (json, xml, vdf)
```

### 2.2 Data Returned

**Response Structure:**
```json
{
  "total": 1234,
  "items": [
    {
      "id": 123456,
      "name": "Game Name",
      "type": "game",
      "discounted": true,
      "discount_percent": 50,
      "original_price": 1999,
      "final_price": 999,
      "currency": "USD",
      "windows_available": true,
      "mac_available": true,
      "linux_available": false,
      "header_image": "https://...",
      "released": "Aug 12, 2024"
    }
  ]
}
```

### 2.3 Result Ranking

Results are ranked by:
1. **Relevance** to search term (default)
2. **Popularity** - games with more players/reviews rank higher
3. **Price** - when price filter is applied
4. **Discount** - when discount filter is applied
5. **Release date** - newer games may be prioritized

### 2.4 Filtering and Ordering

**Available Filters:**
- Type: game, software, dlc, addon, movie, music
- Price: `price_filter=maxprice:X` (price in cents)
- Discount: `discount_filter:discount:X` (minimum discount percentage)
- Country: affects pricing and availability
- Language: affects search term interpretation

**Sorting:** No explicit sort parameter, but results are relevance-sorted by default.

---

## Alternative APIs

### 3.1 SteamDB API (api.steamdb.info)

**Status:** ❌ **No official API**

From the SteamDB FAQ:
> "In short, no. We believe if you need to get Steam data, you can get it from Steam directly using their WebAPI or using libraries like SteamKit."

**Key Points:**
- SteamDB does NOT provide an API
- They explicitly state: "Creating a good API is a lot of work and a big vector for abuse which we are not equipped to deal with"
- They encourage developers to use Steam's official APIs
- Scraping SteamDB is **not allowed** without permission
- Free for academic purposes only with prior approval

### 3.2 SteamWebAPI.com

**Status:** ⚠️ **Paid Third-Party Service**

**Pricing (as of 2026):**
- Price increase of 15-30% implemented due to increased operating costs
- Free tier available with limited requests
- Paid tiers start around $10-20/month

**Endpoints:**
- Account management
- Market data
- Inventory data
- Game data

**Pros:**
- Aggregates multiple Steam APIs
- Better documentation
- Rate limit handling

**Cons:**
- Paid service
- Third-party (not official)
- Potential for service changes

### 3.3 Other Alternatives

#### SteamApis (steamapis.com)
- **Free tier available**
- **Pricing:** Free tier with limits, paid tiers for higher usage
- **Endpoints:** Apps, market data, app details
- **Documentation:** https://docs.steamapis.com/

#### Apify Steam Scrapers
- **Pricing:** Pay per usage, starting at $2-3 per 1000 results
- **Examples:**
  - Steam Game Scraper (cloud9_ai)
  - Steam Game Data Scraper (nexgendata)
  - Steam Game Search Scraper (scrapestorm)

---

## Game Lookup Strategies

### 4.1 Best Way to Look Up a Game by Name

**Recommended Approach:**

1. **Use `ISteamStore/searchAllApps/v1/`** for name-based search
2. **Fallback to `store.steampowered.com/api/storesearch/`** if ISteamStore requires authentication
3. **Use exact matching** when possible

**Search Example:**
```python
import requests

def search_steam_games(query, count=20):
    url = "https://api.steampowered.com/ISteamStore/searchAllApps/v1/"
    params = {
        "term": query,
        "country": "US",
        "language": "en",
        "count": count
    }
    response = requests.get(url, params=params)
    return response.json()
```

### 4.2 Getting AppID Directly from Name

**Challenges:**
- Multiple games can have similar names (e.g., "Hades" vs "Hades II")
- Name variations and translations
- DLCs and remasters share parent names

**Solution:** Use a multi-step approach:

```python
async def find_game_by_name(name):
    # Step 1: Search for the game
    search_results = await search_by_name(name)
    
    # Step 2: Filter by type
    games = [item for item in search_results if item['type'] == 'game']
    
    # Step 3: Get detailed info to disambiguate
    for game in games:
        details = await get_app_details(game['id'])
        # Check release date, developer, description for disambiguation
```

### 4.3 Handling Name Variations

**Common Variations:**
- "Hades" vs "Hades II"
- "GTA V" vs "Grand Theft Auto V"
- "CS:GO" vs "Counter-Strike: Global Offensive"
- "RTS" vs "Real-Time Strategy"

**Strategies:**

1. **Fuzzy Matching:**
   ```python
   from rapidfuzz import fuzz
   
   def normalize_name(name):
       return name.lower().replace("[^\\w\\s]", "").strip()
   
   def calculate_similarity(name1, name2):
       return fuzz.WRatio(normalize_name(name1), normalize_name(name2))
   ```

2. **Use AppID Cache:**
   - Maintain a local cache of known AppID to name mappings
   - Update periodically using `GetAppList`

3. **Multiple Search Strategies:**
   ```python
   async def find_game_by_name(name):
       # Try exact match first
       exact = await search_by_name(name)
       if exact.total > 0:
           return exact.items[0]
       
       # Try partial match
       partial = await search_by_name(" ".join(name.split()[:2]))
       if partial.total > 0:
           return partial.items[0]
       
       # Try fuzzy match
       fuzzy = await fuzzy_search(name)
       return fuzzy[0]
   ```

---

## Data Available

### 5.1 Metadata Available

| Field | Endpoint | Availability |
|-------|----------|--------------|
| AppID | All | Always |
| Name | All | Always |
| Type (game, dlc, etc.) | All | Always |
| Price | appdetails, storesearch | Always |
| Discount | appdetails, storesearch | Always |
| Release Date | appdetails | Yes |
| Developer | appdetails | Yes |
| Publisher | appdetails | Yes |
| Genres | appdetails | Yes |
| Categories | appdetails | Yes |
| Description | appdetails | Yes |
| Platforms (Win/Mac/Linux) | All | Yes |
| Header Image | All | Yes |
| Capsule Images | All | Yes |
| Controller Support | All | Yes |
| Metacritic Score | appdetails | Yes (if available) |
| User Reviews | appdetails | Yes (if available) |
| Tags | appdetails | Yes (community tags) |
| System Requirements | appdetails | Yes |
| Supported Languages | appdetails | Yes |
| Age Rating | appdetails | Yes |
| Website | appdetails | Yes |
| Support Info | appdetails | Yes |

### 5.2 User Tags

**Endpoint:** `ISteamStore/appdetails/v1/`

```json
{
  "data": {
    "tags": [
      {"id": 122, "count": 12345, "name": "Action"},
      {"id": 1684, "count": 8901, "name": "Indie"},
      {"id": 1702, "count": 5678, "name": "Adventure"}
    ]
  }
}
```

### 5.3 Reviews

**Endpoint:** `ISteamStore/appdetails/v1/`

```json
{
  "data": {
    "achievements": {"total": 50},
    "review_score": 9,
    "review_score_desc": "Overwhelmingly Positive",
    "total_positive": 45678,
    "total_negative": 1234,
    "total_reviews": 46912
  }
}
```

### 5.4 Genres

```json
{
  "genres": [
    {"id": "1", "description": "Action"},
    {"id": "25", "description": "Adventure"},
    {"id": "23", "description": "Indie"}
  ]
}
```

---

## Recommendations

### 6.1 Recommended API Strategy

**Primary Approach: Hybrid**

```
┌─────────────────────────────────────────────────────────────┐
│                    Game Matching Pipeline                    │
├─────────────────────────────────────────────────────────────┤
│ 1. CSV Game Title                                         │
│    ↓ (normalize)                                           │
│ 2. Check Local Cache (AppID → Name mapping)              │
│    ↓ (if not found)                                        │
│ 3. Search via ISteamStore/searchAllApps                  │
│    ↓ (get AppIDs)                                          │
│ 4. Get Details via ISteamStore/appdetails                │
│    ↓ (verify match)                                        │
│ 5. Return Match with Confidence Score                     │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Implementation Recommendations

**1. Use Official APIs First:**
```python
# Primary search endpoint
SEARCH_ENDPOINT = 'https://api.steampowered.com/ISteamStore/searchAllApps/v1/'

# Details endpoint
DETAILS_ENDPOINT = 'https://store.steampowered.com/api/appdetails/'

# Request example
async def search_steam_games(query, count=20):
    url = f"{SEARCH_ENDPOINT}?term={quote(query)}&country=US&language=en&count={count}"
    response = requests.get(url)
    return response.json()
```

**2. Implement Caching:**
- Cache search results locally (Redis, SQLite, or file-based)
- Cache app details by AppID
- Cache name variations and synonyms

**3. Confidence Scoring:**
```python
def calculate_confidence(csv_name, steam_name, match_type):
    base_score = {
        'exact': 100,
        'normalized': 85,
        'partial': 60,
        'fuzzy': 40
    }.get(match_type, 0)
    
    # Bonus for additional metadata match
    if match_type == 'fuzzy':
        # Check if genres match, etc.
        pass
    
    return base_score
```

### 6.3 API Selection Summary

| API | Cost | Rate Limit | Best For |
|-----|------|------------|----------|
| ISteamStore/searchAllApps | Free | 100k/hour | Game search by name |
| ISteamStore/appdetails | Free | 100k/hour | Game details |
| store.steampowered.com/storesearch | Free | 200/5min | Store-specific search |
| SteamApis | Free tier | Varies | Alternative when official APIs fail |
| Apify | Paid | Varies | Large-scale scraping |

### 6.4 Recommended Approach for CSV Game Title Matching

**Current Approach (Storefront API - No Key Required):**

Use `store.steampowered.com/api/storesearch/` - no API key, works out of the box.

**Why This Works:**
- No authentication required
- Reliable for game search
- Adequate rate limits for personal use
- Properly normalized response format

**Implementation:**
```python
# Primary search endpoint (storefront)
url = "http://store.steampowered.com/api/storesearch/"
params = {
    "term": query,
    "country": "US",
    "language": "english",
    "cc": "us",
    "count": 20
}
```

**Fallback Strategy:**
```
1. Check local cache first
2. Search via store.steampowered.com/search
3. Apply matching logic (exact, normalized, fuzzy)
4. If no match found, mark as unmatched
```

**Handle Edge Cases:**
- Free games (may appear lower in results)
- Games with similar names (use fuzzy matching with high threshold)
- Regional availability differences (set country parameter)
- Name variations (normalize titles before matching)

**Future Enhancement (Optional):**
- Get API key from https://steamcommunity.com/dev/apikey
- Use ISteamStore endpoints for potentially better results
- Higher rate limits (100k/day vs ~200/5min)
- Not required for current use case

**Recommendation:**
- ✅ Continue with storefront API (works well, no key needed)
- ✅ Implement caching to minimize API calls
- ✅ Focus on improving matching logic
- ⚠️ Consider API key only if rate limits become an issue

---

## Sample Code

### 7.1 Basic Steam Game Matcher Class

```python
import requests
from typing import List, Dict, Optional

class SteamGameMatcher:
    def __init__(self):
        self.cache = {}
        self.search_endpoint = 'https://api.steampowered.com/ISteamStore/searchAllApps/v1/'
        self.details_endpoint = 'https://store.steampowered.com/api/appdetails/'
    
    def search(self, query: str, count: int = 20) -> List[Dict]:
        """Search for games by name."""
        params = {
            'term': query,
            'country': 'US',
            'language': 'en',
            'count': count
        }
        response = requests.get(self.search_endpoint, params=params)
        response.raise_for_status()
        return response.json().get('items', [])
    
    def get_details(self, app_id: int) -> Optional[Dict]:
        """Get detailed information about a game."""
        url = f"{self.details_endpoint}?appids={app_id}&l=en"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get(str(app_id), {}).get('data')
    
    def find_match(self, csv_title: str) -> Optional[Dict]:
        """Find the best match for a CSV game title."""
        # Try cache first
        if csv_title in self.cache:
            return self.cache[csv_title]
        
        # Search Steam
        results = self.search(csv_title)
        
        # Find best match
        best_match = self._find_best_match(results, csv_title)
        
        # Cache result
        self.cache[csv_title] = best_match
        
        return best_match
    
    def _find_best_match(self, results: List[Dict], csv_title: str) -> Optional[Dict]:
        """Find the best matching game from search results."""
        csv_lower = csv_title.lower()
        
        for result in results:
            steam_name = result.get('name', '').lower()
            
            # Exact match
            if csv_lower == steam_name:
                return result
            
            # Check if CSV title is substring of Steam name
            if csv_lower in steam_name:
                return result
        
        # No exact match found
        return results[0] if results else None
```

### 7.2 Usage Example

```python
if __name__ == '__main__':
    matcher = SteamGameMatcher()
    
    games = [
        "The Witcher 3: Wild Hunt",
        "Stardew Valley",
        "Hades"
    ]
    
    for game_title in games:
        match = matcher.find_match(game_title)
        if match:
            print(f"{game_title} → {match['name']} (AppID: {match['id']})")
        else:
            print(f"{game_title} → Not found")
```

---

## Appendix

### A. API Key Setup

1. Visit: https://steamcommunity.com/dev/apikey
2. Log in with your Steam account
3. Enter a domain name (can be localhost for development)
4. Agree to the terms
5. Copy your API key

### B. Rate Limit Best Practices

- Implement exponential backoff for failed requests
- Cache responses to reduce API calls
- Batch requests when possible
- Respect rate limits to avoid IP bans

### C. Error Handling

```python
import requests.exceptions

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        print("Rate limit exceeded, waiting...")
    else:
        print(f"HTTP error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

---

**End of Report**
