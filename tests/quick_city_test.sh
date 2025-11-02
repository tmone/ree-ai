#!/bin/bash
# Quick City Filtering Test Script

echo "🧪 Quick City Filtering Tests"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

DB_GATEWAY="http://localhost:8081"
ORCHESTRATOR="http://localhost:8090"

test_count=0
pass_count=0
fail_count=0

test_db_city() {
    local city=$1
    local expected_city=$2
    local test_name=$3

    echo -n "Testing: $test_name ... "

    response=$(curl -s -X POST "$DB_GATEWAY/search" \
        -H "Content-Type: application/json" \
        -d "{\"query\":\"căn hộ\",\"filters\":{\"city\":\"$city\"},\"limit\":10}")

    total=$(echo "$response" | jq -r '.total')

    if [ "$total" = "null" ] || [ "$total" = "0" ]; then
        echo -e "${RED}FAIL${NC} - No results found"
        ((fail_count++))
        return 1
    fi

    # Check if all results are from correct city
    wrong_count=$(echo "$response" | jq -r ".results[] | select(.city != \"$expected_city\") | .city" | wc -l)

    if [ "$wrong_count" -gt 0 ]; then
        echo -e "${RED}FAIL${NC} - Found $wrong_count results from wrong cities"
        echo "$response" | jq -r ".results[] | select(.city != \"$expected_city\") | \"  Wrong: \\(.city) - \\(.district)\""
        ((fail_count++))
        return 1
    fi

    echo -e "${GREEN}PASS${NC} - $total results, all from $expected_city"
    ((pass_count++))
    return 0
}

test_city_district() {
    local city=$1
    local district=$2
    local test_name=$3

    echo -n "Testing: $test_name ... "

    response=$(curl -s -X POST "$DB_GATEWAY/search" \
        -H "Content-Type: application/json" \
        -d "{\"query\":\"căn hộ\",\"filters\":{\"city\":\"$city\",\"district\":\"$district\"},\"limit\":10}")

    total=$(echo "$response" | jq -r '.total')

    if [ "$total" = "null" ] || [ "$total" = "0" ]; then
        echo -e "${YELLOW}SKIP${NC} - No data for this combination"
        return 0
    fi

    # Check if all results match both city and district
    mismatch=$(echo "$response" | jq -r ".results[] | select(.city != \"$city\" or .district != \"$district\") | .title" | wc -l)

    if [ "$mismatch" -gt 0 ]; then
        echo -e "${RED}FAIL${NC} - Found $mismatch mismatches"
        ((fail_count++))
        return 1
    fi

    echo -e "${GREEN}PASS${NC} - $total results, all match $city/$district"
    ((pass_count++))
    return 0
}

echo "📍 Test Suite 1: Basic City Filters"
echo "-----------------------------------"
((test_count++))
test_db_city "Hồ Chí Minh" "Hồ Chí Minh" "DB Gateway - Hồ Chí Minh"

((test_count++))
test_db_city "Hà Nội" "Hà Nội" "DB Gateway - Hà Nội"

((test_count++))
test_db_city "Đà Nẵng" "Đà Nẵng" "DB Gateway - Đà Nẵng"

((test_count++))
test_db_city "Bình Dương" "Bình Dương" "DB Gateway - Bình Dương"

echo ""
echo "📍 Test Suite 2: City + District"
echo "-----------------------------------"

((test_count++))
test_city_district "Hồ Chí Minh" "Quận 7" "HCM - Quận 7"

((test_count++))
test_city_district "Hồ Chí Minh" "Thủ Đức" "HCM - Thủ Đức"

((test_count++))
test_city_district "Hà Nội" "Hoàng Mai" "Hanoi - Hoàng Mai"

echo ""
echo "📍 Test Suite 3: Case Variations"
echo "-----------------------------------"

((test_count++))
echo -n "Testing: Lowercase city ... "
response=$(curl -s -X POST "$DB_GATEWAY/search" \
    -H "Content-Type: application/json" \
    -d '{"query":"căn hộ","filters":{"city":"hồ chí minh"},"limit":5}')

total=$(echo "$response" | jq -r '.total')
if [ "$total" = "0" ] || [ "$total" = "null" ]; then
    echo -e "${RED}FAIL${NC} - Case sensitivity issue! Lowercase not working"
    ((fail_count++))
else
    echo -e "${GREEN}PASS${NC} - $total results (case-insensitive working)"
    ((pass_count++))
fi

# Summary
echo ""
echo "=============================="
echo "📊 SUMMARY"
echo "=============================="
echo "Total Tests: $test_count"
echo -e "✅ Passed: ${GREEN}$pass_count${NC}"
echo -e "❌ Failed: ${RED}$fail_count${NC}"

if [ $fail_count -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "\n${RED}🚨 SOME TESTS FAILED${NC}"
    exit 1
fi
