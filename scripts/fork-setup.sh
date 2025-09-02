#!/bin/bash
# Fork Setup Script for Kinda-Lang Development
# Sets up local development environment to work with the fork

set -e

echo "🍴 Kinda-Lang Fork Development Setup"
echo "==================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[SETUP]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "kinda" ]; then
    print_error "Please run this script from the kinda-lang project root"
    exit 1
fi

print_status "Setting up fork-based development workflow..."

# Check current remotes
print_status "Current git remotes:"
git remote -v

# Add fork remote if it doesn't exist
if ! git remote | grep -q "fork"; then
    print_status "Adding fork remote..."
    git remote add fork https://github.com/kinda-lang-dev/kinda-lang.git
    print_success "Fork remote added"
else
    print_status "Fork remote already exists"
    git remote set-url fork https://github.com/kinda-lang-dev/kinda-lang.git
    print_success "Fork remote URL updated"
fi

# Rename origin to upstream for clarity
if git remote | grep -q "^origin$"; then
    print_status "Renaming origin to upstream..."
    git remote rename origin upstream
    print_success "Renamed origin -> upstream"
fi

# Set fork as the primary origin
if ! git remote | grep -q "^origin$"; then
    print_status "Setting fork as primary origin..."
    git remote add origin https://github.com/kinda-lang-dev/kinda-lang.git
    print_success "Fork set as origin"
fi

# Show final remote configuration
print_status "Final remote configuration:"
echo "  upstream: https://github.com/kmayhew2020/kinda-lang.git (protected repo)"
echo "  origin:   https://github.com/kinda-lang-dev/kinda-lang.git (fork, bot workspace)"
echo "  fork:     https://github.com/kinda-lang-dev/kinda-lang.git (alias for origin)"

# Fetch all remotes
print_status "Fetching from all remotes..."
git fetch --all
print_success "All remotes fetched"

# Set up branch tracking
print_status "Setting up branch tracking..."

# Make sure we're on dev branch and track upstream
git checkout dev 2>/dev/null || {
    print_status "Creating dev branch from upstream/dev..."
    git checkout -b dev upstream/dev
}

# Set dev to track upstream (for pulling updates) but push to fork
git branch --set-upstream-to=upstream/dev dev
print_success "Dev branch tracks upstream/dev for pulls"

print_status "Verifying setup..."
echo "  Current branch: $(git branch --show-current)"
echo "  Tracking: $(git config branch.dev.remote)/$(git config branch.dev.merge | sed 's|refs/heads/||')"
echo "  Push target: $(git config remote.origin.url)"

echo "==================================="
print_success "🎉 Fork development environment ready!"
print_status "Workflow:"
print_status "  • Pull updates: git pull (from upstream)"
print_status "  • Push changes: git push origin <branch> (to fork)"
print_status "  • Create PRs: fork/<branch> → upstream/dev"
echo "==================================="

exit 0