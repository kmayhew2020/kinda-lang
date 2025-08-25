#!/bin/bash

# Emergency repository cleanup script
echo "=== EMERGENCY REPOSITORY CLEANUP ==="

cd /workspaces/kinda-lang || exit 1

echo "Current directory: $(pwd)"
echo "Current branch: $(git branch --show-current)"

# Check git status
echo "=== Current git status ==="
git status

# Check if we need to switch branches
current_branch=$(git branch --show-current)
if [ "$current_branch" != "develop" ]; then
    echo "=== Switching to develop branch ==="
    git checkout develop
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to switch to develop branch"
        exit 1
    fi
fi

echo "=== Adding untracked test files ==="
# Add the specific untracked test files
git add tests/python/test_cli_comprehensive.py
git add tests/python/test_fuzzy_runtime_coverage.py
git add tests/python/test_interpreter_main.py
git add tests/python/test_interpreter_repl.py
git add tests/python/test_runtime_gen_coverage.py

# Check what's staged
echo "=== Staged changes ==="
git diff --cached --name-only

# Commit the changes
echo "=== Committing changes ==="
git commit -m "feat: add comprehensive test coverage files

- Add test_cli_comprehensive.py for CLI edge case testing
- Add test_fuzzy_runtime_coverage.py for runtime error handling
- Add test_interpreter_main.py for interpreter module testing
- Add test_interpreter_repl.py for REPL functionality testing  
- Add test_runtime_gen_coverage.py for runtime generation coverage

These tests improve overall test coverage and ensure robust error handling
across all major components of the Kinda language system.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Check final status
echo "=== Final git status ==="
git status

echo "=== Repository cleanup completed ==="