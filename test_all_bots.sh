#!/bin/bash
# Test all bots multiple times

BOTS=("aggressive" "reactive" "coin_collector")
RUNS=10
DURATION=20

echo "Testing all bots - $RUNS runs each, $DURATION second duration"
echo "================================================================"
echo ""

for bot in "${BOTS[@]}"; do
    echo "Testing $bot bot ($RUNS runs)..."
    passed=0
    failed=0
    total_score=0
    total_time=0

    for i in $(seq 1 $RUNS); do
        echo -n "  Run $i/$RUNS... "

        output=$(python3 src/main.py --bot $bot --headless --test-duration $DURATION 2>&1)
        exit_code=$?

        if [ $exit_code -eq 0 ]; then
            ((passed++))
            score=$(echo "$output" | grep "Score:" | awk '{print $3}')
            total_score=$((total_score + score))
            echo "✓ PASSED (score: $score)"
        else
            ((failed++))
            time=$(echo "$output" | grep "died after" | awk '{print $5}')
            reason=$(echo "$output" | grep "Collision reason:" | cut -d: -f2)
            echo "✗ FAILED (${time}s, $reason)"
        fi
    done

    echo ""
    echo "Results for $bot:"
    echo "  Passed: $passed/$RUNS ($(( passed * 100 / RUNS ))%)"
    echo "  Failed: $failed/$RUNS"
    if [ $passed -gt 0 ]; then
        avg_score=$((total_score / passed))
        echo "  Avg score: $avg_score"
    fi
    echo ""
done
