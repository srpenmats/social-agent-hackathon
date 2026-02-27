"""
Migration runner endpoint - executes SQL migrations
"""
from fastapi import APIRouter, HTTPException
from db.connection import get_supabase_admin, is_postgres_mode

router = APIRouter(prefix="/api/v1/migrations", tags=["migrations"])


@router.post("/run")
async def run_migrations():
    """
    Run all pending migrations for review_posts table.
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
        
        results = []
        
        # Migration 005: Create review_posts table
        results.append("Running 005_create_review_posts.sql...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_posts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                post_id TEXT NOT NULL UNIQUE,
                author TEXT NOT NULL,
                text TEXT NOT NULL,
                url TEXT NOT NULL,
                likes INTEGER DEFAULT 0,
                retweets INTEGER DEFAULT 0,
                replies INTEGER DEFAULT 0,
                quotes INTEGER DEFAULT 0,
                bookmarks INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                relevance_score FLOAT DEFAULT 0,
                engagement_potential FLOAT DEFAULT 0,
                persona_recommendation TEXT,
                risk_level TEXT,
                angle_summary TEXT,
                recommendation_score FLOAT DEFAULT 0,
                reasoning TEXT,
                status TEXT DEFAULT 'pending',
                draft_comment TEXT,
                final_comment TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE,
                posted_at TIMESTAMP WITH TIME ZONE,
                posted_url TEXT,
                error TEXT
            );
        """)
        conn.commit()
        results.append("✅ Created review_posts table")
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_review_posts_status ON review_posts(status);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_review_posts_created_at ON review_posts(created_at DESC);
        """)
        conn.commit()
        results.append("✅ Created indexes")
        
        # Migration 006: Add response tracking
        results.append("Running 006_add_response_tracking.sql...")
        cursor.execute("""
            ALTER TABLE review_posts ADD COLUMN IF NOT EXISTS responded_at TIMESTAMP WITH TIME ZONE;
        """)
        cursor.execute("""
            ALTER TABLE review_posts ADD COLUMN IF NOT EXISTS response_text TEXT;
        """)
        cursor.execute("""
            ALTER TABLE review_posts ADD COLUMN IF NOT EXISTS response_url TEXT;
        """)
        cursor.execute("""
            ALTER TABLE review_posts ADD COLUMN IF NOT EXISTS posted BOOLEAN DEFAULT FALSE;
        """)
        conn.commit()
        results.append("✅ Added response tracking columns")
        
        # Create index for responded posts
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_review_posts_responded ON review_posts(responded_at) WHERE responded_at IS NOT NULL;
        """)
        conn.commit()
        results.append("✅ Created responded index")
        
        # Verify table exists
        cursor.execute("SELECT COUNT(*) FROM review_posts")
        count = cursor.fetchone()[0]
        results.append(f"✅ Verified: review_posts table exists with {count} rows")
        
        cursor.close()
        
        return {
            "success": True,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@router.get("/status")
async def migration_status():
    """Check if migrations have been run"""
    
    if not is_postgres_mode():
        return {
            "success": False,
            "message": "Only works with PostgreSQL"
        }
    
    try:
        db = get_supabase_admin()
        conn = db._get_conn()
        cursor = conn.cursor()
        
        # Check if review_posts table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'review_posts'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            return {
                "review_posts_exists": False,
                "needs_migration": True
            }
        
        # Check if response tracking columns exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'review_posts' 
            AND column_name IN ('responded_at', 'response_text', 'response_url', 'posted')
        """)
        columns = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT COUNT(*) FROM review_posts")
        count = cursor.fetchone()[0]
        
        cursor.close()
        
        return {
            "review_posts_exists": True,
            "has_response_tracking": len(columns) == 4,
            "tracking_columns": columns,
            "row_count": count,
            "needs_migration": len(columns) < 4
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
