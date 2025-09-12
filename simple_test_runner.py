#!/usr/bin/env python3
"""
Simple test runner for Epic #125 Task 1 validation without pytest dependency.
Validates core loop construct functionality.
"""

import sys
import os
import tempfile
import subprocess
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath("."))

from kinda.langs.python.transformer import transform_line
from kinda.personality import PersonalityContext, PERSONALITY_PROFILES
from kinda.cli import setup_personality


def run_kinda_test(path):
    """Helper function to run kinda files and capture output."""
    result = subprocess.run(
        ["python", "-m", "kinda", "interpret", str(path)],
        capture_output=True,
        text=True,
        cwd="/home/kevin/kinda-lang",
    )
    if result.returncode != 0:
        print(f"Error running {path}: {result.stderr}")
        return None
    return result.stdout.strip()


def test_sometimes_while_transformation():
    """Test ~sometimes_while transforms to correct Python code."""
    print("Testing ~sometimes_while transformation...")
    line = "~sometimes_while count < 10:"
    result = transform_line(line)
    expected = ["while sometimes_while_condition(count < 10):"]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ ~sometimes_while transformation test passed")


def test_maybe_for_transformation():
    """Test ~maybe_for transforms to correct Python code."""
    print("Testing ~maybe_for transformation...")
    line = "~maybe_for item in items:"
    result = transform_line(line)
    expected = ["for item in items:"]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ ~maybe_for transformation test passed")


def test_personality_probabilities():
    """Test that personality profiles have correct loop construct probabilities."""
    print("Testing personality probability settings...")

    # Reset personality context
    PersonalityContext._instance = None

    personalities = {
        "reliable": {"sometimes_while_base": 0.90, "maybe_for_base": 0.95},
        "cautious": {"sometimes_while_base": 0.75, "maybe_for_base": 0.85},
        "playful": {"sometimes_while_base": 0.60, "maybe_for_base": 0.70},
        "chaotic": {"sometimes_while_base": 0.40, "maybe_for_base": 0.50},
    }

    for personality, expected in personalities.items():
        setup_personality(personality, chaos_level=5, seed=42)
        context = PersonalityContext.get_instance()
        profile = context.profile

        assert hasattr(
            profile, "sometimes_while_base"
        ), f"{personality} missing sometimes_while_base"
        assert hasattr(profile, "maybe_for_base"), f"{personality} missing maybe_for_base"

        assert (
            profile.sometimes_while_base == expected["sometimes_while_base"]
        ), f"{personality} sometimes_while_base: expected {expected['sometimes_while_base']}, got {profile.sometimes_while_base}"
        assert (
            profile.maybe_for_base == expected["maybe_for_base"]
        ), f"{personality} maybe_for_base: expected {expected['maybe_for_base']}, got {profile.maybe_for_base}"

        print(f"✓ {personality} personality probabilities correct")


def test_runtime_functionality():
    """Test basic runtime functionality of loop constructs."""
    print("Testing runtime functionality...")

    # Test ~sometimes_while with reliable personality
    setup_personality("reliable", chaos_level=1, seed=42)

    kinda_code = """count = 0
~sometimes_while count < 5:
    count += 1
print(f"Final count: {count}")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
        f.write(kinda_code)
        f.flush()
        temp_path = Path(f.name)

    try:
        output = run_kinda_test(temp_path)
        if output is None:
            print("✗ Runtime test failed - could not execute")
            return False

        # Should have some output with count
        assert "Final count:" in output, f"Expected count output, got: {output}"
        print("✓ ~sometimes_while runtime test passed")

        # Test ~maybe_for
        kinda_code2 = """processed = []
items = [1, 2, 3]
~maybe_for item in items:
    processed.append(item)
print(f"Processed: {len(processed)}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f2:
            f2.write(kinda_code2)
            f2.flush()
            temp_path2 = Path(f2.name)

        try:
            output2 = run_kinda_test(temp_path2)
            if output2 is None:
                print("✗ ~maybe_for runtime test failed - could not execute")
                return False

            assert "Processed:" in output2, f"Expected processed output, got: {output2}"
            print("✓ ~maybe_for runtime test passed")

        finally:
            temp_path2.unlink()

    finally:
        temp_path.unlink()

    return True


def main():
    """Run all validation tests for Epic #125 Task 1."""
    print("=== Epic #125 Task 1 Implementation Validation ===")
    print()

    try:
        # Test transformations
        test_sometimes_while_transformation()
        test_maybe_for_transformation()

        # Test personality integration
        test_personality_probabilities()

        # Test runtime functionality
        if not test_runtime_functionality():
            return False

        print()
        print("🎉 All Epic #125 Task 1 validation tests passed!")
        print("✓ Implementation is complete and functional")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
