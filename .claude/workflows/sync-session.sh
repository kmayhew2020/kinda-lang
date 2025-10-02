#!/bin/bash
# Portable session sync - ensures all Claude Code sessions use same infrastructure
# Run this at the start of any new session to pull latest workflow improvements

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔄 Syncing Claude Code Session Infrastructure${NC}"
echo "══════════════════════════════════════════════════"

# 1. Ensure we're in the right repo
CURRENT_REPO=$(git remote get-url origin 2>/dev/null || echo "NO_ORIGIN")
if [[ ! "$CURRENT_REPO" =~ "kinda-lang-dev/kinda-lang" ]]; then
    echo -e "${RED}❌ ERROR: Not in kinda-lang fork repository${NC}"
    echo "   Current: $CURRENT_REPO"
    echo "   Expected: kinda-lang-dev/kinda-lang"
    exit 1
fi

echo -e "${GREEN}✅ Repository: kinda-lang-dev/kinda-lang (fork)${NC}"

# 2. Check if .claude/ directory exists
if [ ! -d ".claude" ]; then
    echo -e "${RED}❌ ERROR: .claude/ directory not found${NC}"
    echo "   This session may be using an old version of the repo"
    echo "   Pull latest changes: git pull origin dev"
    exit 1
fi

echo -e "${GREEN}✅ .claude/ infrastructure present${NC}"

# 3. Pull latest .claude/ infrastructure from dev
echo ""
echo "Fetching latest workflow infrastructure..."

CURRENT_BRANCH=$(git branch --show-current)

# Fetch latest dev
git fetch origin dev --quiet

# Check if .claude/ has updates on dev
if git diff origin/dev -- .claude/ | grep -q "diff"; then
    echo -e "${YELLOW}📥 Updates available in .claude/ infrastructure${NC}"
    echo ""
    echo "Changes detected:"
    git diff origin/dev --stat -- .claude/ | head -10
    echo ""
    read -p "Pull latest .claude/ updates? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Cherry-pick .claude/ directory from dev
        git checkout origin/dev -- .claude/
        echo -e "${GREEN}✅ Infrastructure updated from dev${NC}"
        echo ""
        echo "Updated files:"
        git status --short | grep ".claude/"
    else
        echo -e "${YELLOW}⚠️  Skipped infrastructure updates${NC}"
    fi
else
    echo -e "${GREEN}✅ Infrastructure is up to date${NC}"
fi

# 4. Verify all required infrastructure exists
echo ""
echo "Verifying infrastructure components..."

REQUIRED_FILES=(
    ".claude/preflight/validate.sh"
    ".claude/status/update-status.sh"
    ".claude/status/show-workflow.sh"
    ".claude/ci/smart-ci.sh"
    ".claude/sessions/session-manager.sh"
    ".claude/workflows/sync-session.sh"
    ".claude/agents/kinda-pm.md"
    ".claude/agents/kinda-architect.md"
    ".claude/agents/kinda-coder.md"
    ".claude/agents/kinda-tester.md"
    ".claude/agents/kinda-pr-reviewer.md"
)

MISSING_COUNT=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Missing: $file${NC}"
        MISSING_COUNT=$((MISSING_COUNT + 1))
    fi
done

if [ $MISSING_COUNT -gt 0 ]; then
    echo -e "${RED}❌ $MISSING_COUNT required files missing${NC}"
    echo "   Pull from dev: git checkout origin/dev -- .claude/"
    exit 1
fi

echo -e "${GREEN}✅ All infrastructure components present ($((${#REQUIRED_FILES[@]} - MISSING_COUNT))/${#REQUIRED_FILES[@]})${NC}"

# 5. Make scripts executable
echo ""
echo "Setting executable permissions..."
chmod +x .claude/preflight/validate.sh
chmod +x .claude/status/update-status.sh
chmod +x .claude/status/show-workflow.sh
chmod +x .claude/ci/smart-ci.sh
chmod +x .claude/sessions/session-manager.sh
chmod +x .claude/workflows/sync-session.sh
echo -e "${GREEN}✅ Permissions updated${NC}"

# 6. Run pre-flight validation
echo ""
echo "Running pre-flight validation..."
bash .claude/preflight/validate.sh

# 7. Summary
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Session infrastructure synchronized and ready${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo "Available tools:"
echo "  📝 Pre-flight check:    bash .claude/preflight/validate.sh"
echo "  📊 Show workflow:       bash .claude/status/show-workflow.sh <agent>"
echo "  🎯 Update status:       bash .claude/status/update-status.sh <agent> <issue> <status>"
echo "  🚀 Smart CI:            bash .claude/ci/smart-ci.sh"
echo "  💾 Session manager:     bash .claude/sessions/session-manager.sh <cmd>"
echo ""
echo "Next steps:"
echo "  1. Review CLAUDE.md for fork/release workflow"
echo "  2. Run pre-flight validation before any work"
echo "  3. Check agent profile in .claude/agents/"
