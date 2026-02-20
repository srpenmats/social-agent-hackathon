-- 002_pgvector.sql
-- Vector embeddings for brand voice RAG and comment similarity

CREATE EXTENSION IF NOT EXISTS vector;

-- Brand voice document embeddings for RAG retrieval
CREATE TABLE brand_voice_embeddings (
    id BIGSERIAL PRIMARY KEY,
    document_name VARCHAR(255),
    chunk_text TEXT,
    chunk_index INTEGER DEFAULT 0,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_brand_voice_embeddings_cosine
    ON brand_voice_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Comment embeddings for similarity search
CREATE TABLE comment_embeddings (
    id BIGSERIAL PRIMARY KEY,
    comment_id BIGINT NOT NULL REFERENCES generated_comments(id) ON DELETE CASCADE,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_comment_embeddings_cosine
    ON comment_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
