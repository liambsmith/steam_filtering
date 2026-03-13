"""Configuration settings for Steam Filter."""
from pathlib import Path

# API settings
STEAM_COUNTRY = "US"
STEAM_LANGUAGE = "english"
STEAM_CC = "us"

# Cache settings
CACHE_DIR = Path.home() / ".steam_filtering"
CACHE_DB = Path(__file__).parent / "steam_cache.db"

# Processing settings
BATCH_SIZE = 10
BATCH_DELAY = 2  # seconds

# Output settings
DEFAULT_OUTPUT = "filtered_games.csv"

# Logging
VERBOSE = False
