# Steam Filter

A CLI tool to help you sort through unredeemed Steam game keys from a CSV file and enrich them with Steam metadata (ratings, tags, reviews, etc.).

## Features

- Import game titles from CSV file
- Match titles to Steam games (exact + fuzzy matching)
- Enrich with Steam metadata (ratings, tags, genres, release date)
- Filter by review rating and tags
- Sort by various criteria
- Export filtered results to CSV
- SQLite caching for faster repeated lookups

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd steam_filtering
```

2. Create virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Process a CSV file with game titles
python main.py games.csv

# Export results to CSV
python main.py games.csv -o filtered_games.csv
```

### With Filters

```bash
# Filter by minimum rating (0-100)
python main.py games.csv --min-rating 80

# Filter by tags (partial match, comma-separated)
python main.py games.csv --tags "rpg,adventure"

# Sort by rating (descending)
python main.py games.csv --sort-by rating --sort-order desc

# Combine filters
python main.py games.csv --min-rating 80 --tags "rpg,strategy" --sort-by rating
```

### CSV Format

Your CSV file should have a header row with game titles. The tool will auto-detect the title column.

**Example (games.csv):**
```csv
title
The Witcher 3: Wild Hunt
Stardew Valley
Dark Souls III
Portal 2
Hollow Knight
```

Or with different column names:
```csv
game_name
The Witcher 3
Stardew Valley
```

### Output

The tool will display a formatted table:

```
========================================================================================================================
ORIGINAL TITLE               STEAM TITLE                     RATING       MATCH      TAGS
========================================================================================================================
The Witcher 3: Wild Hunt     The Witcher 3: Wild Hunt        97%          ✓ Exact    RPG, Open World, Story Rich (+2)
Stardew Valley               Stardew Valley                  98%          ✓ Exact    Farming Sim, Relaxing, Pixel Graphics (+5)
Dark Souls III               DARK SOULS III                  90%          ✓ Exact    Dark Fantasy, Challenging, Souls-like (+8)
Portal 2                     Portal 2                        98%          ✓ Exact    Puzzle, Co-op, Sci-fi (+4)
Hollow Knight                Hollow Knight                   97%          ✓ Exact    Metroidvania, Dark Fantasy, Platformer (+3)
========================================================================================================================

Summary: 5 games processed (5 exact match, 0 unmatched)
```

### Command Line Options

```
steam-filter CSV_FILE [OPTIONS]

Arguments:
  CSV_FILE              Path to CSV file with game titles

Options:
  -o, --output FILE     Output CSV file path
  --min-rating INTEGER  Minimum review rating (0-100)
  --tags TEXT           Filter by tags (comma-separated, partial match)
  --sort-by TEXT        Sort by field (rating, match_score, released)
  --sort-order TEXT     Sort order (asc, desc) [default: desc]
  -v, --verbose         Show verbose output
  --clear-cache         Clear cache before processing
  --help                Show this message and exit.
```

## How It Works

1. **Title Matching**:
   - First attempts exact match (case-insensitive)
   - Falls back to fuzzy matching using RapidFuzz (weighted ratio)
   - Scores: ≥95% = exact, 85-94% = fuzzy, 60-84% = low confidence, <60% = unmatched

2. **Steam API Integration**:
   - Uses Steam Store Search API to find games by title
   - Fetches game details (tags, reviews, release date, etc.)
   - Rate limit: 100k requests/day

3. **Caching**:
   - SQLite database (`steam_cache.db`) stores API responses
   - Search results cached for 30 days
   - Game details cached for 7 days
   - Improves performance for repeated runs

4. **Filtering**:
   - Review rating filter (minimum positive %)
   - Tag filter (exact or partial match)
   - Sort by rating, match score, or release date

## Project Structure

```
steam_filtering/
├── main.py              # CLI entry point
├── cli.py               # Typer commands
├── steam_api.py         # Steam Web API client
├── matcher.py           # Title matching (exact + fuzzy)
├── cache.py             # SQLite caching
├── models.py            # Pydantic data models
├── output.py            # Export handlers
├── config.py            # Configuration
├── requirements.txt
├── .gitignore
├── README.md
└── tests/
    ├── conftest.py      # Test fixtures
    ├── test_matcher.py  # Matching tests
    ├── test_cache.py    # Cache tests
    └── test_integration.py  # Integration tests
```

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

## Future Enhancements

- [ ] Batch processing with progress bars
- [ ] Interactive TUI mode
- [ ] Steam library integration (import owned games)
- [ ] Recommendation engine based on tags/ratings
- [ ] Price filtering (for new purchases)
- [ ] Checkpoint/resume for large CSVs
- [ ] Export to Excel/JSON

## License

MIT License

## Credits

- Steam Web API by Valve Corporation
- RapidFuzz for fuzzy string matching
- Typer for CLI framework
- Pydantic for data validation
