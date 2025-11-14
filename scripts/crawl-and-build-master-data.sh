#!/bin/bash

# =============================================================================
# Crawl Real Estate Sites and Build Master Data
# =============================================================================
# This script crawls multiple real estate websites to discover and populate
# master data automatically.
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
CRAWLER_SERVICE_URL="http://localhost:8095"
EXTRACTION_SERVICE_URL="http://localhost:8084"
MAX_PAGES=20  # Crawl 20 pages per site
SITES=("batdongsan" "mogi")

# =============================================================================
# Utility Functions
# =============================================================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

log_stat() {
    echo -e "${CYAN}  ▸ $1:${NC} $2"
}

# =============================================================================
# Pre-Flight Checks
# =============================================================================

check_services() {
    log_section "Pre-Flight Checks"

    # Check crawler service
    if curl -sf "$CRAWLER_SERVICE_URL/health" > /dev/null 2>&1; then
        log_info "✓ Crawler Service is running"
    else
        log_error "Crawler Service is not running!"
        log_info "Please start it with: docker-compose up -d crawler-service"
        exit 1
    fi

    # Check extraction service (optional but recommended)
    if curl -sf "$EXTRACTION_SERVICE_URL/health" > /dev/null 2>&1; then
        log_info "✓ Extraction Service is running"
    else
        log_warning "⚠ Extraction Service is not running (optional)"
    fi

    # Check available crawlers
    log_info "Checking available crawlers..."
    crawlers_response=$(curl -sf "$CRAWLER_SERVICE_URL/crawlers")
    crawler_count=$(echo "$crawlers_response" | grep -o '"id"' | wc -l)
    log_info "✓ Found $crawler_count crawler(s)"
}

# =============================================================================
# Crawling Functions
# =============================================================================

crawl_site() {
    local site=$1
    local max_pages=$2

    log_section "Crawling: $site"
    log_info "Max pages: $max_pages"
    log_info "Extract master data: YES"
    log_info "Auto-populate: YES"

    # Build request
    local request="{
        \"site\": \"$site\",
        \"max_pages\": $max_pages,
        \"extract_master_data\": true,
        \"auto_populate\": true
    }"

    # Start crawl
    log_info "Starting crawl (this may take a few minutes)..."

    local start_time=$(date +%s)
    local response=$(curl -sf -X POST "$CRAWLER_SERVICE_URL/crawl" \
        -H "Content-Type: application/json" \
        -d "$request")
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    if [ $? -eq 0 ]; then
        # Parse response
        local listings_scraped=$(echo "$response" | grep -o '"listings_scraped":[0-9]*' | grep -o '[0-9]*')
        local new_attributes=$(echo "$response" | grep -o '"new_attributes_found":[0-9]*' | grep -o '[0-9]*')
        local processing_time=$(echo "$response" | grep -o '"processing_time_ms":[0-9.]*' | grep -o '[0-9.]*')

        log_info "✅ Crawl completed successfully!"
        echo ""
        log_stat "Listings Scraped" "$listings_scraped"
        log_stat "New Attributes Found" "$new_attributes"
        log_stat "Processing Time" "${processing_time}ms"
        log_stat "Total Duration" "${duration}s"
        echo ""

        # Show sample listings
        log_info "Sample Listings:"
        echo "$response" | grep -A 200 '"sample_listings"' | head -20

        return 0
    else
        log_error "Crawl failed for $site"
        return 1
    fi
}

# =============================================================================
# Master Data Review
# =============================================================================

show_master_data_status() {
    log_section "Master Data Status"

    # Get pending items
    local pending_response=$(curl -sf "$EXTRACTION_SERVICE_URL/admin/pending-items?status=pending&limit=20")

    if [ $? -eq 0 ]; then
        local total_pending=$(echo "$pending_response" | grep -o '"total_count":[0-9]*' | grep -o '[0-9]*')
        local high_frequency=$(echo "$pending_response" | grep -o '"high_frequency_items":[0-9]*' | grep -o '[0-9]*')

        log_stat "Total Pending Items" "$total_pending"
        log_stat "High Frequency Items" "$high_frequency (priority review)"
        echo ""

        if [ "$total_pending" -gt 0 ]; then
            log_info "Top Pending Items (by frequency):"
            echo "$pending_response" | grep -A 100 '"pending_items"' | grep -E 'value_english|frequency|suggested_table' | head -30
        fi
    else
        log_warning "Could not retrieve pending items"
    fi
}

show_master_data_growth() {
    log_section "Master Data Growth"

    # Query master data tables
    tables=("districts" "amenities" "property_types" "view_types")

    for table in "${tables[@]}"; do
        # You would need to connect to PostgreSQL here
        # For now, just show a placeholder
        log_info "Table: $table"
    done

    log_info "Use Grafana dashboard for detailed growth visualization:"
    log_info "http://localhost:3001/d/master-data-growth"
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    echo "======================================================================="
    echo "  🌐 Real Estate Data Crawler - Master Data Builder"
    echo "======================================================================="
    echo ""
    echo "  This script will crawl real estate websites and automatically"
    echo "  discover new master data (amenities, features, locations, etc.)"
    echo ""
    echo "  Settings:"
    echo "  ├─ Sites: ${SITES[@]}"
    echo "  ├─ Max Pages: $MAX_PAGES per site"
    echo "  └─ Auto-Populate: Enabled"
    echo ""
    echo "======================================================================="
    echo ""

    # Pre-flight checks
    check_services

    # Crawl each site
    total_listings=0
    total_new_attributes=0
    successful_crawls=0

    for site in "${SITES[@]}"; do
        if crawl_site "$site" "$MAX_PAGES"; then
            successful_crawls=$((successful_crawls + 1))
        fi

        # Wait between sites to avoid rate limiting
        log_info "Waiting 10 seconds before next crawl..."
        sleep 10
    done

    # Show results
    echo ""
    log_section "Crawl Summary"
    log_stat "Sites Crawled" "$successful_crawls/${#SITES[@]}"
    echo ""

    # Show master data status
    show_master_data_status

    # Next steps
    echo ""
    log_section "Next Steps"
    echo ""
    log_info "1. Review pending master data items:"
    echo "   curl http://localhost:$EXTRACTION_SERVICE_URL/admin/pending-items?status=pending"
    echo ""
    log_info "2. Approve high-frequency items (admin only):"
    echo "   curl -X POST http://localhost:$EXTRACTION_SERVICE_URL/admin/approve-item \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"pending_id\": 1, \"translations\": {...}, \"admin_user_id\": \"admin\"}'"
    echo ""
    log_info "3. View master data growth in Grafana:"
    echo "   http://localhost:3001/d/master-data-growth"
    echo ""
    log_info "4. Run extraction test with new master data:"
    echo "   curl -X POST http://localhost:$EXTRACTION_SERVICE_URL/extract-with-master-data \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"text\": \"Căn hộ 2PN Quận 1 có hồ bơi\"}'"
    echo ""

    echo "======================================================================="
    echo "  ✅ Crawl completed!"
    echo "======================================================================="
}

# Run main function
main "$@"
