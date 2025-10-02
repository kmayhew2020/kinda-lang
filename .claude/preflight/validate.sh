#!/bin/bash
# Pre-flight validation - call before any agent work
# Ensures correct repository setup and prevents common mistakes

set -e

echo "🚦 Pre-flight Validation"
echo "========================"

# 1. Verify we're in the right repo (fork, not upstream)
CURRENT_REPO=$(git remote get-url origin 2>/dev/null || echo "NO_ORIGIN")
EXPECTED_REPO="kinda-lang-dev/kinda-lang"
if [[ ! "$CURRENT_REPO" =~ "$EXPECTED_REPO" ]]; then
    echo "❌ WRONG REPO: $CURRENT_REPO"
    echo "   Expected fork: $EXPECTED_REPO"
    echo "   Fix: git remote set-url origin https://github.com/kinda-lang-dev/kinda-lang.git"
    exit 1
fi
echo "✅ Correct repo: $EXPECTED_REPO"

# 2. Verify remotes are set up correctly
UPSTREAM=$(git remote get-url upstream 2>/dev/null || echo "NOT_SET")
if [[ "$UPSTREAM" != *"kmayhew2020/kinda-lang"* ]]; then
    echo "⚠️  Upstream not configured (should be kmayhew2020/kinda-lang for releases)"
    echo "   Fix: git remote add upstream https://github.com/kmayhew2020/kinda-lang.git"
else
    echo "✅ Upstream configured: kmayhew2020/kinda-lang"
fi

# 3. Check current branch - warn if on release branch
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" =~ ^release/ ]]; then
    echo "⚠️  WARNING: On release branch '$BRANCH'"
    echo "   Release branches should only be used by PM for version releases"
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo "📍 Current branch: $BRANCH"

# 4. Check for uncommitted changes
UNCOMMITTED=$(git status -s)
if [[ -n "$UNCOMMITTED" ]]; then
    echo "⚠️  Uncommitted changes present:"
    git status -s | head -10
fi

# 5. Verify scripts/ci-full.sh exists
if [[ ! -f "scripts/ci-full.sh" ]]; then
    echo "❌ Local CI script missing: scripts/ci-full.sh"
    echo "   This is required for local CI validation"
    exit 1
fi
echo "✅ Local CI script found"

# 6. Check for prohibited files (status reports)
PROHIBITED=$(find . -name "*_REPORT.md" -o -name "*_SUMMARY.md" -o -name "*_ANALYSIS.md" 2>/dev/null | grep -v node_modules | grep -v ".git" | head -5)
if [[ -n "$PROHIBITED" ]]; then
    echo "❌ POLICY VIOLATION: Prohibited .md files found:"
    echo "$PROHIBITED"
    echo "   Remove these files - status updates go in GitHub issues, not .md files"
    exit 1
fi
echo "✅ No prohibited status .md files"

# 7. Check if accidentally working with upstream for non-release work
CURRENT_PR_REPO=$(gh pr list --head "$BRANCH" --json headRepository --jq '.[0].headRepository.owner.login' 2>/dev/null || echo "")
if [[ "$CURRENT_PR_REPO" == "kmayhew2020" ]] && [[ ! "$BRANCH" =~ ^release/ ]]; then
    echo "❌ POLICY VIOLATION: Found PR on upstream repo for non-release branch"
    echo "   Branch: $BRANCH"
    echo "   Feature/bugfix PRs should only be on fork (kinda-lang-dev)"
    echo "   Close the upstream PR and create it on the fork instead"
    exit 1
fi

echo ""
echo "✅ All pre-flight checks passed"
echo "   Safe to proceed with agent work"
exit 0
