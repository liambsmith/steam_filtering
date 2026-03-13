"""Tests for caching functionality."""
import pytest
import sqlite3
from pathlib import Path
from cache import init_db, get_cache, set_cache, clear_cache, _hash_query


@pytest.fixture
def test_db():
    """Create a test database."""
    # Use a test database path
    test_path = Path(__file__).parent / "fixtures" / "test_cache.db"
    
    # Temporarily change the cache path
    import cache
    original_path = cache.CACHE_DB
    cache.CACHE_DB = test_path
    
    init_db()
    yield test_path
    
    # Cleanup
    cache.CACHE_DB = original_path
    if test_path.exists():
        test_path.unlink()


class TestInitDB:
    """Tests for database initialization."""
    
    def test_db_created(self, test_db):
        """Test that database is created."""
        assert test_db.exists()
    
    def test_tables_created(self, test_db):
        """Test that required tables exist."""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Check search_cache table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='search_cache'")
        assert cursor.fetchone() is not None
        
        # Check game_cache table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='game_cache'")
        assert cursor.fetchone() is not None
        
        conn.close()


class TestCacheOperations:
    """Tests for cache get/set operations."""
    
    def test_set_and_get_search(self, test_db):
        """Test setting and getting search cache."""
        test_data = {"appid": 123, "name": "Test Game"}
        set_cache('search', 'test query', test_data)
        result = get_cache('search', 'test query')
        assert result == test_data
    
    def test_set_and_get_game(self, test_db):
        """Test setting and getting game cache."""
        test_data = {"name": "Test Game", "price": 1999}
        set_cache('game', '12345', test_data)
        result = get_cache('game', '12345')
        assert result == test_data
    
    def test_cache_miss(self, test_db):
        """Test that cache miss returns None."""
        result = get_cache('search', 'nonexistent query')
        assert result is None
    
    def test_different_keys_different_results(self, test_db):
        """Test that different keys return different results."""
        set_cache('search', 'query 1', {"value": 1})
        set_cache('search', 'query 2', {"value": 2})
        
        assert get_cache('search', 'query 1') == {"value": 1}
        assert get_cache('search', 'query 2') == {"value": 2}


class TestHashing:
    """Tests for cache key hashing."""
    
    def test_same_query_same_hash(self):
        """Test that same query produces same hash."""
        hash1 = _hash_query("test query")
        hash2 = _hash_query("test query")
        assert hash1 == hash2
    
    def test_different_query_different_hash(self):
        """Test that different queries produce different hashes."""
        hash1 = _hash_query("query 1")
        hash2 = _hash_query("query 2")
        assert hash1 != hash2
    
    def test_hash_consistency(self):
        """Test that hash is consistent across calls."""
        for _ in range(10):
            assert _hash_query("consistent test") == _hash_query("consistent test")
