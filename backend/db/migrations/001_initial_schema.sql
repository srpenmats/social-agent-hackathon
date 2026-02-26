-- 001_initial_schema.sql
-- Core tables for the MoneyLion Social Agent Dashboard

-- Enum types
CREATE TYPE platform_status AS ENUM ('connected', 'disconnected', 'token_expiring', 'error');
CREATE TYPE comment_approach AS ENUM ('witty', 'helpful', 'supportive');
CREATE TYPE routing_decision AS ENUM ('auto_approve', 'review', 'discard');
CREATE TYPE approval_path AS ENUM ('auto', 'human');
CREATE TYPE review_decision AS ENUM ('approve', 'reject');

-- Platform connections
CREATE TABLE platforms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    auth_method VARCHAR(50),
    status platform_status NOT NULL DEFAULT 'disconnected',
    credentials_encrypted TEXT,
    session_health VARCHAR(50),
    workers_status JSONB DEFAULT '{}',
    connected_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_platforms_name ON platforms (name);

-- Discovered videos / content opportunities
CREATE TABLE discovered_videos (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    video_url TEXT NOT NULL,
    creator VARCHAR(255),
    description TEXT,
    transcript TEXT,
    hashtags TEXT[] DEFAULT '{}',
    likes INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    classification VARCHAR(100),
    discovered_at TIMESTAMPTZ DEFAULT now(),
    status VARCHAR(50) DEFAULT 'new',
    engaged BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_discovered_videos_platform ON discovered_videos (platform);
CREATE INDEX idx_discovered_videos_status ON discovered_videos (status);
CREATE INDEX idx_discovered_videos_discovered_at ON discovered_videos (discovered_at DESC);

-- Generated comment candidates
CREATE TABLE generated_comments (
    id BIGSERIAL PRIMARY KEY,
    video_id BIGINT NOT NULL REFERENCES discovered_videos(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    approach comment_approach NOT NULL,
    char_count INTEGER DEFAULT 0,
    generated_at TIMESTAMPTZ DEFAULT now(),
    selected BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_generated_comments_video_id ON generated_comments (video_id);

-- Risk scores
CREATE TABLE risk_scores (
    id BIGSERIAL PRIMARY KEY,
    comment_id BIGINT NOT NULL REFERENCES generated_comments(id) ON DELETE CASCADE,
    total_score INTEGER NOT NULL DEFAULT 0 CHECK (total_score >= 0 AND total_score <= 100),
    blocklist_score INTEGER DEFAULT 0,
    context_score INTEGER DEFAULT 0,
    ai_judge_score INTEGER DEFAULT 0,
    reasoning TEXT,
    routing_decision routing_decision NOT NULL DEFAULT 'review',
    scored_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_risk_scores_comment_id ON risk_scores (comment_id);
CREATE INDEX idx_risk_scores_routing ON risk_scores (routing_decision);

-- Posted engagements
CREATE TABLE engagements (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    video_id BIGINT REFERENCES discovered_videos(id) ON DELETE SET NULL,
    comment_id BIGINT REFERENCES generated_comments(id) ON DELETE SET NULL,
    comment_text TEXT NOT NULL,
    risk_score INTEGER DEFAULT 0,
    approval_path approval_path NOT NULL DEFAULT 'human',
    approved_by VARCHAR(255),
    posted_at TIMESTAMPTZ DEFAULT now(),
    screenshot_url TEXT,
    status VARCHAR(50) DEFAULT 'pending'
);

CREATE INDEX idx_engagements_platform ON engagements (platform);
CREATE INDEX idx_engagements_posted_at ON engagements (posted_at DESC);
CREATE INDEX idx_engagements_status ON engagements (status);

-- Post-engagement metrics snapshots
CREATE TABLE engagement_metrics (
    id BIGSERIAL PRIMARY KEY,
    engagement_id BIGINT NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    checked_at TIMESTAMPTZ DEFAULT now(),
    likes INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    reply_texts TEXT[] DEFAULT '{}',
    reply_sentiment FLOAT,
    impressions INTEGER
);

CREATE INDEX idx_engagement_metrics_engagement_id ON engagement_metrics (engagement_id);

-- Bookmarked / saved comments
CREATE TABLE saved_comments (
    id BIGSERIAL PRIMARY KEY,
    engagement_id BIGINT NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    saved_by VARCHAR(255),
    tags TEXT[] DEFAULT '{}',
    notes TEXT,
    saved_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_saved_comments_engagement_id ON saved_comments (engagement_id);

-- Human review queue
CREATE TABLE review_queue (
    id BIGSERIAL PRIMARY KEY,
    comment_id BIGINT REFERENCES generated_comments(id) ON DELETE SET NULL,
    video_id BIGINT REFERENCES discovered_videos(id) ON DELETE SET NULL,
    proposed_text TEXT NOT NULL,
    risk_score INTEGER DEFAULT 0,
    risk_reasoning TEXT,
    classification VARCHAR(100),
    queued_at TIMESTAMPTZ DEFAULT now(),
    reviewed_by VARCHAR(255),
    decision review_decision,
    decision_reason TEXT,
    decided_at TIMESTAMPTZ
);

CREATE INDEX idx_review_queue_decision ON review_queue (decision);
CREATE INDEX idx_review_queue_queued_at ON review_queue (queued_at DESC);

-- Brand voice configuration
CREATE TABLE voice_config (
    id SERIAL PRIMARY KEY,
    voice_guide_md TEXT,
    positive_examples JSONB DEFAULT '[]',
    negative_examples JSONB DEFAULT '[]',
    platform_adapters JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT now(),
    updated_by VARCHAR(255)
);

-- Risk scoring configuration
CREATE TABLE risk_config (
    id SERIAL PRIMARY KEY,
    auto_approve_max INTEGER NOT NULL DEFAULT 30,
    review_max INTEGER NOT NULL DEFAULT 65,
    blocklist JSONB DEFAULT '{}',
    override_rules JSONB DEFAULT '[]',
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- General system configuration (key-value)
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL UNIQUE,
    value JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_system_config_key ON system_config (key);

-- Immutable audit log
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100),
    entity_id VARCHAR(255),
    details JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_audit_log_user_id ON audit_log (user_id);
CREATE INDEX idx_audit_log_action ON audit_log (action);
CREATE INDEX idx_audit_log_created_at ON audit_log (created_at DESC);

-- Seed default configurations
INSERT INTO risk_config (auto_approve_max, review_max, blocklist, override_rules)
VALUES (30, 65, '{}', '[]');

INSERT INTO system_config (key, value) VALUES
    ('kill_switch', '{"active": false, "reason": null, "activated_by": null, "activated_at": null}'),
    ('rate_limits', '{"tiktok": 12, "instagram": 10, "x": 15, "min_gap_seconds": 180, "jitter_seconds": 30}'),
    ('posting_schedule', '{"start_hour": 8, "end_hour": 23, "timezone": "America/New_York"}');
