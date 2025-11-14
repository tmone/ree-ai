#!/bin/bash
# ================================================================
# Setup REE-AI Database on Remote Server
# ================================================================
# Server: 103.153.74.213
# SSH Key: C:\Users\dev\.ssh\tmone
# ================================================================

set -e  # Exit on error

# Configuration
REMOTE_HOST="103.153.74.213"
SSH_KEY="C:/Users/dev/.ssh/tmone"
DB_NAME="ree_ai"
DB_USER="ree_ai_user"
DB_PASSWORD="ree_ai_pass_2025"

echo "================================================================"
echo "REE-AI Database Setup on Remote Server"
echo "================================================================"
echo "Server: $REMOTE_HOST"
echo "Database: $DB_NAME"
echo "================================================================"
echo ""

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key not found: $SSH_KEY"
    exit 1
fi

echo "✅ SSH key found: $SSH_KEY"
echo ""

# Test SSH connection
echo "📡 Testing SSH connection..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@$REMOTE_HOST "echo '✅ SSH connection successful'" || {
    echo "❌ SSH connection failed. Please check:"
    echo "  - Server IP: $REMOTE_HOST"
    echo "  - SSH key: $SSH_KEY"
    echo "  - SSH key permissions (should be 600)"
    exit 1
}
echo ""

# Check if PostgreSQL is installed
echo "🔍 Checking PostgreSQL installation..."
ssh -i "$SSH_KEY" root@$REMOTE_HOST "which psql" > /dev/null 2>&1 || {
    echo "❌ PostgreSQL not found on server. Installing..."
    ssh -i "$SSH_KEY" root@$REMOTE_HOST "apt-get update && apt-get install -y postgresql postgresql-contrib"
}
echo "✅ PostgreSQL is installed"
echo ""

# Check PostgreSQL version
echo "📊 PostgreSQL version:"
ssh -i "$SSH_KEY" root@$REMOTE_HOST "sudo -u postgres psql --version"
echo ""

# Create database and user
echo "📦 Creating database and user..."
ssh -i "$SSH_KEY" root@$REMOTE_HOST << 'ENDSSH'
sudo -u postgres psql << EOF
-- Drop database if exists (for clean setup)
DROP DATABASE IF EXISTS ree_ai;

-- Drop user if exists
DROP USER IF EXISTS ree_ai_user;

-- Create user
CREATE USER ree_ai_user WITH PASSWORD 'ree_ai_pass_2025';

-- Create database
CREATE DATABASE ree_ai
    OWNER ree_ai_user
    ENCODING 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE template0;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ree_ai TO ree_ai_user;

-- Connect to database and grant schema privileges
\c ree_ai
GRANT ALL ON SCHEMA public TO ree_ai_user;

-- Show result
\l ree_ai
EOF
ENDSSH

echo "✅ Database and user created successfully"
echo ""

# Upload migration scripts
echo "📤 Uploading migration scripts..."
scp -i "$SSH_KEY" \
    scripts/rebuild_master_data_schema.sql \
    scripts/seed_master_data.sql \
    scripts/seed_amenities_views.sql \
    root@$REMOTE_HOST:/tmp/

echo "✅ Migration scripts uploaded"
echo ""

# Run migration scripts
echo "🔧 Running migration scripts..."
ssh -i "$SSH_KEY" root@$REMOTE_HOST << 'ENDSSH'
# Run schema migration
echo "1. Creating schema..."
sudo -u postgres psql -d ree_ai < /tmp/rebuild_master_data_schema.sql

# Run seed data
echo "2. Seeding core data..."
sudo -u postgres psql -d ree_ai < /tmp/seed_master_data.sql

# Run amenities/views seed
echo "3. Seeding amenities and views..."
sudo -u postgres psql -d ree_ai < /tmp/seed_amenities_views.sql

# Verify data
echo "4. Verifying data..."
sudo -u postgres psql -d ree_ai << EOF
SELECT
    'amenities' as table_name,
    COUNT(*) as records
FROM ree_common.amenities
UNION ALL
SELECT 'views', COUNT(*) FROM ree_common.views
UNION ALL
SELECT 'districts', COUNT(*) FROM ree_common.districts
UNION ALL
SELECT 'property_types', COUNT(*) FROM ree_common.property_types;
EOF

# Cleanup temp files
rm -f /tmp/rebuild_master_data_schema.sql
rm -f /tmp/seed_master_data.sql
rm -f /tmp/seed_amenities_views.sql
ENDSSH

echo "✅ Migration completed successfully"
echo ""

# Update PostgreSQL to allow remote connections
echo "🔐 Configuring PostgreSQL for remote connections..."
ssh -i "$SSH_KEY" root@$REMOTE_HOST << 'ENDSSH'
# Find PostgreSQL config directory
PG_VERSION=$(sudo -u postgres psql -tAc "SHOW server_version" | cut -d'.' -f1)
PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"

# Backup original configs
cp $PG_CONF ${PG_CONF}.backup
cp $PG_HBA ${PG_HBA}.backup

# Allow remote connections
grep -q "^listen_addresses" $PG_CONF || echo "listen_addresses = '*'" >> $PG_CONF
sed -i "s/^#listen_addresses.*/listen_addresses = '*'/" $PG_CONF

# Add remote access rule
echo "host    ree_ai    ree_ai_user    0.0.0.0/0    md5" >> $PG_HBA

# Restart PostgreSQL
systemctl restart postgresql

echo "✅ PostgreSQL configured for remote access"
ENDSSH

echo ""
echo "================================================================"
echo "✅ DATABASE SETUP COMPLETED SUCCESSFULLY"
echo "================================================================"
echo ""
echo "Connection Details:"
echo "  Host:     $REMOTE_HOST"
echo "  Port:     5432"
echo "  Database: $DB_NAME"
echo "  User:     $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo "Connection String:"
echo "  postgresql://$DB_USER:$DB_PASSWORD@$REMOTE_HOST:5432/$DB_NAME"
echo ""
echo "Test connection:"
echo "  psql -h $REMOTE_HOST -p 5432 -U $DB_USER -d $DB_NAME"
echo ""
echo "================================================================"
