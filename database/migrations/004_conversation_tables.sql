-- Migration 004: Conversation Tables for Context Memory
-- Purpose: Store conversation history for Orchestrator agent
-- Date: 2025-11-01

-- Table: users (for conversation ownership)
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: conversations (conversation sessions)
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(500),  -- Optional: first message or summary
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: messages (conversation messages)
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,

    -- Optional: metadata for debugging/analytics
    metadata JSONB DEFAULT '{}',  -- Store extra info like model used, tokens, etc.

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes (created separately after tables)
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at ASC);

-- Function: Auto-update updated_at on conversations
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET updated_at = NOW()
    WHERE conversation_id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Update conversation.updated_at when new message added
CREATE TRIGGER trigger_update_conversation_timestamp
AFTER INSERT ON messages
FOR EACH ROW
EXECUTE FUNCTION update_conversation_timestamp();

-- Comments for documentation
COMMENT ON TABLE users IS 'User accounts for conversation ownership';
COMMENT ON TABLE conversations IS 'Conversation sessions between user and AI';
COMMENT ON TABLE messages IS 'Individual messages in conversations (chronological order)';
COMMENT ON COLUMN messages.metadata IS 'Optional JSON metadata: {model, tokens, intent, etc.}';

-- Sample test data (optional, remove in production)
-- INSERT INTO users (user_id, email, name)
-- VALUES ('00000000-0000-0000-0000-000000000001', 'test@example.com', 'Test User');
