#!/bin/bash
# Show current workflow position in 5-agent pipeline

CURRENT_AGENT="${1:-}"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              KINDA-LANG 5-AGENT WORKFLOW PIPELINE             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

show_stage() {
    local stage_name="$1"
    local stage_agent="$2"
    local is_current="$3"

    if [ "$is_current" = "true" ]; then
        echo -e "  ▶ \033[1;32m${stage_name}\033[0m  ← \033[1;33mYOU ARE HERE\033[0m"
    else
        echo "    ${stage_name}"
    fi
}

# Determine current stage
case "${CURRENT_AGENT,,}" in
    *pm*|*manager*)
        show_stage "📋 PM: Requirements & Assignment" "pm" "true"
        show_stage "🏗️  Architect: Design & Specs" "architect" "false"
        show_stage "💻 Coder: Implementation" "coder" "false"
        show_stage "🧪 Tester: Quality Validation" "tester" "false"
        show_stage "👀 Reviewer: PR Review" "reviewer" "false"
        show_stage "🔀 PM: Merge to dev" "pm" "false"
        ;;
    *architect*)
        show_stage "📋 PM: Requirements & Assignment" "pm" "false"
        show_stage "🏗️  Architect: Design & Specs" "architect" "true"
        show_stage "💻 Coder: Implementation" "coder" "false"
        show_stage "🧪 Tester: Quality Validation" "tester" "false"
        show_stage "👀 Reviewer: PR Review" "reviewer" "false"
        show_stage "🔀 PM: Merge to dev" "pm" "false"
        ;;
    *coder*)
        show_stage "📋 PM: Requirements & Assignment" "pm" "false"
        show_stage "🏗️  Architect: Design & Specs" "architect" "false"
        show_stage "💻 Coder: Implementation" "coder" "true"
        show_stage "🧪 Tester: Quality Validation" "tester" "false"
        show_stage "👀 Reviewer: PR Review" "reviewer" "false"
        show_stage "🔀 PM: Merge to dev" "pm" "false"
        ;;
    *tester*|*test*)
        show_stage "📋 PM: Requirements & Assignment" "pm" "false"
        show_stage "🏗️  Architect: Design & Specs" "architect" "false"
        show_stage "💻 Coder: Implementation" "coder" "false"
        show_stage "🧪 Tester: Quality Validation" "tester" "true"
        show_stage "👀 Reviewer: PR Review" "reviewer" "false"
        show_stage "🔀 PM: Merge to dev" "pm" "false"
        ;;
    *review*)
        show_stage "📋 PM: Requirements & Assignment" "pm" "false"
        show_stage "🏗️  Architect: Design & Specs" "architect" "false"
        show_stage "💻 Coder: Implementation" "coder" "false"
        show_stage "🧪 Tester: Quality Validation" "tester" "false"
        show_stage "👀 Reviewer: PR Review" "reviewer" "true"
        show_stage "🔀 PM: Merge to dev" "pm" "false"
        ;;
    *)
        # Show all stages without highlighting
        show_stage "📋 PM: Requirements & Assignment" "pm" "false"
        show_stage "🏗️  Architect: Design & Specs" "architect" "false"
        show_stage "💻 Coder: Implementation" "coder" "false"
        show_stage "🧪 Tester: Quality Validation" "tester" "false"
        show_stage "👀 Reviewer: PR Review" "reviewer" "false"
        show_stage "🔀 PM: Merge to dev" "pm" "false"
        ;;
esac

echo ""
echo "Usage: $0 <agent-role>"
echo "Example: $0 coder"
