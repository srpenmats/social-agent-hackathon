-- NeoClaw Discovery Queue Tables
-- Supports async processing: Backend queues → NeoClaw processes → Results stored

-- Queue of pending discovery requests
CREATE TABLE IF NOT EXISTS discovery_queue (
    id SERIAL PRIMARY KEY,
    query_id VARCHAR(255) UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    max_results INTEGER DEFAULT 10,
    status VARCHAR(50) DEFAULT 'queued',  -- queued | processing | complete | error
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    processing_started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_discovery_queue_status ON discovery_queue(status);
CREATE INDEX IF NOT EXISTS idx_discovery_queue_created ON discovery_queue(created_at);

-- Completed discovery results (NeoClaw posts here)
CREATE TABLE IF NOT EXISTS discovery_results (
    id SERIAL PRIMARY KEY,
    query_id VARCHAR(255) UNIQUE NOT NULL,
    results JSONB NOT NULL,  -- Full DiscoveryResults object
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_discovery_results_query ON discovery_results(query_id);

-- discovered_posts table (if not exists - reuse existing)
-- This is where individual posts are stored for dashboard metrics
CREATE TABLE IF NOT EXISTS discovered_posts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    post_id VARCHAR(255) UNIQUE NOT NULL,
    post_url TEXT,
    post_text TEXT,
    author_username VARCHAR(255),
    author_name VARCHAR(255),
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    quotes INTEGER DEFAULT 0,
    bookmarks INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'discovered',
    discovered_at TIMESTAMPTZ DEFAULT now(),
    job_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_discovered_posts_platform ON discovered_posts(platform);
CREATE INDEX IF NOT EXISTS idx_discovered_posts_status ON discovered_posts(status);
CREATE INDEX IF NOT EXISTS idx_discovered_posts_discovered ON discovered_posts(discovered_at DESC);
