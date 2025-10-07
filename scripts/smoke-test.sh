#!/bin/bash
# Fast Smoke Tests for Kinda-Lang
# Quick validation before PR creation (runs in ~2-3 minutes)
# For full CI validation, use scripts/ci-full.sh (release only)

set -e  # Exit on any error

echo "🚀 Kinda-Lang Fast Smoke Tests"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${BLUE}[SMOKE]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

# Change to project root
cd "$(dirname "$0")/.."

START_TIME=$(date +%s)

# 1. Black formatting check (fast)
print_status "Checking code formatting..."
black --check --diff . || {
    print_error "Code formatting issues found. Run 'black .' to fix."
    exit 1
}
print_success "Code formatting OK"

# 2. MyPy type checking on core files only (fast)
print_status "Type checking core files..."
mypy kinda/cli.py kinda/personality.py kinda/security.py --ignore-missing-imports || {
    print_error "Type checking failed"
    exit 1
}
print_success "Type checking OK"

# 3. Run core security tests only (fastest critical tests)
print_status "Running critical security tests..."
pytest tests/security/test_dos_protection.py -v --tb=short -x || {
    print_error "Security tests failed"
    exit 1
}
print_success "Security tests OK"

# 4. Run core transformer tests only (fast)
print_status "Running core transformer tests..."
pytest tests/python/test_fuzzy_constructs.py -v --tb=short -x || {
    print_error "Core transformer tests failed"
    exit 1
}
print_success "Core transformer tests OK"

# 5. Test CLI is functional
print_status "Testing CLI..."
kinda --help > /dev/null || { print_error "CLI broken"; exit 1; }
print_success "CLI functional"

# 6. Quick example smoke test (one example only)
print_status "Testing one example..."
kinda run examples/python/unified_syntax.py.knda > /dev/null || {
    print_error "Example execution failed"
    exit 1
}
print_success "Example execution OK"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
print_success "All smoke tests passed in ${DURATION}s"
echo ""
echo "✅ Ready for PR creation"
echo "⚠️  Note: Full CI validation runs on GitHub (scripts/ci-full.sh for local full test)"
