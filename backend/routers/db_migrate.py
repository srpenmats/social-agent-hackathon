"""
Add missing columns to discovered_videos table for engagement metrics.
"""

from fastapi import APIRouter, HTTPException
from db.connection import get_supabase_admin, is_postgres_mode
import psycopg2

router = APIRouter(prefix="/api/v1/db", tags=["database"])


@router.post("/add-engagement-columns")
async def add_engagement_columns():
    """
    Add comments, shares, views columns to discovered_videos table.
    Safe to run multiple times (uses IF NOT EXISTS).
    """
    
    if not is_postgres_mode():
        return {
            "success": False,
            "message": "Only works with PostgreSQL"
        }
    
    try:
        db = get_supabase_admin()
        conn = db._get_conn()
        cursor = conn.cursor()
        
        # Add columns if they don't exist
        cursor.execute("""
            ALTER TABLE discovered_videos 
            ADD COLUMN IF NOT EXISTS comments INTEGER DEFAULT 0;
            
            ALTER TABLE discovered_videos 
            ADD COLUMN IF NOT EXISTS shares INTEGER DEFAULT 0;
            
            ALTER TABLE discovered_videos 
            ADD COLUMN IF NOT EXISTS views INTEGER DEFAULT 0;
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Added comments, shares, views columns to discovered_videos",
            "columns_added": ["comments", "shares", "views"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add columns"
        }
