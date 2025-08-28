#!/usr/bin/env python3
"""
Emergency repository cleanup script
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        print(f"Command: {cmd}")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result
    except Exception as e:
        print(f"Exception running command '{cmd}': {e}")
        return None

def main():
    print("=== EMERGENCY REPOSITORY CLEANUP ===")
    
    # Change to repository root
    repo_root = Path("/workspaces/kinda-lang")
    os.chdir(repo_root)
    print(f"Working in: {repo_root}")
    
    # Check current branch
    result = run_command("git branch --show-current")
    if result and result.returncode == 0:
        current_branch = result.stdout.strip()
        print(f"Current branch: {current_branch}")
        
        # Switch to develop if needed
        if current_branch != "develop":
            print("=== Switching to develop branch ===")
            result = run_command("git checkout develop")
            if result.returncode != 0:
                print("ERROR: Failed to switch to develop branch")
                sys.exit(1)
    
    # Check git status
    print("=== Current git status ===")
    run_command("git status --porcelain")
    
    # Add untracked test files
    print("=== Adding untracked test files ===")
    test_files = [
        "tests/python/test_cli_comprehensive.py",
        "tests/python/test_fuzzy_runtime_coverage.py", 
        "tests/python/test_interpreter_main.py",
        "tests/python/test_interpreter_repl.py",
        "tests/python/test_runtime_gen_coverage.py"
    ]
    
    for test_file in test_files:
        if (repo_root / test_file).exists():
            result = run_command(f"git add {test_file}")
            if result.returncode == 0:
                print(f"✓ Added {test_file}")
            else:
                print(f"✗ Failed to add {test_file}")
    
    # Check what's staged
    print("=== Staged changes ===")
    run_command("git diff --cached --name-only")
    
    # Commit the changes
    print("=== Committing changes ===")
    commit_message = '''feat: add comprehensive test coverage files

- Add test_cli_comprehensive.py for CLI edge case testing
- Add test_fuzzy_runtime_coverage.py for runtime error handling
- Add test_interpreter_main.py for interpreter module testing
- Add test_interpreter_repl.py for REPL functionality testing  
- Add test_runtime_gen_coverage.py for runtime generation coverage

These tests improve overall test coverage and ensure robust error handling
across all major components of the Kinda language system.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>'''
    
    result = run_command(f'git commit -m "{commit_message}"')
    
    # Check final status
    print("=== Final git status ===")
    run_command("git status")
    
    print("=== Repository cleanup completed ===")

if __name__ == "__main__":
    main()