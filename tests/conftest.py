"""Pytest fixtures and configuration."""
import pytest
import json
from pathlib import Path


@pytest.fixture
def sample_csv_path():
    """Path to sample CSV file."""
    return Path(__file__).parent / "fixtures" / "sample_games.csv"


@pytest.fixture
def mocked_responses():
    """Load mocked API responses."""
    with open(Path(__file__).parent / "fixtures" / "mocked_responses.json") as f:
        return json.load(f)


@pytest.fixture
def sample_titles():
    """Sample game titles from CSV."""
    return [
        "The Witcher 3: Wild Hunt",
        "Stardew Valley",
        "Dark Souls III",
        "Portal 2",
        "Hollow Knight"
    ]
