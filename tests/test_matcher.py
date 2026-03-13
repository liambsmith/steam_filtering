"""Tests for title matching functionality."""
import pytest
from matcher import clean_title, exact_match, fuzzy_match, match_games


class TestCleanTitle:
    """Tests for title cleaning."""
    
    def test_basic_cleaning(self):
        """Test basic whitespace and case cleaning."""
        assert clean_title("  THE WITCHER 3  ") == "the witcher 3"
    
    def test_preserves_the_prefix(self):
        """Test that 'the' prefix is preserved."""
        assert clean_title("The Witcher 3") == "the witcher 3"
    
    def test_preserves_a_prefix(self):
        """Test that 'a' prefix is preserved."""
        assert clean_title("A Plague Tale") == "a plague tale"
    
    def test_no_prefix_to_remove(self):
        """Test title without prefix."""
        assert clean_title("Stardew Valley") == "stardew valley"


class TestExactMatch:
    """Tests for exact matching."""
    
    def test_exact_match_found(self):
        """Test that exact match is found."""
        steam_results = [
            {"name": "The Witcher 3: Wild Hunt", "appid": 292030},
            {"name": "Stardew Valley", "appid": 413150}
        ]
        result = exact_match(steam_results, "The Witcher 3")
        assert result is not None
        assert result["name"] == "The Witcher 3: Wild Hunt"
    
    def test_exact_match_case_insensitive(self):
        """Test case-insensitive matching."""
        steam_results = [
            {"name": "Portal 2", "appid": 620}
        ]
        result = exact_match(steam_results, "PORTAL 2")
        assert result is not None
    
    def test_exact_match_not_found(self):
        """Test when no exact match exists."""
        steam_results = [
            {"name": "The Witcher 3", "appid": 292030}
        ]
        result = exact_match(steam_results, "Dark Souls 3")
        assert result is None


class TestFuzzyMatch:
    """Tests for fuzzy matching."""
    
    def test_high_confidence_match(self, mocked_responses):
        """Test fuzzy match with high confidence."""
        results = mocked_responses["search"]["the witcher 3"]["items"]
        matches = fuzzy_match(results, "Witcher 3")
        assert len(matches) > 0
        assert matches[0]["score"] >= 80
    
    def test_low_confidence_match(self, mocked_responses):
        """Test fuzzy match with low confidence."""
        results = mocked_responses["search"]["the witcher 3"]["items"]
        matches = fuzzy_match(results, "SomeRandomGame123")
        # Should have no matches above threshold
        assert all(m["score"] < 60 for m in matches) or len(matches) == 0
    
    def test_fuzzy_match_threshold(self):
        """Test that threshold filters matches correctly."""
        steam_results = [
            {"name": "The Witcher 3: Wild Hunt", "appid": 292030},
            {"name": "Some Other Game", "appid": 123}
        ]
        # With high threshold, should get matches above threshold
        matches = fuzzy_match(steam_results, "Witcher 3", threshold=70)
        assert len(matches) >= 1


class TestMatchGames:
    """Tests for the main match_games function."""
    
    def test_match_exact_game(self, mocked_responses):
        """Test matching an exact game."""
        results = mocked_responses["search"]["the witcher 3"]["items"]
        game = match_games(results, "The Witcher 3: Wild Hunt")
        assert game.appid == 292030
        assert game.match_score >= 95
        assert game.is_exact_match == True
    
    def test_match_with_typo(self, mocked_responses):
        """Test matching with a typo."""
        results = mocked_responses["search"]["stardew valley"]["items"]
        game = match_games(results, "Stardew Vallay")
        assert game.appid == 413150
        assert game.match_score >= 75
    
    def test_match_no_result(self):
        """Test matching when no results exist."""
        game = match_games([], "NonExistentGame")
        assert game.appid == 0
        assert game.match_score == 0
