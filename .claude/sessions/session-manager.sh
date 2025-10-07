#!/bin/bash
# Agent session state manager
# Saves and restores agent context across sessions

set -e

SESSIONS_DIR=".claude/sessions"
mkdir -p "$SESSIONS_DIR"

COMMAND="${1:-}"
AGENT_ROLE="${2:-}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

get_session_file() {
    local agent="$1"
    echo "${SESSIONS_DIR}/${agent}-session.json"
}

save_session() {
    local agent="$1"
    local issue="$2"
    local pr="$3"
    local status="$4"
    local notes="$5"

    local session_file=$(get_session_file "$agent")
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local branch=$(git branch --show-current)
    local commit=$(git rev-parse HEAD)

    cat > "$session_file" <<EOF
{
  "agent": "$agent",
  "timestamp": "$timestamp",
  "branch": "$branch",
  "commit": "${commit:0:8}",
  "issue": "$issue",
  "pr": "$pr",
  "status": "$status",
  "notes": "$notes"
}
EOF

    echo -e "${GREEN}✅ Session saved for agent: $agent${NC}"
    echo "   Issue: #$issue"
    echo "   PR: #$pr"
    echo "   Status: $status"
    echo "   File: $session_file"
}

load_session() {
    local agent="$1"
    local session_file=$(get_session_file "$agent")

    if [ ! -f "$session_file" ]; then
        echo -e "${YELLOW}⚠️  No saved session found for agent: $agent${NC}"
        return 1
    fi

    echo -e "${BLUE}📖 Loading session for agent: $agent${NC}"
    echo "════════════════════════════════════════"
    cat "$session_file" | python3 -m json.tool 2>/dev/null || cat "$session_file"
    echo "════════════════════════════════════════"
}

list_sessions() {
    echo -e "${BLUE}📚 Active Agent Sessions${NC}"
    echo "════════════════════════════════════════"

    for session_file in "$SESSIONS_DIR"/*-session.json; do
        if [ -f "$session_file" ]; then
            local agent=$(basename "$session_file" | sed 's/-session.json//')
            echo ""
            echo "Agent: $agent"
            cat "$session_file" | python3 -m json.tool 2>/dev/null | grep -E "(timestamp|issue|pr|status)" | sed 's/^/  /'
        fi
    done

    echo ""
    echo "════════════════════════════════════════"
}

clear_session() {
    local agent="$1"
    local session_file=$(get_session_file "$agent")

    if [ -f "$session_file" ]; then
        rm "$session_file"
        echo -e "${GREEN}✅ Session cleared for agent: $agent${NC}"
    else
        echo -e "${YELLOW}⚠️  No session to clear for agent: $agent${NC}"
    fi
}

case "$COMMAND" in
    save)
        if [ -z "$AGENT_ROLE" ]; then
            echo "Usage: $0 save <agent> <issue#> <pr#> <status> [notes]"
            exit 1
        fi
        save_session "$2" "$3" "$4" "$5" "${6:-}"
        ;;
    load)
        if [ -z "$AGENT_ROLE" ]; then
            echo "Usage: $0 load <agent>"
            exit 1
        fi
        load_session "$AGENT_ROLE"
        ;;
    list)
        list_sessions
        ;;
    clear)
        if [ -z "$AGENT_ROLE" ]; then
            echo "Usage: $0 clear <agent>"
            exit 1
        fi
        clear_session "$AGENT_ROLE"
        ;;
    *)
        echo "Agent Session Manager"
        echo ""
        echo "Usage:"
        echo "  $0 save <agent> <issue#> <pr#> <status> [notes]"
        echo "  $0 load <agent>"
        echo "  $0 list"
        echo "  $0 clear <agent>"
        echo ""
        echo "Examples:"
        echo "  $0 save coder 106 142 'implementing fix' 'working on test_fuzzy_declaration'"
        echo "  $0 load coder"
        echo "  $0 list"
        echo "  $0 clear coder"
        ;;
esac
