-- Migration: Re-ranking Phase 2 Data Infrastructure
-- CTO Priority 4: Re-ranking Service - Phase 2
-- Tables for seller analytics, property analytics, user preferences, and search interactions

-- ============================================================================
-- Table 1: seller_stats
-- Tracks seller performance metrics for reputation scoring
-- ============================================================================
CREATE TABLE IF NOT EXISTS seller_stats (
    seller_id VARCHAR(255) PRIMARY KEY,

    -- Listing metrics
    total_listings INT DEFAULT 0,
    active_listings INT DEFAULT 0,
    closed_deals INT DEFAULT 0,

    -- Communication metrics
    total_inquiries INT DEFAULT 0,
    total_responses INT DEFAULT 0,
    avg_response_time_hours FLOAT DEFAULT NULL,

    -- Performance scores
    response_rate FLOAT DEFAULT 0.0,  -- responses / inquiries
    closure_rate FLOAT DEFAULT 0.0,   -- closed_deals / total_listings

    -- Account info
    account_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_listing_at TIMESTAMP DEFAULT NULL,

    -- Metadata
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for lookups
CREATE INDEX IF NOT EXISTS idx_seller_stats_seller_id ON seller_stats(seller_id);

-- ============================================================================
-- Table 2: property_stats
-- Tracks property engagement metrics (views, inquiries, favorites)
-- ============================================================================
CREATE TABLE IF NOT EXISTS property_stats (
    property_id VARCHAR(255) PRIMARY KEY,

    -- View metrics
    views_total INT DEFAULT 0,
    views_7d INT DEFAULT 0,
    views_30d INT DEFAULT 0,
    last_viewed_at TIMESTAMP DEFAULT NULL,

    -- Inquiry metrics
    inquiries_total INT DEFAULT 0,
    inquiries_7d INT DEFAULT 0,
    inquiries_30d INT DEFAULT 0,
    last_inquiry_at TIMESTAMP DEFAULT NULL,

    -- Favorite metrics
    favorites_total INT DEFAULT 0,
    favorites_7d INT DEFAULT 0,
    favorites_30d INT DEFAULT 0,
    last_favorited_at TIMESTAMP DEFAULT NULL,

    -- CTR metrics (from search results)
    search_impressions INT DEFAULT 0,
    search_clicks INT DEFAULT 0,
    ctr FLOAT DEFAULT 0.0,  -- search_clicks / search_impressions

    -- Metadata
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for lookups
CREATE INDEX IF NOT EXISTS idx_property_stats_property_id ON property_stats(property_id);

-- ============================================================================
-- Table 3: user_preferences
-- Stores user search preferences for personalization
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id VARCHAR(255) PRIMARY KEY,

    -- Price preferences
    min_price BIGINT DEFAULT NULL,
    max_price BIGINT DEFAULT NULL,
    avg_clicked_price BIGINT DEFAULT NULL,

    -- Location preferences (JSONB for flexibility)
    preferred_districts JSONB DEFAULT '[]'::JSONB,
    preferred_cities JSONB DEFAULT '[]'::JSONB,

    -- Property type preferences
    preferred_property_types JSONB DEFAULT '[]'::JSONB,

    -- Size preferences
    preferred_bedrooms INT[] DEFAULT NULL,
    preferred_bathrooms INT[] DEFAULT NULL,
    preferred_area_min FLOAT DEFAULT NULL,
    preferred_area_max FLOAT DEFAULT NULL,

    -- Search history stats
    total_searches INT DEFAULT 0,
    total_clicks INT DEFAULT 0,
    total_inquiries INT DEFAULT 0,
    total_favorites INT DEFAULT 0,

    -- Metadata
    last_search_at TIMESTAMP DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for lookups
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- ============================================================================
-- Table 4: search_interactions
-- Tracks user interactions with search results for ML training
-- ============================================================================
CREATE TABLE IF NOT EXISTS search_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- User and query
    user_id VARCHAR(255) DEFAULT NULL,  -- NULL for anonymous users
    query TEXT NOT NULL,
    session_id VARCHAR(255) DEFAULT NULL,

    -- Property and ranking
    property_id VARCHAR(255) NOT NULL,
    rank_position INT NOT NULL,  -- Position in search results (1-indexed)

    -- Interaction signals
    clicked BOOLEAN DEFAULT FALSE,
    inquiry_sent BOOLEAN DEFAULT FALSE,
    favorited BOOLEAN DEFAULT FALSE,
    time_on_page_seconds INT DEFAULT 0,

    -- Context (for ML features)
    device_type VARCHAR(50) DEFAULT NULL,  -- mobile, desktop, tablet
    user_location VARCHAR(255) DEFAULT NULL,
    time_of_day VARCHAR(20) DEFAULT NULL,  -- morning, afternoon, evening, night

    -- Property features at time of search (JSONB snapshot)
    property_features JSONB DEFAULT '{}'::JSONB,

    -- Search metadata
    search_type VARCHAR(50) DEFAULT 'hybrid',  -- bm25, vector, hybrid
    hybrid_score FLOAT DEFAULT NULL,
    rerank_score FLOAT DEFAULT NULL,
    final_score FLOAT DEFAULT NULL,

    -- Timestamps
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_search_interactions_user_id ON search_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_search_interactions_property_id ON search_interactions(property_id);
CREATE INDEX IF NOT EXISTS idx_search_interactions_timestamp ON search_interactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_search_interactions_clicked ON search_interactions(clicked) WHERE clicked = TRUE;

-- Composite index for ML training queries
CREATE INDEX IF NOT EXISTS idx_search_interactions_training
    ON search_interactions(user_id, timestamp DESC, clicked, inquiry_sent, favorited);

-- ============================================================================
-- Functions and Triggers
-- ============================================================================

-- Function to update seller_stats automatically
CREATE OR REPLACE FUNCTION update_seller_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate metrics
    NEW.response_rate := CASE
        WHEN NEW.total_inquiries > 0
        THEN NEW.total_responses::FLOAT / NEW.total_inquiries::FLOAT
        ELSE 0.0
    END;

    NEW.closure_rate := CASE
        WHEN NEW.total_listings > 0
        THEN NEW.closed_deals::FLOAT / NEW.total_listings::FLOAT
        ELSE 0.0
    END;

    NEW.updated_at := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for seller_stats
DROP TRIGGER IF EXISTS trigger_update_seller_stats ON seller_stats;
CREATE TRIGGER trigger_update_seller_stats
    BEFORE INSERT OR UPDATE ON seller_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_seller_stats();

-- Function to update property_stats automatically
CREATE OR REPLACE FUNCTION update_property_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate CTR
    NEW.ctr := CASE
        WHEN NEW.search_impressions > 0
        THEN NEW.search_clicks::FLOAT / NEW.search_impressions::FLOAT
        ELSE 0.0
    END;

    NEW.updated_at := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for property_stats
DROP TRIGGER IF EXISTS trigger_update_property_stats ON property_stats;
CREATE TRIGGER trigger_update_property_stats
    BEFORE INSERT OR UPDATE ON property_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_property_stats();

-- ============================================================================
-- Sample Data (for testing)
-- ============================================================================

-- Sample seller stats
INSERT INTO seller_stats (seller_id, total_listings, active_listings, closed_deals, total_inquiries, total_responses, avg_response_time_hours, account_created_at)
VALUES
    ('seller_123', 10, 5, 3, 50, 45, 2.5, CURRENT_TIMESTAMP - INTERVAL '6 months'),
    ('seller_456', 5, 3, 1, 20, 18, 4.0, CURRENT_TIMESTAMP - INTERVAL '2 months'),
    ('seller_789', 20, 8, 8, 100, 95, 1.5, CURRENT_TIMESTAMP - INTERVAL '1 year')
ON CONFLICT (seller_id) DO NOTHING;

-- Sample property stats
INSERT INTO property_stats (property_id, views_total, views_7d, views_30d, inquiries_total, inquiries_7d, inquiries_30d, favorites_total, favorites_7d, favorites_30d, search_impressions, search_clicks)
VALUES
    ('prop_1', 100, 15, 60, 10, 2, 8, 5, 1, 3, 200, 20),
    ('prop_2', 500, 80, 300, 50, 10, 40, 30, 5, 20, 1000, 100),
    ('prop_3', 50, 5, 20, 3, 0, 2, 1, 0, 1, 100, 8)
ON CONFLICT (property_id) DO NOTHING;

-- Sample user preferences
INSERT INTO user_preferences (user_id, min_price, max_price, preferred_districts, preferred_property_types, preferred_bedrooms)
VALUES
    ('user_123', 2000000000, 8000000000, '["District 1", "District 2", "District 7"]'::JSONB, '["apartment", "villa"]'::JSONB, ARRAY[2, 3]),
    ('user_456', 1000000000, 5000000000, '["District 3", "District 10"]'::JSONB, '["apartment"]'::JSONB, ARRAY[1, 2])
ON CONFLICT (user_id) DO NOTHING;

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE seller_stats IS 'Seller performance metrics for reputation scoring (CTO Priority 4 - Phase 2)';
COMMENT ON TABLE property_stats IS 'Property engagement metrics for ranking (CTO Priority 4 - Phase 2)';
COMMENT ON TABLE user_preferences IS 'User search preferences for personalization (CTO Priority 4 - Phase 2)';
COMMENT ON TABLE search_interactions IS 'User interactions with search results for ML training (CTO Priority 4 - Phase 2)';
