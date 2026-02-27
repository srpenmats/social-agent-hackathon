-- Add response tracking to review_posts table
ALTER TABLE review_posts ADD COLUMN IF NOT EXISTS responded_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE review_posts ADD COLUMN IF NOT EXISTS response_text TEXT;
ALTER TABLE review_posts ADD COLUMN IF NOT EXISTS response_url TEXT;

-- Create index for quick filtering of responded posts
CREATE INDEX IF NOT EXISTS idx_review_posts_responded ON review_posts(responded_at) WHERE responded_at IS NOT NULL;

-- Add column to track if post was actually posted (vs just saved as draft)
ALTER TABLE review_posts ADD COLUMN IF NOT EXISTS posted BOOLEAN DEFAULT FALSE;
