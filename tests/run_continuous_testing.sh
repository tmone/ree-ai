#!/bin/bash

###############################################################################
# Continuous Testing Loop - REE AI Orchestrator
# Runs tests continuously, logs results, monitors for new bugs
###############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LOG_DIR="./test_logs"
ITERATION=0
START_TIME=$(date +%s)

# Create log directory
mkdir -p $LOG_DIR

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     CONTINUOUS TESTING SYSTEM - REE AI ORCHESTRATOR           ║${NC}"
echo -e "${BLUE}║     Running infinite test loop until stopped...               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}[INFO]${NC} Test logs will be saved to: $LOG_DIR"
echo -e "${GREEN}[INFO]${NC} Press Ctrl+C to stop"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}[STOP]${NC} Continuous testing stopped by user"
    TOTAL_TIME=$(($(date +%s) - START_TIME))
    HOURS=$((TOTAL_TIME / 3600))
    MINS=$(((TOTAL_TIME % 3600) / 60))
    echo -e "${GREEN}[INFO]${NC} Total iterations: $ITERATION"
    echo -e "${GREEN}[INFO]${NC} Total runtime: ${HOURS}h ${MINS}m"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Main loop
while true; do
    ITERATION=$((ITERATION + 1))
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    LOG_FILE="$LOG_DIR/test_iteration_${ITERATION}_${TIMESTAMP}.log"

    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  ITERATION #${ITERATION} - $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

    # Run quick test for fast feedback
    echo -e "${GREEN}[TEST 1/4]${NC} Running Quick Test..."
    python3 tests/quick_continuous_test.py > "$LOG_FILE.quick" 2>&1
    QUICK_EXIT=$?

    if [ $QUICK_EXIT -eq 0 ]; then
        # Check for bugs in output
        BUGS=$(grep "🐛" "$LOG_FILE.quick" | wc -l | tr -d ' ')
        if [ "$BUGS" -gt 0 ]; then
            echo -e "  ${RED}✗ Found $BUGS bugs!${NC}"
            # Alert to main log
            echo "[$(date)] ITERATION $ITERATION: Found $BUGS bugs in quick test" >> "$LOG_DIR/bug_alerts.log"
        else
            echo -e "  ${GREEN}✓ All tests passed${NC}"
        fi
    else
        echo -e "  ${RED}✗ Test failed with exit code $QUICK_EXIT${NC}"
    fi

    # Run scenario tests (rotating scenarios to avoid overwhelming)
    SCENARIOS=("real_estate_search" "ambiguous_queries" "conversational" "multilingual" "edge_cases")
    SCENARIO_INDEX=$((ITERATION % ${#SCENARIOS[@]}))
    SCENARIO=${SCENARIOS[$SCENARIO_INDEX]}

    echo -e "${GREEN}[TEST 2/4]${NC} Running Scenario: $SCENARIO..."
    python3 tests/continuous_test_scenarios.py --scenarios $SCENARIO > "$LOG_FILE.scenario" 2>&1

    # Performance check
    echo -e "${GREEN}[TEST 3/4]${NC} Performance Check..."
    SLOW_QUERIES=$(grep "SLOW:" "$LOG_FILE.quick" "$LOG_FILE.scenario" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$SLOW_QUERIES" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠ Found $SLOW_QUERIES slow queries (>10s)${NC}"
    else
        echo -e "  ${GREEN}✓ All queries under threshold${NC}"
    fi

    # Health check
    echo -e "${GREEN}[TEST 4/4]${NC} Service Health Check..."
    HEALTH=$(curl -s http://localhost:8090/health 2>/dev/null)
    if echo "$HEALTH" | grep -q "healthy"; then
        echo -e "  ${GREEN}✓ Service is healthy${NC}"
    else
        echo -e "  ${RED}✗ Service health check failed!${NC}"
        echo "[$(date)] ITERATION $ITERATION: Service health check failed!" >> "$LOG_DIR/bug_alerts.log"
    fi

    # Summary
    TOTAL_BUGS=$(grep -r "🐛" "$LOG_FILE."* 2>/dev/null | wc -l | tr -d ' ')
    echo ""
    echo -e "${BLUE}[SUMMARY]${NC} Iteration #$ITERATION Complete"
    echo -e "  - Total bugs detected: $TOTAL_BUGS"
    echo -e "  - Slow queries: $SLOW_QUERIES"
    echo -e "  - Logs: $LOG_FILE.*"

    # Aggregate stats
    echo "$ITERATION,$TOTAL_BUGS,$SLOW_QUERIES,$(date +%s)" >> "$LOG_DIR/stats.csv"

    # Wait before next iteration (5 minutes)
    echo ""
    echo -e "${YELLOW}[WAIT]${NC} Waiting 5 minutes before next iteration..."
    echo -e "${YELLOW}[INFO]${NC} Next iteration: #$((ITERATION + 1)) at $(date -v+5M '+%H:%M:%S' 2>/dev/null || date -d '+5 minutes' '+%H:%M:%S' 2>/dev/null || echo 'in 5 minutes')"

    sleep 300  # 5 minutes
done
