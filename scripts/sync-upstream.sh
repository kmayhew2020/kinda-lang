#!/bin/bash
# Upstream Sync Script for Kinda-Lang Development
# Syncs fork with latest changes from upstream (main repo)

set -e

echo "🔄 Kinda-Lang Upstream Sync"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[SYNC]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "kinda" ]; then
    print_error "Please run this script from the kinda-lang project root"
    exit 1
fi

# Check if we have the upstream remote
if ! git remote | grep -q "upstream"; then
    print_error "Upstream remote not found. Run fork-setup.sh first."
    exit 1
fi

print_status "Syncing fork with upstream changes..."

# Save current branch
CURRENT_BRANCH=$(git branch --show-current)
print_status "Current branch: $CURRENT_BRANCH"

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    print_warning "You have uncommitted changes."
    print_status "Stashing changes temporarily..."
    git stash push -m "Upstream sync stash $(date)"
    STASHED=true
else
    STASHED=false
fi

# Fetch latest from upstream
print_status "Fetching latest from upstream..."
git fetch upstream
print_success "Upstream fetched"

# Sync main branch
print_status "Syncing main branch..."
git checkout main
git reset --hard upstream/main
git push origin main --force-with-lease
print_success "Main branch synced"

# Sync dev branch
print_status "Syncing dev branch..."
git checkout dev
git reset --hard upstream/dev
git push origin dev --force-with-lease
print_success "Dev branch synced"

# Return to original branch
if [ "$CURRENT_BRANCH" != "dev" ] && [ "$CURRENT_BRANCH" != "main" ]; then
    print_status "Returning to branch: $CURRENT_BRANCH"
    git checkout "$CURRENT_BRANCH"
    
    # Offer to rebase feature branch on updated dev
    if git show-branch | grep -q "$CURRENT_BRANCH"; then
        print_warning "Consider rebasing $CURRENT_BRANCH on updated dev:"
        print_status "  git rebase dev"
    fi
else
    git checkout dev  # Default to dev branch
fi

# Restore stashed changes if any
if [ "$STASHED" = true ]; then
    print_status "Restoring stashed changes..."
    git stash pop
    print_success "Stashed changes restored"
fi

echo "=========================="
print_success "🎉 Upstream sync complete!"
print_status "Fork is now up-to-date with upstream"
echo "=========================="

exit 0