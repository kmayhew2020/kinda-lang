#!/bin/bash
# Visual status update script
# Updates current workflow status with visual indicators

set -e

AGENT_ROLE="${1:-unknown}"
ISSUE_NUMBER="${2:-}"
STATUS="${3:-}"

STATUS_FILE=".claude/status/current.txt"
HISTORY_FILE=".claude/status/history.log"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Status emojis
EMOJI_PLANNING="📋"
EMOJI_DESIGNING="🏗️"
EMOJI_CODING="💻"
EMOJI_TESTING="🧪"
EMOJI_REVIEWING="👀"
EMOJI_MERGING="🔀"
EMOJI_COMPLETE="✅"
EMOJI_BLOCKED="🚫"

get_emoji() {
    case "$1" in
        pm*) echo "$EMOJI_PLANNING" ;;
        architect*) echo "$EMOJI_DESIGNING" ;;
        coder*) echo "$EMOJI_CODING" ;;
        tester*) echo "$EMOJI_TESTING" ;;
        reviewer*) echo "$EMOJI_REVIEWING" ;;
        merge*) echo "$EMOJI_MERGING" ;;
        complete*) echo "$EMOJI_COMPLETE" ;;
        blocked*) echo "$EMOJI_BLOCKED" ;;
        *) echo "❓" ;;
    esac
}

get_status_color() {
    case "$1" in
        *complete*|*approved*|*pass*) echo "$GREEN" ;;
        *blocked*|*fail*|*reject*) echo "$RED" ;;
        *progress*|*working*) echo "$YELLOW" ;;
        *) echo "$BLUE" ;;
    esac
}

# Update current status
if [ -n "$ISSUE_NUMBER" ] && [ -n "$STATUS" ]; then
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    EMOJI=$(get_emoji "$AGENT_ROLE")
    COLOR=$(get_status_color "$STATUS")

    # Write to current status
    cat > "$STATUS_FILE" <<EOF
╔════════════════════════════════════════════════════════════════╗
║                    KINDA-LANG WORKFLOW STATUS                  ║
╚════════════════════════════════════════════════════════════════╝

  Issue: #${ISSUE_NUMBER}
  Agent: ${EMOJI} ${AGENT_ROLE^^}
  Status: ${STATUS}
  Updated: ${TIMESTAMP}

EOF

    # Append to history
    echo "${TIMESTAMP} | ${EMOJI} ${AGENT_ROLE} | #${ISSUE_NUMBER} | ${STATUS}" >> "$HISTORY_FILE"

    # Display with colors
    echo -e "${COLOR}"
    cat "$STATUS_FILE"
    echo -e "${NC}"
fi

# Show current status if no args
if [ -z "$ISSUE_NUMBER" ]; then
    if [ -f "$STATUS_FILE" ]; then
        cat "$STATUS_FILE"
    else
        echo "No current workflow status. Use: $0 <agent> <issue#> <status>"
    fi
fi
