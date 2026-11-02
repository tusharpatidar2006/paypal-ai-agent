"""Nonce store for single-use mandate enforcement."""
import sqlite3
import threading
from pathlib import Path
from typing import Optional


class NonceStore:
    """Thread-safe nonce store to prevent mandate replay attacks."""
    
    def __init__(self, db_path: Path | str = "data/nonces.db"):
        """Initialize nonce store.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS nonces (
                    mandate_id TEXT PRIMARY KEY,
                    nonce TEXT NOT NULL,
                    used_at REAL NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_used_at ON nonces(used_at)
            """)
            conn.commit()
    
    def check_and_mark(self, mandate_id: str, nonce: str) -> bool:
        """Check if nonce is unused and mark as used atomically.
        
        Args:
            mandate_id: Mandate identifier
            nonce: Nonce value
            
        Returns:
            True if nonce was unused (and is now marked), False if already used
        """
        import time
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # Check if exists
                cursor = conn.execute(
                    "SELECT nonce FROM nonces WHERE mandate_id = ?",
                    (mandate_id,),
                )
                row = cursor.fetchone()
                
                if row is not None:
                    # Already used
                    return False
                
                # Mark as used
                conn.execute(
                    "INSERT INTO nonces (mandate_id, nonce, used_at) VALUES (?, ?, ?)",
                    (mandate_id, nonce, time.time()),
                )
                conn.commit()
                return True
    
    def cleanup_old(self, older_than_seconds: float = 86400) -> int:
        """Remove nonces older than specified time.
        
        Args:
            older_than_seconds: Remove nonces older than this many seconds
            
        Returns:
            Number of nonces removed
        """
        import time
        
        cutoff = time.time() - older_than_seconds
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM nonces WHERE used_at < ?",
                    (cutoff,),
                )
                conn.commit()
                return cursor.rowcount
