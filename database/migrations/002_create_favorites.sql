-- Migration 002: Create favorites table
-- Description: Allows users to save favorite properties

CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    property_id VARCHAR(255) NOT NULL,
    notes TEXT,  -- User's private notes about the property
    created_at TIMESTAMP DEFAULT NOW(),

    -- Ensure unique user-property combination
    UNIQUE (user_id, property_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_property_id ON favorites(property_id);
CREATE INDEX IF NOT EXISTS idx_favorites_created_at ON favorites(created_at DESC);

-- Add foreign key if user table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user') THEN
        ALTER TABLE favorites
        ADD CONSTRAINT IF NOT EXISTS fk_favorites_user
        FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE;
    END IF;
END $$;

COMMENT ON TABLE favorites IS 'User favorite properties';
COMMENT ON COLUMN favorites.user_id IS 'User who favorited the property';
COMMENT ON COLUMN favorites.property_id IS 'Property ID from OpenSearch';
COMMENT ON COLUMN favorites.notes IS 'User private notes about property';
