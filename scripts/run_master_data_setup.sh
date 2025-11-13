#!/bin/bash
# Complete Master Data Setup Script
# Runs migrations, seeds data, and verifies installation

set -e

echo "=========================================="
echo "REE AI Master Data Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Database connection
DB_CONTAINER="ree-ai-postgres"
DB_USER="ree_ai_user"
DB_NAME="ree_ai"

echo -e "${YELLOW}Step 1: Checking PostgreSQL connection...${NC}"
if docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL connected${NC}"
else
    echo -e "${RED}✗ PostgreSQL connection failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Running migrations...${NC}"

# Migration 006
echo "Running 006_create_master_data.sql..."
docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < database/migrations/006_create_master_data.sql
echo -e "${GREEN}✓ Migration 006 completed${NC}"

# Migration 007
echo "Running 007_create_extended_master_data.sql..."
docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < database/migrations/007_create_extended_master_data.sql
echo -e "${GREEN}✓ Migration 007 completed${NC}"

# Migration 008
echo "Running 008_create_foreign_master_data.sql..."
docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < database/migrations/008_create_foreign_master_data.sql
echo -e "${GREEN}✓ Migration 008 completed${NC}"

echo ""
echo -e "${YELLOW}Step 3: Seeding master data...${NC}"
docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < database/seeds/001_seed_master_data_multilingual.sql
echo -e "${GREEN}✓ Seed data loaded${NC}"

echo ""
echo -e "${YELLOW}Step 4: Verifying installation...${NC}"

# Check table counts
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT
    'Countries' as table_name, COUNT(*) as count FROM master_countries
UNION ALL SELECT 'Currencies', COUNT(*) FROM master_currencies
UNION ALL SELECT 'Cities', COUNT(*) FROM master_cities
UNION ALL SELECT 'Districts', COUNT(*) FROM master_districts
UNION ALL SELECT 'Property Types', COUNT(*) FROM master_property_types
UNION ALL SELECT 'Amenities', COUNT(*) FROM master_amenities
UNION ALL SELECT 'Views', COUNT(*) FROM master_views
UNION ALL SELECT 'Directions', COUNT(*) FROM master_directions
ORDER BY count DESC;
"

echo ""
echo -e "${GREEN}=========================================="
echo -e "Master Data Setup Complete!"
echo -e "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Start master data service: docker-compose up master-data-service"
echo "2. Test lookup API: curl http://localhost:8095/lookup"
echo "3. Run crawler: curl -X POST http://localhost:8095/crawl-updates"
echo ""
