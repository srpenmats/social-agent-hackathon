#!/usr/bin/env python3
"""Add tables for live discovery."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "backend" / "db" / "local.db"

def add_discovery_tables():
    """Add discovery_jobs and discovered_posts tables."""
    print(f"📁 Opening database: {DB_PATH}")
    
    conn = sqlite3.connect(str(DB_PATH))
    
    print("🔧 Adding discovery tables...")
    
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS discovery_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            max_results INTEGER DEFAULT 20,
            status TEXT DEFAULT 'pending',
            posts_found INTEGER DEFAULT 0,
            error_message TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            completed_at TEXT
        );
        
        CREATE TABLE IF NOT EXISTS discovered_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            post_id TEXT UNIQUE NOT NULL,
            post_url TEXT,
            post_text TEXT,
            author_username TEXT,
            author_name TEXT,
            likes INTEGER DEFAULT 0,
            retweets INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            status TEXT DEFAULT 'discovered',
            discovered_at TEXT DEFAULT (datetime('now')),
            job_id INTEGER REFERENCES discovery_jobs(id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_discovered_posts_status 
        ON discovered_posts(status);
        
        CREATE INDEX IF NOT EXISTS idx_discovered_posts_job 
        ON discovered_posts(job_id);
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Tables created successfully!")
    print("\nTables added:")
    print("  - discovery_jobs (tracks discovery runs)")
    print("  - discovered_posts (stores found tweets)")


if __name__ == "__main__":
    add_discovery_tables()
