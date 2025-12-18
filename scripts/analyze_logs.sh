#!/bin/bash
# analyze_logs.sh - Analyze MyFinGPT log files

# Default to today's date
DATE=${1:-$(date +%Y-%m-%d)}
LOG_DIR=${LOG_DIR:-./logs}

echo "=== MyFinGPT Log Analysis for ${DATE} ==="
echo "Log directory: ${LOG_DIR}"
echo ""

# Check if log files exist
if [ ! -f "${LOG_DIR}/myfingpt_${DATE}.log" ]; then
    echo "Error: Log file not found: ${LOG_DIR}/myfingpt_${DATE}.log"
    exit 1
fi

MAIN_LOG="${LOG_DIR}/myfingpt_${DATE}.log"
ERROR_LOG="${LOG_DIR}/myfingpt_errors_${DATE}.log"

echo "=== Summary Statistics ==="
echo "Total log entries: $(wc -l < ${MAIN_LOG} 2>/dev/null || echo 0)"
echo "Error entries: $(grep -c "ERROR" ${MAIN_LOG} 2>/dev/null || echo 0)"
echo "Warning entries: $(grep -c "WARNING" ${MAIN_LOG} 2>/dev/null || echo 0)"
echo ""

echo "=== Component Activity ==="
for component in "[UI]" "[WORKFLOW]" "[GRAPH]" "Research Agent" "Analyst Agent" "Reporting Agent" "[MCP:" "[VectorDB]"; do
    count=$(grep -c "$component" ${MAIN_LOG} 2>/dev/null || echo 0)
    if [ $count -gt 0 ]; then
        echo "$component: $count entries"
    fi
done
echo ""

echo "=== Recent Errors (last 10) ==="
if [ -f "${ERROR_LOG}" ]; then
    tail -10 "${ERROR_LOG}"
else
    grep "ERROR" ${MAIN_LOG} | tail -10
fi
echo ""

echo "=== Performance Metrics ==="
echo "Average execution times:"
grep "Completed in" ${MAIN_LOG} 2>/dev/null | \
    grep -oP 'Completed in \K[0-9.]+' | \
    awk '{sum+=$1; count++} END {if(count>0) printf "  Average: %.2fs (from %d operations)\n", sum/count, count}'

echo ""
echo "Token usage:"
grep "Total tokens:" ${MAIN_LOG} 2>/dev/null | \
    grep -oP 'Total tokens: \K[0-9]+' | \
    awk '{sum+=$1; count++; max=$1>max?$1:max} END {if(count>0) printf "  Average: %.0f tokens\n  Max: %d tokens\n  Total queries: %d\n", sum/count, max, count}'

echo ""
echo "=== Query Processing ==="
query_count=$(grep -c "Processing query" ${MAIN_LOG} 2>/dev/null || echo 0)
success_count=$(grep -c "Query processing completed successfully" ${MAIN_LOG} 2>/dev/null || echo 0)
if [ $query_count -gt 0 ]; then
    success_rate=$(echo "scale=1; $success_count * 100 / $query_count" | bc)
    echo "Total queries: $query_count"
    echo "Successful: $success_count"
    echo "Success rate: ${success_rate}%"
fi
echo ""

echo "=== MCP API Performance ==="
mcp_calls=$(grep -c "Stock price fetched\|Error fetching" ${LOG_DIR}/mcp_${DATE}.log 2>/dev/null || echo 0)
if [ $mcp_calls -gt 0 ]; then
    echo "Total API calls: $mcp_calls"
    avg_time=$(grep "Time:" ${LOG_DIR}/mcp_${DATE}.log 2>/dev/null | \
        grep -oP 'Time: \K[0-9.]+' | \
        awk '{sum+=$1; count++} END {if(count>0) print sum/count}')
    if [ ! -z "$avg_time" ]; then
        echo "Average response time: ${avg_time}s"
    fi
fi
echo ""

echo "=== Log File Sizes ==="
ls -lh ${LOG_DIR}/*${DATE}*.log 2>/dev/null | awk '{print $9, $5}'
echo ""

echo "Analysis complete!"

