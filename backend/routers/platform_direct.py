"""
Direct database insert for platform connection.
Bypasses ORM to avoid JSONB issues.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import os

from db.connection import get_supabase_admin, is_postgres_mode

router = APIRouter(prefix="/api/v1/platforms", tags=["platforms-direct"])


@router.post("/direct-connect/twitter")
async def direct_connect_twitter():
    """
    Directly insert Twitter platform connection using raw SQL.
    Bypasses ORM JSONB issues.
    """
    
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        return {
            "success": False,
            "error": "TWITTER_BEARER_TOKEN not set"
        }
    
    if not is_postgres_mode():
        return {
            "success": False,
            "error": "PostgreSQL required"
        }
    
    db = get_supabase_admin()
    conn = db._get_conn()
    cursor = conn.cursor()
    
    try:
        # Check if record exists
        cursor.execute("SELECT id FROM platforms WHERE name = 'x'")
        existing = cursor.fetchone()
        
        now = datetime.now(timezone.utc).isoformat()
        
        if existing:
            # Update existing
            cursor.execute("""
                UPDATE platforms 
                SET status = 'connected',
                    display_name = 'X / Twitter',
                    credentials = '{"has_bearer_token": true, "connection_type": "api_token"}'::jsonb,
                    last_verified = %s
                WHERE name = 'x'
            """, (now,))
            action = "updated"
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO platforms (name, display_name, status, credentials, connected_at, last_verified)
                VALUES ('x', 'X / Twitter', 'connected', 
                        '{"has_bearer_token": true, "connection_type": "api_token"}'::jsonb,
                        %s, %s)
            """, (now, now))
            action = "created"
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "action": action,
            "platform": "x",
            "display_name": "X / Twitter",
            "status": "connected",
            "message": "Twitter platform directly connected"
        }
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {
            "success": False,
            "error": str(e),
            "message": "Direct connection failed"
        }
