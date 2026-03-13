"""SQLite caching for Steam API responses."""
import sqlite3
import hashlib
import json
from pathlib import Path
from typing import Any, Optional, Dict
from config import CACHE_DB


def _get_connection() -> sqlite3.Connection:
    """Get database connection."""
    conn = sqlite3.connect(CACHE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the cache database."""
    conn = _get_connection()
    cursor = conn.cursor()
    
    # Search cache table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_cache (
            query_hash TEXT PRIMARY KEY,
            query TEXT NOT NULL,
            results TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Game details cache table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_cache (
            appid INTEGER PRIMARY KEY,
            details TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def _hash_query(query: str) -> str:
    """Create hash for cache key."""
    return hashlib.sha256(query.encode('utf-8')).hexdigest()


def get_cache(key_type: str, key: str) -> Optional[Dict[str, Any]]:
    """
    Get cached result.
    
    Args:
        key_type: 'search' or 'game'
        key: Query string or appid
    
    Returns:
        Cached result or None
    """
    conn = _get_connection()
    cursor = conn.cursor()
    
    if key_type == 'search':
        query_hash = _hash_query(key)
        cursor.execute(
            "SELECT results FROM search_cache WHERE query_hash = ?",
            (query_hash,)
        )
    elif key_type == 'game':
        cursor.execute(
            "SELECT details FROM game_cache WHERE appid = ?",
            (key,)
        )
    else:
        conn.close()
        return None
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row[0])
    return None


def set_cache(key_type: str, key: str, data: Dict[str, Any]):
    """
    Store result in cache.
    
    Args:
        key_type: 'search' or 'game'
        key: Query string or appid
        data: Data to cache
    """
    conn = _get_connection()
    cursor = conn.cursor()
    
    if key_type == 'search':
        query_hash = _hash_query(key)
        cursor.execute("""
            INSERT OR REPLACE INTO search_cache (query_hash, query, results)
            VALUES (?, ?, ?)
        """, (query_hash, key, json.dumps(data)))
    elif key_type == 'game':
        cursor.execute("""
            INSERT OR REPLACE INTO game_cache (appid, details)
            VALUES (?, ?)
        """, (key, json.dumps(data)))
    
    conn.commit()
    conn.close()


def clear_cache():
    """Clear all cache."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM search_cache")
    cursor.execute("DELETE FROM game_cache")
    conn.commit()
    conn.close()
