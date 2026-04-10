# Steam Filter - Agent Guidelines

## Project Overview
A CLI tool for filtering Steam game keys from CSV files and enriching them with Steam metadata (ratings, tags, reviews).

## Quick Start
```bash
# Activate virtual environment
source venv/bin/activate

# Run the tool
python main.py games.csv

# Run tests
pytest tests/ -v
```

## Build & Test Commands

### Running Tests
```bash
# Run all tests with verbose output
pytest tests/ -v

# Run single test file
pytest tests/test_matcher.py -v

# Run single test function
pytest tests/test_matcher.py::TestCleanTitle::test_basic_cleaning -v

# Run tests with coverage
pytest tests/ --cov=steam_filtering --cov-report=term-missing

# Run specific test class
pytest tests/test_cache.py -v

# Run tests with detailed failure output
pytest tests/ -v --tb=short
```

### Virtual Environment
```bash
# Create venv (first time only)
python -m venv venv

# Activate venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Upgrade dependencies
pip install -r requirements.txt --upgrade
```

## Code Style Guidelines

### Imports
- **Order**: Standard library → third-party → local imports
- **Grouping**: Separate groups with blank lines
- **Style**: Use absolute imports, avoid relative imports

```python
# ✅ Good
from typing import List, Dict, Any, Optional
import re
import requests
from pydantic import BaseModel

from models import SteamGame
from config import STEAM_API_KEY
```

```python
# ❌ Bad
import re
from typing import List
import requests
from models import SteamGame  # mixed with stdlib
```

### Type Hints
- **Always use type hints** for function parameters and return values
- Use `Optional[X]` for nullable types
- Use `List[X]` or `dict[str, Any]` for collections
- Use `Any` sparingly, prefer specific types

```python
# ✅ Good
def search_games(title: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search for games on Steam."""
    ...

def clean_title(title: str) -> str:
    """Clean and normalize a game title."""
    ...
```

```python
# ❌ Bad
def search_games(title, limit=20):  # no type hints
    ...
```

### Naming Conventions
- **Modules**: lowercase with underscores (e.g., `steam_api.py`)
- **Classes**: PascalCase (e.g., `SteamGame`, `SteamAPIError`)
- **Functions**: lowercase with underscores (e.g., `search_games`, `word_match`)
- **Constants**: UPPERCASE with underscores (e.g., `STEAM_API_KEY`, `ROMAN_TO_INT`)
- **Variables**: lowercase with underscores (e.g., `game_title`, `match_score`)

### Docstrings
- **Functions/Classes**: Use Google-style docstrings
- **Required**: description, args (if any), returns
- **Keep concise**: 1-3 sentence summary

```python
def exact_match(steam_results: List[Dict[str, Any]], csv_title: str) -> Optional[Dict[str, Any]]:
    """
    Find exact case-insensitive match in Steam results.
    
    Args:
        steam_results: List of Steam game results
        csv_title: Title from CSV file
    
    Returns:
        Best match dictionary or None
    """
    ...
```

### Error Handling
- **Use custom exceptions** for domain-specific errors
- **Raise descriptive errors** with context
- **Handle API errors** gracefully with retry logic

```python
class SteamAPIError(Exception):
    """Exception raised for Steam API errors."""
    pass

def search_games(title: str, limit: int = 20) -> List[Dict[str, Any]]:
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise SteamAPIError(f"Failed to search Steam API: {e}")
```

### Pydantic Models
- **Use Field()** for field metadata and constraints
- **Use Optional[]** for nullable fields
- **Use default_factory** for mutable defaults (lists, dicts)
- **Add descriptions** for better documentation

```python
class SteamGame(BaseModel):
    match_score: float = Field(..., ge=0, le=100, description="Match confidence 0-100")
    top_tags: List[str] = Field(default_factory=list, description="Top user tags")
    price: Optional[float] = Field(default=None, description="Price in USD")
```

### Testing
- **Use pytest** for all tests
- **Name tests** clearly: `test_<function>_<scenario>`
- **Group tests** in classes by module/functionality
- **Use fixtures** for shared test data
- **Mock external APIs** using pytest-mock

```python
class TestExactMatch:
    def test_exact_match_found(self):
        steam_results = [{"name": "The Witcher 3", "appid": 292030}]
        result = exact_match(steam_results, "The Witcher 3")
        assert result is not None
        assert result["name"] == "The Witcher 3"
```

### Code Organization
- **One class/function per file** when possible
- **Group related functions** in modules
- **Keep files under 300 lines** when possible
- **Use helper functions** to avoid code duplication

### Configuration
- **Load config from environment** or config files
- **Never hardcode secrets** - use `STEAM_API_KEY` file
- **Provide defaults** for all configuration values

```python
# config.py
STEAM_API_KEY = None
api_key_path = Path(__file__).parent / "STEAM_API_KEY"
if api_key_path.exists():
    with open(api_key_path) as f:
        STEAM_API_KEY = f.read().strip()
```

### Git & Version Control
- **Commit often** with descriptive messages
- **Use feature branches** for new functionality
- **Run tests** before committing
- **Add .gitignore** for venv, cache files, secrets

### Dependencies
- **Pin versions** in requirements.txt
- **Use minimal versions** (>=) for stability
- **Keep dependencies minimal** - avoid unnecessary packages
- **Document** why each dependency is needed

## Common Patterns

### API Calls
```python
def search_games(title: str, limit: int = 20) -> List[Dict[str, Any]]:
    url = "http://store.steampowered.com/api/storesearch/"
    params = {"term": title, "country": "US", "language": "english", "count": limit}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise SteamAPIError(f"Failed to search Steam API: {e}")
```

### Caching
```python
def get_cache(key_type: str, key: str) -> Optional[Dict[str, Any]]:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT results FROM cache WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None
```

### Fuzzy Matching
```python
from rapidfuzz import fuzz, process

matches = process.extract(
    cleaned_csv,
    titles,
    scorer=fuzz.WRatio,
    limit=10
)
```

## Known Issues & Workarounds

1. **Exact matching only**: CSV titles should be full game names for best results
2. **Subset matching**: Handles "Dark Souls III" → "Dark Souls III Deluxe Edition"
3. **API rate limits**: Implemented SQLite caching (30-day TTL for search results)
4. **Fuzzy fallback**: First result from Steam API used when no exact/subset match

## References
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [RapidFuzz Documentation](https://rapidfuzz.github.io/RapidFuzz/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Steam API Terms](https://steamcommunity.com/dev/apiterms)
