-- Migration 005: Create user actions table
-- Description: Track user behavior for analytics and recommendations

CREATE TABLE IF NOT EXISTS user_actions (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('view', 'favorite', 'unfavorite', 'contact', 'search', 'share')),
    property_id VARCHAR(255),  -- NULL for search actions
    metadata JSONB,  -- Action metadata (search query, filters, etc.)
    created_at TIMESTAMP DEFAULT NOW(),

    -- Foreign key
    CONSTRAINT fk_user_actions_user FOREIGN KEY (user_id)
        REFERENCES "user"(id) ON DELETE CASCADE
);

-- Indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_user_actions_user_id ON user_actions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_actions_property_id ON user_actions(property_id) WHERE property_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_actions_type ON user_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_user_actions_created_at ON user_actions(created_at DESC);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_user_actions_user_type_date
    ON user_actions(user_id, action_type, created_at DESC);

-- Partitioning hint: This table will grow large, consider partitioning by created_at
COMMENT ON TABLE user_actions IS 'User behavior tracking for analytics and ML recommendations';
COMMENT ON COLUMN user_actions.action_type IS 'Type: view, favorite, unfavorite, contact, search, share';
COMMENT ON COLUMN user_actions.metadata IS 'Additional context as JSON (query, filters, session_id, etc.)';

-- Example metadata structure:
-- {
--   "query": "căn hộ quận 7",
--   "filters": {"min_price": 2000000000, "max_price": 5000000000},
--   "session_id": "abc123",
--   "referrer": "google"
-- }
