# ================================================================
# Setup REE-AI Database on Remote Server (Windows PowerShell)
# ================================================================
# Server: 103.153.74.213
# SSH Key: C:\Users\dev\.ssh\tmone
# ================================================================

$ErrorActionPreference = "Stop"

# Configuration
$REMOTE_HOST = "103.153.74.213"
$SSH_KEY = "C:\Users\dev\.ssh\tmone"
$DB_NAME = "ree_ai"
$DB_USER = "ree_ai_user"
$DB_PASSWORD = "ree_ai_pass_2025"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "REE-AI Database Setup on Remote Server" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Server: $REMOTE_HOST"
Write-Host "Database: $DB_NAME"
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if SSH key exists
if (-not (Test-Path $SSH_KEY)) {
    Write-Host "❌ SSH key not found: $SSH_KEY" -ForegroundColor Red
    exit 1
}

Write-Host "✅ SSH key found: $SSH_KEY" -ForegroundColor Green
Write-Host ""

# Test SSH connection
Write-Host "📡 Testing SSH connection..." -ForegroundColor Yellow
try {
    $result = ssh -i $SSH_KEY -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@$REMOTE_HOST "echo 'SSH OK'"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SSH connection successful" -ForegroundColor Green
    } else {
        throw "SSH connection failed"
    }
} catch {
    Write-Host "❌ SSH connection failed. Please check:" -ForegroundColor Red
    Write-Host "  - Server IP: $REMOTE_HOST"
    Write-Host "  - SSH key: $SSH_KEY"
    Write-Host "  - SSH key permissions"
    Write-Host "  - Server SSH port (default: 22)"
    exit 1
}
Write-Host ""

# Check if PostgreSQL is installed
Write-Host "🔍 Checking PostgreSQL installation..." -ForegroundColor Yellow
$pgCheck = ssh -i $SSH_KEY root@$REMOTE_HOST "which psql 2>/dev/null"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ PostgreSQL not found on server. Please install it first:" -ForegroundColor Red
    Write-Host "  ssh -i $SSH_KEY root@$REMOTE_HOST"
    Write-Host "  apt-get update && apt-get install -y postgresql postgresql-contrib"
    exit 1
}
Write-Host "✅ PostgreSQL is installed" -ForegroundColor Green
Write-Host ""

# Get PostgreSQL version
Write-Host "📊 PostgreSQL version:" -ForegroundColor Yellow
ssh -i $SSH_KEY root@$REMOTE_HOST "sudo -u postgres psql --version"
Write-Host ""

# Create database and user
Write-Host "📦 Creating database and user..." -ForegroundColor Yellow
$createDbScript = @"
sudo -u postgres psql << 'EOF'
-- Drop database if exists (for clean setup)
DROP DATABASE IF EXISTS ree_ai;

-- Drop user if exists
DROP USER IF EXISTS ree_ai_user;

-- Create user
CREATE USER ree_ai_user WITH PASSWORD '$DB_PASSWORD';

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
SELECT 'Database created successfully!' as status;
EOF
"@

ssh -i $SSH_KEY root@$REMOTE_HOST $createDbScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database and user created successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create database" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Upload migration scripts
Write-Host "📤 Uploading migration scripts..." -ForegroundColor Yellow
$scriptPath = "D:\Crastonic\ree-ai\scripts"

scp -i $SSH_KEY `
    "$scriptPath\rebuild_master_data_schema.sql" `
    "$scriptPath\seed_master_data.sql" `
    "$scriptPath\seed_amenities_views.sql" `
    root@${REMOTE_HOST}:/tmp/

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migration scripts uploaded" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to upload scripts" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Run migration scripts
Write-Host "🔧 Running migration scripts..." -ForegroundColor Yellow
$runMigrations = @"
# Run schema migration
echo '1. Creating schema...'
sudo -u postgres psql -d ree_ai < /tmp/rebuild_master_data_schema.sql

# Run seed data
echo '2. Seeding core data...'
sudo -u postgres psql -d ree_ai < /tmp/seed_master_data.sql

# Run amenities/views seed
echo '3. Seeding amenities and views...'
sudo -u postgres psql -d ree_ai < /tmp/seed_amenities_views.sql

# Verify data
echo '4. Verifying data...'
sudo -u postgres psql -d ree_ai << 'PSQL'
SELECT
    table_name,
    COUNT(*) as records
FROM (
    SELECT 'amenities' as table_name, id FROM ree_common.amenities
    UNION ALL
    SELECT 'views', id FROM ree_common.views
    UNION ALL
    SELECT 'districts', id FROM ree_common.districts
    UNION ALL
    SELECT 'property_types', id FROM ree_common.property_types
) t
GROUP BY table_name
ORDER BY table_name;
PSQL

# Cleanup temp files
rm -f /tmp/rebuild_master_data_schema.sql
rm -f /tmp/seed_master_data.sql
rm -f /tmp/seed_amenities_views.sql

echo 'Migration completed!'
"@

ssh -i $SSH_KEY root@$REMOTE_HOST $runMigrations

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migration completed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Migration failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Configure PostgreSQL for remote connections
Write-Host "🔐 Configuring PostgreSQL for remote connections..." -ForegroundColor Yellow
$configPg = @"
# Find PostgreSQL config directory
PG_VERSION=`$(sudo -u postgres psql -tAc "SHOW server_version" | cut -d'.' -f1)
PG_CONF="/etc/postgresql/`$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/`$PG_VERSION/main/pg_hba.conf"

# Backup original configs
cp `$PG_CONF `${PG_CONF}.backup 2>/dev/null || true
cp `$PG_HBA `${PG_HBA}.backup 2>/dev/null || true

# Allow remote connections
if ! grep -q "^listen_addresses = '\*'" `$PG_CONF; then
    echo "listen_addresses = '*'" >> `$PG_CONF
fi

# Add remote access rule for ree_ai database
if ! grep -q "host.*ree_ai.*ree_ai_user" `$PG_HBA; then
    echo "host    ree_ai    ree_ai_user    0.0.0.0/0    md5" >> `$PG_HBA
fi

# Restart PostgreSQL
systemctl restart postgresql

echo 'PostgreSQL configured for remote access'
"@

ssh -i $SSH_KEY root@$REMOTE_HOST $configPg

Write-Host "✅ PostgreSQL configured for remote access" -ForegroundColor Green
Write-Host ""

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "✅ DATABASE SETUP COMPLETED SUCCESSFULLY" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Connection Details:" -ForegroundColor Yellow
Write-Host "  Host:     $REMOTE_HOST"
Write-Host "  Port:     5432"
Write-Host "  Database: $DB_NAME"
Write-Host "  User:     $DB_USER"
Write-Host "  Password: $DB_PASSWORD"
Write-Host ""
Write-Host "Connection String:" -ForegroundColor Yellow
Write-Host "  postgresql://$DB_USER:$DB_PASSWORD@$REMOTE_HOST:5432/$DB_NAME"
Write-Host ""
Write-Host "Test connection (from local):" -ForegroundColor Yellow
Write-Host "  psql -h $REMOTE_HOST -p 5432 -U $DB_USER -d $DB_NAME"
Write-Host ""
Write-Host "Update .env file:" -ForegroundColor Yellow
Write-Host "  DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$REMOTE_HOST:5432/$DB_NAME"
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
