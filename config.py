"""Configuration settings for Steam Filter."""
from pathlib import Path
import os

# API settings
STEAM_COUNTRY = "US"
STEAM_LANGUAGE = "english"
STEAM_CC = "us"

# Load Steam API key from file if it exists
STEAM_API_KEY = None
api_key_path = Path(__file__).parent / "STEAM_API_KEY"
if api_key_path.exists():
    try:
        with open(api_key_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    STEAM_API_KEY = line.split("=")[1].strip()
                    break
    except:
        pass

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
