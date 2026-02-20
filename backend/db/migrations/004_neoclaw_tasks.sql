-- 004_neoclaw_tasks.sql
-- Task queue and heartbeat tables for NeoClaw agent integration

-- Task queue for NeoClaw agent work items
CREATE TABLE neoclaw_tasks (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    platform VARCHAR(20),
    payload JSONB NOT NULL,
    priority INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'pending',
    assigned_agent VARCHAR(100),
    result JSONB,
    error TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_by VARCHAR(50),
    metadata JSONB
);

CREATE INDEX idx_neoclaw_tasks_status_priority ON neoclaw_tasks (status, priority);
CREATE INDEX idx_neoclaw_tasks_platform ON neoclaw_tasks (platform);
CREATE INDEX idx_neoclaw_tasks_type ON neoclaw_tasks (type);
CREATE INDEX idx_neoclaw_tasks_expires ON neoclaw_tasks (expires_at)
    WHERE status IN ('pending', 'assigned');

-- Agent heartbeat / health tracking
CREATE TABLE neoclaw_heartbeats (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    active_sessions JSONB,
    current_task_id INTEGER REFERENCES neoclaw_tasks(id),
    system_stats JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_heartbeats_agent ON neoclaw_heartbeats (agent_id, created_at DESC);

-- Row Level Security
ALTER TABLE neoclaw_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE neoclaw_heartbeats ENABLE ROW LEVEL SECURITY;

-- Admin: full access
CREATE POLICY admin_all ON neoclaw_tasks FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON neoclaw_heartbeats FOR ALL USING (auth.user_role() = 'admin');

-- Analyst: read only
CREATE POLICY analyst_read ON neoclaw_tasks FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON neoclaw_heartbeats FOR SELECT USING (auth.user_role() = 'analyst');

-- Viewer: read only
CREATE POLICY viewer_read ON neoclaw_tasks FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON neoclaw_heartbeats FOR SELECT USING (auth.user_role() = 'viewer');
