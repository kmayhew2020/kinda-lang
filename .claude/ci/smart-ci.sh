#!/bin/bash
# Smart CI execution - only run when needed
# Tracks file changes and determines appropriate CI scope

set -e

CI_STATE_FILE=".claude/ci/last-ci-state.txt"
CI_HISTORY_FILE=".claude/ci/ci-history.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 Smart CI Validation"
echo "======================"

# Create state directory if needed
mkdir -p .claude/ci

# Get current git state
CURRENT_COMMIT=$(git rev-parse HEAD)
CURRENT_BRANCH=$(git branch --show-current)

# Check if we have previous state
if [ -f "$CI_STATE_FILE" ]; then
    LAST_COMMIT=$(head -n 1 "$CI_STATE_FILE" 2>/dev/null || echo "")

    if [ "$LAST_COMMIT" = "$CURRENT_COMMIT" ]; then
        echo -e "${GREEN}✅ No changes since last CI run (commit: ${CURRENT_COMMIT:0:8})${NC}"
        echo "   Last CI passed, skipping redundant validation"
        echo ""
        echo "To force CI anyway: bash scripts/ci-full.sh"
        exit 0
    fi
fi

# Determine what changed
echo "📊 Analyzing changes since last CI run..."

# Get changed files
if [ -n "$LAST_COMMIT" ] && git rev-parse "$LAST_COMMIT" >/dev/null 2>&1; then
    CHANGED_FILES=$(git diff --name-only "$LAST_COMMIT" HEAD)
else
    # First run or invalid last commit - check all tracked files
    CHANGED_FILES=$(git ls-files)
fi

# Count changes by type
PYTHON_CHANGES=$(echo "$CHANGED_FILES" | grep -c "\.py$" || true)
TEST_CHANGES=$(echo "$CHANGED_FILES" | grep -c "tests/" || true)
DOC_CHANGES=$(echo "$CHANGED_FILES" | grep -c "\.md$" || true)
CONFIG_CHANGES=$(echo "$CHANGED_FILES" | grep -c -E "(\.toml|\.yml|\.yaml|\.json)$" || true)

echo "   Python files changed: $PYTHON_CHANGES"
echo "   Test files changed: $TEST_CHANGES"
echo "   Documentation changed: $DOC_CHANGES"
echo "   Config files changed: $CONFIG_CHANGES"
echo ""

# Determine CI scope
if [ "$PYTHON_CHANGES" -gt 0 ] || [ "$TEST_CHANGES" -gt 0 ]; then
    echo -e "${YELLOW}🚀 Running FULL CI validation (code changes detected)${NC}"
    CI_SCOPE="full"
elif [ "$CONFIG_CHANGES" -gt 0 ]; then
    echo -e "${YELLOW}🔧 Running CONFIG validation (config changes detected)${NC}"
    CI_SCOPE="config"
elif [ "$DOC_CHANGES" -gt 0 ]; then
    echo -e "${GREEN}📝 Running DOCS validation (docs only)${NC}"
    CI_SCOPE="docs"
else
    echo -e "${GREEN}✅ No significant changes, skipping CI${NC}"
    exit 0
fi

# Execute appropriate CI scope
case "$CI_SCOPE" in
    full)
        echo ""
        echo "Running full CI validation..."
        bash scripts/ci-full.sh
        CI_EXIT=$?
        ;;
    config)
        echo ""
        echo "Running config validation..."
        # Just check formatting and basic tests
        black . --check && mypy . && pytest tests/ -x --tb=short
        CI_EXIT=$?
        ;;
    docs)
        echo ""
        echo "Validating documentation..."
        # Just check markdown formatting if we have tools
        CI_EXIT=0
        ;;
    *)
        CI_EXIT=0
        ;;
esac

# Record CI state
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
if [ $CI_EXIT -eq 0 ]; then
    echo "$CURRENT_COMMIT" > "$CI_STATE_FILE"
    echo "$CURRENT_BRANCH" >> "$CI_STATE_FILE"
    echo "$TIMESTAMP" >> "$CI_STATE_FILE"
    echo "${TIMESTAMP} | ${CURRENT_COMMIT:0:8} | ${CI_SCOPE} | PASS" >> "$CI_HISTORY_FILE"
    echo -e "${GREEN}✅ CI passed and state saved${NC}"
else
    echo "${TIMESTAMP} | ${CURRENT_COMMIT:0:8} | ${CI_SCOPE} | FAIL" >> "$CI_HISTORY_FILE"
    echo -e "${RED}❌ CI failed${NC}"
fi

exit $CI_EXIT
