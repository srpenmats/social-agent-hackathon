-- Create review_posts table for Jen workflow
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

CREATE INDEX IF NOT EXISTS idx_review_posts_status ON review_posts(status);
CREATE INDEX IF NOT EXISTS idx_review_posts_created_at ON review_posts(created_at DESC);
