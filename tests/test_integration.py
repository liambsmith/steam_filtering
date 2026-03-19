"""Integration tests for the full workflow."""
import pytest
import pandas as pd
import json
import tempfile
from pathlib import Path
from matcher import match_games
from output import export_csv, export_json
from models import SteamGame


class TestFullWorkflow:
    """Integration tests for complete workflow."""
    
    def test_match_from_mocked_api(self, mocked_responses):
        """Test matching games from mocked API responses."""
        for query, data in mocked_responses["search"].items():
            results = data["items"]
            # Should find at least one match
            game = match_games(results, query)
            # Games should match (either exact, subset, or fuzzy)
            assert game.appid > 0
    
    def test_csv_parsing(self, sample_csv_path):
        """Test CSV file parsing."""
        df = pd.read_csv(sample_csv_path)
        assert len(df) == 5
        assert "title" in df.columns
        assert df["title"].iloc[0] == "The Witcher 3: Wild Hunt"
    
    def test_game_model_validation(self):
        """Test that SteamGame model validates correctly."""
        game = SteamGame(
            original_title="Test Game",
            steam_title="Test Game",
            appid=12345,
            url="https://store.steampowered.com/app/12345/",
            match_score=95.0,
            is_exact_match=True,
            price=19.99,
            discount=0,
            review_score=90,
            review_score_desc="Very Positive",
            released="Jan 1, 2020",
            top_tags=["Action", "Adventure"],
            genres=["Action"],
            developer="Test Dev",
            publisher="Test Pub"
        )
        assert game.appid == 12345
        assert game.match_score == 95.0
    
    def test_game_model_invalid_rating(self):
        """Test that model rejects invalid rating."""
        with pytest.raises(ValueError):
            SteamGame(
                original_title="Test",
                steam_title="Test",
                appid=123,
                url="http://test.com",
                match_score=95.0,
                is_exact_match=False,
                review_score=150  # Invalid: > 100
            )


class TestExportFunctions:
    """Tests for export functionality."""
    
    def test_export_csv(self):
        """Test CSV export."""
        games = [
            SteamGame(
                original_title="Test 1",
                steam_title="Test Game 1",
                appid=111,
                url="http://test.com/1",
                match_score=95.0,
                is_exact_match=True
            ),
            SteamGame(
                original_title="Test 2",
                steam_title="Test Game 2",
                appid=222,
                url="http://test.com/2",
                match_score=85.0,
                is_exact_match=False
            )
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            export_csv(games, temp_path)
            
            # Verify file was created
            assert Path(temp_path).exists()
            
            # Verify content
            df = pd.read_csv(temp_path)
            assert len(df) == 2
            assert "original_title" in df.columns
            assert "steam_title" in df.columns
            assert "appid" in df.columns
        finally:
            # Cleanup
            if Path(temp_path).exists():
                Path(temp_path).unlink()
    
    def test_export_json(self):
        """Test JSON export."""
        games = [
            SteamGame(
                original_title="Test",
                steam_title="Test Game",
                appid=123,
                url="http://test.com",
                match_score=95.0,
                is_exact_match=True
            )
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            export_json(games, temp_path, {"total": 1})
            
            # Verify file was created
            assert Path(temp_path).exists()
            
            # Verify content
            with open(temp_path) as f:
                data = json.load(f)
            
            assert "games" in data
            assert len(data["games"]) == 1
            assert data["games"][0]["appid"] == 123
            assert "stats" in data
        finally:
            # Cleanup
            if Path(temp_path).exists():
                Path(temp_path).unlink()
