-- Migration 004: Create inquiries table
-- Description: Buyer-seller communication system

CREATE TABLE IF NOT EXISTS inquiries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id VARCHAR(255) NOT NULL,
    sender_id VARCHAR(255) NOT NULL,  -- Buyer
    receiver_id VARCHAR(255) NOT NULL,  -- Seller (property owner)

    -- Inquiry message
    message TEXT NOT NULL,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),

    -- Seller response
    response TEXT,

    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'responded', 'closed')),

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    responded_at TIMESTAMP,

    -- Foreign keys
    CONSTRAINT fk_inquiries_sender FOREIGN KEY (sender_id)
        REFERENCES "user"(id) ON DELETE CASCADE,
    CONSTRAINT fk_inquiries_receiver FOREIGN KEY (receiver_id)
        REFERENCES "user"(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_inquiries_property_id ON inquiries(property_id);
CREATE INDEX IF NOT EXISTS idx_inquiries_sender_id ON inquiries(sender_id);
CREATE INDEX IF NOT EXISTS idx_inquiries_receiver_id ON inquiries(receiver_id);
CREATE INDEX IF NOT EXISTS idx_inquiries_status ON inquiries(status);
CREATE INDEX IF NOT EXISTS idx_inquiries_created_at ON inquiries(created_at DESC);

COMMENT ON TABLE inquiries IS 'Buyer inquiries to sellers about properties';
COMMENT ON COLUMN inquiries.sender_id IS 'Buyer who sent the inquiry';
COMMENT ON COLUMN inquiries.receiver_id IS 'Seller who owns the property';
COMMENT ON COLUMN inquiries.status IS 'pending, responded, or closed';
COMMENT ON COLUMN inquiries.responded_at IS 'When seller responded to inquiry';
