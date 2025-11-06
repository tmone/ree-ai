-- Migration 001: Add user types and seller fields
-- Description: Extends user table to support seller/buyer distinction

-- Add new columns to users table (non-breaking changes)
ALTER TABLE IF EXISTS "user"
ADD COLUMN IF NOT EXISTS user_type VARCHAR(20) DEFAULT 'buyer',
ADD COLUMN IF NOT EXISTS company_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS license_number VARCHAR(100),
ADD COLUMN IF NOT EXISTS verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_user_type ON "user"(user_type);
CREATE INDEX IF NOT EXISTS idx_user_verified ON "user"(verified);
CREATE INDEX IF NOT EXISTS idx_user_phone ON "user"(phone_number);

-- Update existing users to be buyers (they were only searching before)
UPDATE "user" SET user_type = 'buyer' WHERE user_type IS NULL;

-- Add check constraint for user_type
ALTER TABLE "user"
ADD CONSTRAINT IF NOT EXISTS check_user_type
CHECK (user_type IN ('seller', 'buyer', 'both'));

COMMENT ON COLUMN "user".user_type IS 'User classification: seller, buyer, or both';
COMMENT ON COLUMN "user".company_name IS 'Company name for real estate agencies';
COMMENT ON COLUMN "user".license_number IS 'Real estate license number for sellers';
COMMENT ON COLUMN "user".verified IS 'Email/phone verification status';
