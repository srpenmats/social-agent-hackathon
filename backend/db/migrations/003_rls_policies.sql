-- 003_rls_policies.sql
-- Row Level Security policies for role-based access control
-- Roles stored in JWT claims: admin, analyst, viewer

-- Helper function to extract role from JWT
CREATE OR REPLACE FUNCTION auth.user_role()
RETURNS TEXT AS $$
    SELECT coalesce(
        current_setting('request.jwt.claims', true)::json->>'user_role',
        'viewer'
    );
$$ LANGUAGE sql STABLE;

-- Enable RLS on all tables
ALTER TABLE platforms ENABLE ROW LEVEL SECURITY;
ALTER TABLE discovered_videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE engagements ENABLE ROW LEVEL SECURITY;
ALTER TABLE engagement_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_voice_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE comment_embeddings ENABLE ROW LEVEL SECURITY;

-- Admin: full read/write on all tables
CREATE POLICY admin_all ON platforms FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON discovered_videos FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON generated_comments FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON risk_scores FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON engagements FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON engagement_metrics FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON saved_comments FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON review_queue FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON voice_config FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON risk_config FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON system_config FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON audit_log FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON brand_voice_embeddings FOR ALL USING (auth.user_role() = 'admin');
CREATE POLICY admin_all ON comment_embeddings FOR ALL USING (auth.user_role() = 'admin');

-- Analyst: read all tables
CREATE POLICY analyst_read ON platforms FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON discovered_videos FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON generated_comments FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON risk_scores FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON engagements FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON engagement_metrics FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON saved_comments FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON review_queue FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON voice_config FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON risk_config FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON system_config FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON audit_log FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON brand_voice_embeddings FOR SELECT USING (auth.user_role() = 'analyst');
CREATE POLICY analyst_read ON comment_embeddings FOR SELECT USING (auth.user_role() = 'analyst');

-- Analyst: write review decisions
CREATE POLICY analyst_review ON review_queue FOR UPDATE
    USING (auth.user_role() = 'analyst')
    WITH CHECK (auth.user_role() = 'analyst');

-- Analyst: write saved comments
CREATE POLICY analyst_save ON saved_comments FOR INSERT
    WITH CHECK (auth.user_role() = 'analyst');
CREATE POLICY analyst_save_delete ON saved_comments FOR DELETE
    USING (auth.user_role() = 'analyst');

-- Viewer: read only on all tables
CREATE POLICY viewer_read ON platforms FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON discovered_videos FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON generated_comments FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON risk_scores FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON engagements FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON engagement_metrics FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON saved_comments FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON review_queue FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON voice_config FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON risk_config FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON system_config FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON audit_log FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON brand_voice_embeddings FOR SELECT USING (auth.user_role() = 'viewer');
CREATE POLICY viewer_read ON comment_embeddings FOR SELECT USING (auth.user_role() = 'viewer');
