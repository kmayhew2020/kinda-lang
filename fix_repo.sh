#!/bin/bash
# Repository cleanup script

echo "=== Fixing Repository State ==="

# Check current branch
echo "Current branch:"
git branch --show-current

# Check status  
echo "Git status:"
git status --porcelain

# Switch to develop branch
echo "Switching to develop branch..."
git checkout develop || git checkout -b develop

# Add the untracked test files
echo "Adding untracked test files..."
git add tests/python/test_cli_comprehensive.py
git add tests/python/test_fuzzy_runtime_coverage.py
git add tests/python/test_interpreter_main.py
git add tests/python/test_interpreter_repl.py
git add tests/python/test_runtime_gen_coverage.py

# Commit them
echo "Committing test coverage files..."
git commit -m "test: add comprehensive test coverage improvements

- Add CLI comprehensive testing with error handling
- Add fuzzy runtime error handling coverage tests  
- Add interpreter main module testing
- Add REPL functionality tests
- Add runtime generation coverage tests

Improves overall test coverage and robustness.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Clean any build artifacts
echo "Cleaning build artifacts..."
rm -rf build/ htmlcov/ *.egg-info/

# Check final status
echo "Final git status:"
git status

echo "=== Repository cleanup complete ==="