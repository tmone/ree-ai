-- Migration: Crawler Configuration and State Management
-- Purpose: Store auto-generated crawl configs and track crawl state

-- Table: crawl_configs
-- Stores AI-generated configurations for each real estate site
CREATE TABLE IF NOT EXISTS crawl_configs (
    id SERIAL PRIMARY KEY,
    site_domain VARCHAR(255) UNIQUE NOT NULL,
    site_name VARCHAR(255) NOT NULL,
    base_url TEXT NOT NULL,

    -- Structure (JSON format)
    selectors JSONB NOT NULL,  -- {card, title, price, location, area, description, link, image}
    pagination JSONB NOT NULL, -- {pattern, max_pages, per_page}

    -- Crawl strategy
    rate_limit_seconds FLOAT DEFAULT 2.0,
    max_workers INT DEFAULT 5,
    crawl_frequency VARCHAR(50) DEFAULT 'daily',  -- 'hourly', 'daily', 'weekly'

    -- Technical flags
    has_cloudflare BOOLEAN DEFAULT false,
    requires_js BOOLEAN DEFAULT false,

    -- Quality metrics
    quality_score FLOAT DEFAULT 5.0,  -- 1-10
    data_completeness FLOAT DEFAULT 0.5,  -- 0-1
    data_fields JSONB DEFAULT '[]',  -- ['price', 'location', etc]

    -- State
    enabled BOOLEAN DEFAULT true,
    status VARCHAR(50) DEFAULT 'active',  -- 'active', 'rate_limited', 'blocked', 'failed', 'disabled'

    -- Timestamps
    last_full_crawl TIMESTAMP,
    last_incremental_crawl TIMESTAMP,
    last_error TIMESTAMP,
    error_count INT DEFAULT 0,

    -- Metadata
    analysis_confidence FLOAT DEFAULT 0.8,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for crawl_configs
CREATE INDEX idx_crawl_configs_domain ON crawl_configs(site_domain);
CREATE INDEX idx_crawl_configs_enabled ON crawl_configs(enabled);
CREATE INDEX idx_crawl_configs_status ON crawl_configs(status);
CREATE INDEX idx_crawl_configs_frequency ON crawl_configs(crawl_frequency);

-- Table: crawl_state
-- Tracks individual URLs and their state (for incremental crawling)
CREATE TABLE IF NOT EXISTS crawl_state (
    id SERIAL PRIMARY KEY,
    site_domain VARCHAR(255) NOT NULL REFERENCES crawl_configs(site_domain) ON DELETE CASCADE,
    url TEXT NOT NULL,
    url_hash VARCHAR(64) NOT NULL,  -- MD5 hash for faster lookups

    -- Content tracking
    content_hash VARCHAR(64),  -- Hash of property data for change detection
    property_id INT REFERENCES properties(id) ON DELETE SET NULL,

    -- State
    status VARCHAR(50) DEFAULT 'active',  -- 'active', 'updated', 'removed'

    -- Timestamps
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP,

    UNIQUE(site_domain, url_hash)
);

-- Indexes for crawl_state
CREATE INDEX idx_crawl_state_domain ON crawl_state(site_domain);
CREATE INDEX idx_crawl_state_url_hash ON crawl_state(url_hash);
CREATE INDEX idx_crawl_state_status ON crawl_state(status);
CREATE INDEX idx_crawl_state_last_seen ON crawl_state(last_seen);

-- Table: crawl_jobs
-- Tracks individual crawl jobs (for monitoring and debugging)
CREATE TABLE IF NOT EXISTS crawl_jobs (
    id SERIAL PRIMARY KEY,
    site_domain VARCHAR(255) REFERENCES crawl_configs(site_domain) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,  -- 'full', 'incremental', 'test'

    -- Job state
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'

    -- Metrics
    pages_crawled INT DEFAULT 0,
    properties_found INT DEFAULT 0,
    properties_new INT DEFAULT 0,
    properties_updated INT DEFAULT 0,
    properties_removed INT DEFAULT 0,
    errors_count INT DEFAULT 0,

    -- Performance
    duration_seconds FLOAT,
    avg_page_time FLOAT,

    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Error details
    error_message TEXT,
    error_details JSONB
);

-- Indexes for crawl_jobs
CREATE INDEX idx_crawl_jobs_domain ON crawl_jobs(site_domain);
CREATE INDEX idx_crawl_jobs_status ON crawl_jobs(status);
CREATE INDEX idx_crawl_jobs_type ON crawl_jobs(job_type);
CREATE INDEX idx_crawl_jobs_created ON crawl_jobs(created_at DESC);

-- Table: rate_limit_events
-- Tracks rate limit detections for adaptive rate limiting
CREATE TABLE IF NOT EXISTS rate_limit_events (
    id SERIAL PRIMARY KEY,
    site_domain VARCHAR(255) REFERENCES crawl_configs(site_domain) ON DELETE CASCADE,

    -- Event details
    event_type VARCHAR(50) NOT NULL,  -- 'http_429', 'cloudflare', 'captcha', 'ip_block', 'timeout'
    response_code INT,
    response_headers JSONB,
    retry_after INT,  -- seconds

    -- Context
    url TEXT,
    worker_id INT,

    -- Timestamp
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for rate_limit_events
CREATE INDEX idx_rate_limit_domain ON rate_limit_events(site_domain);
CREATE INDEX idx_rate_limit_type ON rate_limit_events(event_type);
CREATE INDEX idx_rate_limit_detected ON rate_limit_events(detected_at DESC);

-- Update trigger for crawl_configs
CREATE OR REPLACE FUNCTION update_crawl_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER crawl_configs_update_timestamp
BEFORE UPDATE ON crawl_configs
FOR EACH ROW
EXECUTE FUNCTION update_crawl_config_timestamp();

-- Function to mark URLs as removed (not seen in N days)
CREATE OR REPLACE FUNCTION mark_removed_properties(p_site_domain VARCHAR, p_days INT DEFAULT 7)
RETURNS INT AS $$
DECLARE
    updated_count INT;
BEGIN
    UPDATE crawl_state
    SET status = 'removed'
    WHERE site_domain = p_site_domain
      AND status = 'active'
      AND last_seen < (CURRENT_TIMESTAMP - INTERVAL '1 day' * p_days);

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get crawl statistics for a site
CREATE OR REPLACE FUNCTION get_crawl_stats(p_site_domain VARCHAR)
RETURNS TABLE (
    total_urls INT,
    active_urls INT,
    updated_urls INT,
    removed_urls INT,
    last_crawl TIMESTAMP,
    avg_quality FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::INT as total_urls,
        COUNT(*) FILTER (WHERE status = 'active')::INT as active_urls,
        COUNT(*) FILTER (WHERE status = 'updated')::INT as updated_urls,
        COUNT(*) FILTER (WHERE status = 'removed')::INT as removed_urls,
        MAX(last_seen) as last_crawl,
        (SELECT quality_score FROM crawl_configs WHERE site_domain = p_site_domain)
    FROM crawl_state
    WHERE site_domain = p_site_domain;
END;
$$ LANGUAGE plpgsql;

-- Insert sample configs for testing
INSERT INTO crawl_configs (
    site_domain,
    site_name,
    base_url,
    selectors,
    pagination,
    rate_limit_seconds,
    max_workers,
    quality_score,
    data_fields
) VALUES
(
    'batdongsan.com.vn',
    'Batdongsan.com.vn',
    'https://batdongsan.com.vn/nha-dat-ban',
    '{
        "card": ".re__card-full",
        "title": ".re__card-title",
        "price": ".re__card-config-price",
        "location": ".re__card-location",
        "area": ".re__card-config-area",
        "description": ".re__card-description",
        "link": "a"
    }',
    '{
        "pattern": "/p{page}",
        "max_pages": 500,
        "per_page": 20
    }',
    2.0,
    5,
    9.5,
    '["title", "price", "location", "area", "description"]'
),
(
    'nhatot.com',
    'Nhatot.com',
    'https://nhatot.com/mua-ban-bat-dong-san',
    '{
        "card": ".AdItem_adItem__2O0X5",
        "title": ".AdItem_adName__3O6tT",
        "price": ".AdItem_price__3uOMB",
        "location": ".AdItem_location__3O6tT",
        "area": ".AdItem_area__3O6tT",
        "description": ".AdItem_description__3O6tT",
        "link": "a"
    }',
    '{
        "pattern": "?page={page}",
        "max_pages": 300,
        "per_page": 20
    }',
    3.0,
    3,
    7.5,
    '["title", "price", "location", "area"]'
)
ON CONFLICT (site_domain) DO NOTHING;
