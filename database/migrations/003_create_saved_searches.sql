-- Migration 003: Create saved searches table
-- Description: Allows users to save search criteria and get notifications

CREATE TABLE IF NOT EXISTS saved_searches (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    search_name VARCHAR(255) NOT NULL,
    query TEXT NOT NULL,
    filters JSONB,  -- Search filters as JSON
    notify_new_listings BOOLEAN DEFAULT TRUE,
    notify_price_drops BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_notified_at TIMESTAMP,

    -- Foreign key
    CONSTRAINT fk_saved_searches_user FOREIGN KEY (user_id)
        REFERENCES "user"(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_saved_searches_user_id ON saved_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_searches_created_at ON saved_searches(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_saved_searches_notify ON saved_searches(notify_new_listings)
    WHERE notify_new_listings = TRUE;

-- Function to automatically update updated_at
CREATE OR REPLACE FUNCTION update_saved_searches_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
DROP TRIGGER IF EXISTS trigger_update_saved_searches_updated_at ON saved_searches;
CREATE TRIGGER trigger_update_saved_searches_updated_at
    BEFORE UPDATE ON saved_searches
    FOR EACH ROW
    EXECUTE FUNCTION update_saved_searches_updated_at();

COMMENT ON TABLE saved_searches IS 'User saved search criteria with notifications';
COMMENT ON COLUMN saved_searches.filters IS 'Search filters stored as JSON (property_type, price_range, etc.)';
COMMENT ON COLUMN saved_searches.notify_new_listings IS 'Send email when new matching properties posted';
COMMENT ON COLUMN saved_searches.notify_price_drops IS 'Send email when price drops on matching properties';
COMMENT ON COLUMN saved_searches.last_notified_at IS 'Timestamp of last notification sent';
