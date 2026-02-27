"""Database initialization endpoint."""

from fastapi import APIRouter
import sqlite3
from pathlib import Path

router = APIRouter(prefix="/api/v1/db", tags=["database"])

@router.post("/init-discovery-tables")
async def init_discovery_tables():
    """Initialize discovery tables in the database."""
    try:
        db_path = Path(__file__).parent.parent / "db" / "local.db"
        conn = sqlite3.connect(str(db_path))
        
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
        
        return {
            "success": True,
            "message": "Discovery tables created successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
