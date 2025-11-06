# Database Migrations

This directory contains SQL migration scripts for REE AI platform database schema updates.

## Migration Files

| File | Description | Status |
|------|-------------|--------|
| `001_add_user_types.sql` | Add user type fields (seller/buyer/both) | ✅ Ready |
| `002_create_favorites.sql` | Create favorites table | ✅ Ready |
| `003_create_saved_searches.sql` | Create saved searches with notifications | ✅ Ready |
| `004_create_inquiries.sql` | Create buyer-seller inquiry system | ✅ Ready |
| `005_create_user_actions.sql` | Create analytics tracking table | ✅ Ready |

## Running Migrations

### Option 1: PostgreSQL CLI (Manual)

```bash
# Connect to database
psql -h localhost -U ree_ai_user -d ree_ai

# Run migrations in order
\i database/migrations/001_add_user_types.sql
\i database/migrations/002_create_favorites.sql
\i database/migrations/003_create_saved_searches.sql
\i database/migrations/004_create_inquiries.sql
\i database/migrations/005_create_user_actions.sql
```

### Option 2: Docker Compose (Automatic)

```bash
# Copy migrations to running container
docker cp database/migrations/ ree-ai-postgres:/tmp/

# Execute migrations
docker exec -it ree-ai-postgres bash -c "
  for file in /tmp/migrations/*.sql; do
    echo 'Running: \$file'
    psql -U ree_ai_user -d ree_ai -f \"\$file\"
  done
"
```

### Option 3: Migration Script (Recommended)

```bash
# Run all migrations
./scripts/run-migrations.sh

# Or run individually
./scripts/run-migrations.sh 001
```

## Migration Guidelines

### Principles

1. **Backward Compatible**: Always use `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`
2. **Idempotent**: Can run multiple times without errors
3. **Sequential**: Numbered 001, 002, 003... (run in order)
4. **Non-Breaking**: Never drop columns in production
5. **Documented**: Include comments explaining changes

### Creating New Migration

```sql
-- Migration XXX: Short description
-- Description: Detailed explanation of what this migration does

-- Your SQL here
CREATE TABLE IF NOT EXISTS my_table (
    id SERIAL PRIMARY KEY,
    ...
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_my_table_col ON my_table(col);

-- Add comments
COMMENT ON TABLE my_table IS 'Purpose of this table';
```

### Testing Migrations

```bash
# 1. Backup database
pg_dump -U ree_ai_user -d ree_ai > backup.sql

# 2. Run migration
psql -U ree_ai_user -d ree_ai -f database/migrations/XXX_name.sql

# 3. Verify schema
psql -U ree_ai_user -d ree_ai -c "\d+ table_name"

# 4. Rollback if needed
psql -U ree_ai_user -d ree_ai < backup.sql
```

## Schema Overview

### After All Migrations

```
┌─────────────────┐
│     users       │ (Open WebUI existing table)
│─────────────────│
│ id (PK)         │
│ email           │
│ user_type       │ ← NEW: seller/buyer/both
│ company_name    │ ← NEW
│ verified        │ ← NEW
└─────────────────┘
        │
        ├─────────────────────┐
        │                     │
        ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│   favorites     │   │ saved_searches  │
│─────────────────│   │─────────────────│
│ id (PK)         │   │ id (PK)         │
│ user_id (FK)    │   │ user_id (FK)    │
│ property_id     │   │ search_name     │
│ notes           │   │ query           │
│ created_at      │   │ filters (JSON)  │
└─────────────────┘   │ notify_new      │
                      └─────────────────┘
        │
        │
        ▼
┌─────────────────┐
│   inquiries     │
│─────────────────│
│ id (PK)         │
│ sender_id (FK)  │ ← Buyer
│ receiver_id(FK) │ ← Seller
│ property_id     │
│ message         │
│ response        │
│ status          │
└─────────────────┘
        │
        │
        ▼
┌─────────────────┐
│  user_actions   │
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │
│ action_type     │
│ property_id     │
│ metadata (JSON) │
│ created_at      │
└─────────────────┘
```

## OpenSearch Mappings

Properties are stored in OpenSearch (not PostgreSQL). Update mapping:

```json
{
  "mappings": {
    "properties": {
      "owner_id": {"type": "keyword"},
      "status": {"type": "keyword"},
      "verification_status": {"type": "keyword"},
      "listing_type": {"type": "keyword"},
      "views_count": {"type": "integer"},
      "favorites_count": {"type": "integer"},
      "inquiries_count": {"type": "integer"},
      "published_at": {"type": "date"},
      "expires_at": {"type": "date"}
    }
  }
}
```

## Rollback Strategy

### Undo 001: User Types

```sql
ALTER TABLE "user"
DROP COLUMN IF EXISTS user_type,
DROP COLUMN IF EXISTS company_name,
DROP COLUMN IF EXISTS license_number,
DROP COLUMN IF EXISTS verified,
DROP COLUMN IF EXISTS phone_number,
DROP COLUMN IF EXISTS full_name;
```

### Undo 002-005: Drop Tables

```sql
DROP TABLE IF EXISTS user_actions CASCADE;
DROP TABLE IF EXISTS inquiries CASCADE;
DROP TABLE IF EXISTS saved_searches CASCADE;
DROP TABLE IF EXISTS favorites CASCADE;
```

**⚠️ WARNING**: Only rollback in development. In production, create forward-fixing migrations instead.

## Performance Considerations

### Indexing Strategy

- **user_id**: Indexed in all tables (foreign key queries)
- **created_at**: Indexed DESC for recent-first queries
- **status**: Indexed for filtering active/pending items
- **Composite**: user_id + type + date for analytics

### Query Optimization

```sql
-- Get user's recent favorites (FAST - uses indexes)
SELECT * FROM favorites
WHERE user_id = 'user123'
ORDER BY created_at DESC
LIMIT 20;

-- Get seller's pending inquiries (FAST)
SELECT * FROM inquiries
WHERE receiver_id = 'seller456' AND status = 'pending'
ORDER BY created_at DESC;

-- Analytics query (uses composite index)
SELECT action_type, COUNT(*)
FROM user_actions
WHERE user_id = 'user123'
AND created_at > NOW() - INTERVAL '30 days'
GROUP BY action_type;
```

### Maintenance

```sql
-- Vacuum tables regularly
VACUUM ANALYZE favorites;
VACUUM ANALYZE saved_searches;
VACUUM ANALYZE inquiries;
VACUUM ANALYZE user_actions;

-- Reindex if queries slow down
REINDEX TABLE user_actions;
```

## Future Considerations

1. **Partitioning**: `user_actions` table by month (high volume)
2. **Archiving**: Move old inquiries (>1 year) to archive table
3. **Denormalization**: Cache frequent queries in Redis
4. **Replication**: Read replicas for analytics queries

---

**Last Updated**: 2025-01-15
**Schema Version**: 1.0.0
**Compatible With**: PostgreSQL 13+
