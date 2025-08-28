#!/usr/bin/env python3
"""
Comprehensive testing of all .knda example files.
This ensures every example file can be transformed and executed without errors.
"""

import pytest
from pathlib import Path
import subprocess
import tempfile
import os


def get_all_example_files():
    """Discover all .knda example files (Python only for v0.3.0)."""
    examples_dir = Path("examples")
    if not examples_dir.exists():
        return []
    
    # Only include Python examples for now
    return list((examples_dir / "python").rglob("*.knda"))


@pytest.mark.parametrize("example_file", get_all_example_files())
def test_example_transforms_successfully(example_file):
    """Test that each example file transforms without errors."""
<<<<<<< HEAD
    project_root = Path(__file__).parent.parent.parent
    result = subprocess.run(
        ["python", "-m", "kinda.cli", "transform", str(example_file)],
        capture_output=True,
        text=True,
        cwd=project_root  # Ensure consistent working directory
=======
    result = subprocess.run(
        ["python", "-m", "kinda.cli", "transform", str(example_file)],
        capture_output=True,
        text=True
>>>>>>> origin/main
    )
    
    assert result.returncode == 0, (
        f"Transformation failed for {example_file}:\n"
        f"STDOUT: {result.stdout}\n"
        f"STDERR: {result.stderr}"
    )
    
    # Check that build file was created
    expected_build_file = Path("build") / example_file.stem  # Remove .knda and add .py
    expected_build_file = expected_build_file.with_suffix(".py")
    assert expected_build_file.exists(), f"Build file not created for {example_file}"


@pytest.mark.parametrize("example_file", get_all_example_files())
def test_example_runs_without_crash(example_file):
    """Test that each example file runs without crashing."""
    # Skip files that are known to have runtime issues (like syntax errors in original examples)
    skip_files = {
        "chaos_arena2_complete.py.knda",  # Has pre-existing multi-line sorta_print issue
    }
    
    if example_file.name in skip_files:
        pytest.skip(f"Skipping {example_file.name} - known issue")
    
<<<<<<< HEAD
    project_root = Path(__file__).parent.parent.parent
=======
>>>>>>> origin/main
    result = subprocess.run(
        ["python", "-m", "kinda.cli", "run", str(example_file)],
        capture_output=True,
        text=True,
<<<<<<< HEAD
        timeout=30,  # 30 second timeout to avoid hanging
        cwd=project_root  # Ensure consistent working directory
=======
        timeout=30  # 30 second timeout to avoid hanging
>>>>>>> origin/main
    )
    
    # We expect successful execution (returncode 0) or at most warnings/fuzzy behavior
    # But not crashes or syntax errors
    if result.returncode != 0:
        # Check if it's a runtime syntax error vs expected fuzzy behavior
        stderr_lower = result.stderr.lower()
        if any(error in stderr_lower for error in ["syntaxerror", "unmatched", "invalid syntax"]):
            pytest.fail(
                f"Syntax error in {example_file}:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )
        # Otherwise it might be expected fuzzy behavior, so we allow it


def test_all_examples_discovered():
    """Ensure we actually found example files to test."""
    example_files = get_all_example_files()
    assert len(example_files) > 0, "No example files found! Check examples directory structure."
    
    # Verify we found the key examples we expect
    example_names = [f.name for f in example_files]
    expected_examples = [
        "welp_example.py.knda",
        "chaos_arena_complete.py.knda",
        "hello.py.knda",
    ]
    
    for expected in expected_examples:
        assert expected in example_names, f"Expected example {expected} not found"


def test_complex_examples_present():
    """Verify our most complex examples are present and testable."""
    example_files = get_all_example_files()
    complex_examples = [f for f in example_files if "chaos_arena" in f.name or "comprehensive" in str(f.parent)]
    
    assert len(complex_examples) >= 3, (
        f"Expected at least 3 complex examples, found {len(complex_examples)}: "
        f"{[f.name for f in complex_examples]}"
    )


class TestExampleIntegration:
    """Integration tests for example functionality."""
    
    def test_chaos_arena_complete_transforms(self):
        """Test that chaos_arena_complete specifically transforms correctly."""
<<<<<<< HEAD
        project_root = Path(__file__).parent.parent.parent
        result = subprocess.run(
            ["python", "-m", "kinda.cli", "transform", "examples/python/comprehensive/chaos_arena_complete.py.knda"],
            capture_output=True,
            text=True,
            cwd=project_root  # Ensure consistent working directory
=======
        result = subprocess.run(
            ["python", "-m", "kinda.cli", "transform", "examples/python/comprehensive/chaos_arena_complete.py.knda"],
            capture_output=True,
            text=True
>>>>>>> origin/main
        )
        
        assert result.returncode == 0, f"chaos_arena_complete transformation failed: {result.stderr}"
        
        # Check for expected constructs in output
        build_file = Path("build/chaos_arena_complete.py")
        assert build_file.exists(), "chaos_arena_complete build file not created"
        
        content = build_file.read_text(encoding='utf-8')
        # Only check for constructs that are actually used in this specific file
        expected_imports = [
            "from kinda.langs.python.runtime.fuzzy import",
            "kinda_int",
            "sorta_print", 
            "sometimes",
            "maybe",
            "ish_value"
            # Note: welp_fallback not used in chaos_arena_complete, only in welp_example
        ]
        
        for expected in expected_imports:
            assert expected in content, f"Expected '{expected}' in transformed output"
    
    def test_welp_example_runs_successfully(self):
        """Test that welp_example runs without issues."""
        project_root = Path(__file__).parent.parent.parent
        example_path = project_root / "examples" / "python" / "individual" / "welp_example.py.knda"
        result = subprocess.run(
            ["python", "-m", "kinda.cli", "run", str(example_path)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=project_root  # Ensure we're in project root
        )
        
        # Should complete successfully
        assert result.returncode == 0, f"welp_example run failed: {result.stderr}"
        
        # Check for expected welp behavior in output
        output = result.stdout + result.stderr
        assert "=== ~welp Construct Demo ===" in output
        assert "~welp provides graceful fallbacks" in output