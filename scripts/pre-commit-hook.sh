#!/bin/bash
# Pre-commit hook for Kinda-Lang development
# Runs essential checks before each commit to catch issues early

set -e

echo "🎲 Kinda pre-commit validation..."

# Change to project root
cd "$(git rev-parse --show-toplevel)"

# Quick style and basic test check
echo "  → Code formatting check..."
python -m black --check --quiet kinda/ tests/ || {
    echo "❌ Code formatting issues. Run: black kinda/ tests/"
    exit 1
}

echo "  → Import sorting check..."
python -m isort --check-only --quiet kinda/ tests/ || {
    echo "❌ Import sorting issues. Run: isort kinda/ tests/"
    exit 1
}

echo "  → Quick linting check..."
python -m flake8 kinda/ tests/ --max-line-length=100 --ignore=E203,W503 --quiet || {
    echo "❌ Linting issues found"
    exit 1
}

echo "  → Fast test suite (critical tests only)..."
python -m pytest tests/ -x --tb=line --quiet -k "test_basic or test_cli" || {
    echo "❌ Critical tests failed"
    exit 1
}

echo "✅ Pre-commit checks passed!"
exit 0