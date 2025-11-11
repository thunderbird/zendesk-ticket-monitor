"""Data persistence."""

import sqlite3
from pathlib import Path
from datetime import datetime


class SQLiteBackend:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS buckets (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    count INTEGER NOT NULL
                )
            """)
    
    def save_bucket(self, timestamp, count, metadata):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO buckets (timestamp, count) VALUES (?, ?)",
                (timestamp.isoformat(), count)
            )
    
    def load_history(self, hours=168):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT timestamp, count FROM buckets ORDER BY timestamp DESC LIMIT 2000"
            )
            return [{"timestamp": row[0], "count": row[1]} for row in cursor]
