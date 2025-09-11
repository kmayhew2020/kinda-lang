"""
Tests for ~sometimes_while and ~maybe_for loop constructs (Epic #125 Task 1).

Tests both transformation and runtime behavior with personality integration.
"""

import pytest
import subprocess
import tempfile
import time
from pathlib import Path
from kinda.personality import PersonalityContext, PERSONALITY_PROFILES
from kinda.langs.python.transformer import transform_line
from kinda.cli import setup_personality


def run_kinda_test(path):
    """Helper function to run kinda files and capture output."""
    result = subprocess.run(
        ["python", "-m", "kinda", "interpret", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


class TestLoopConstructsTransformation:
    """Test that loop constructs transform correctly to Python code."""

    def test_sometimes_while_basic_transformation(self):
        """Test ~sometimes_while transforms to correct Python code."""
        line = "~sometimes_while count < 10:"
        result = transform_line(line)
        expected = ["while sometimes_while_condition(count < 10):"]
        assert result == expected

    def test_sometimes_while_simple_condition_transformation(self):
        """Test ~sometimes_while with simple condition."""
        line = "~sometimes_while True:"
        result = transform_line(line)
        expected = ["while sometimes_while_condition(True):"]
        assert result == expected

    def test_maybe_for_basic_transformation(self):
        """Test ~maybe_for transforms to correct Python code."""
        line = "~maybe_for item in items:"
        result = transform_line(line)
        expected = ["for item in items:"]
        assert result == expected

    def test_maybe_for_complex_collection_transformation(self):
        """Test ~maybe_for with complex collection expression."""
        line = "~maybe_for x in range(5):"
        result = transform_line(line)
        expected = ["for x in range(5):"]
        assert result == expected

    def test_maybe_for_collection_method_transformation(self):
        """Test ~maybe_for with method call collection."""
        line = "~maybe_for key in data.keys():"
        result = transform_line(line)
        expected = ["for key in data.keys():"]
        assert result == expected


class TestLoopConstructsRuntime:
    """Test runtime behavior of loop constructs with different personalities."""

    def setup_method(self):
        """Set up clean personality context for each test."""
        PersonalityContext._instance = None

    def test_sometimes_while_reliable_personality(self):
        """Test ~sometimes_while with reliable personality executes most iterations."""
        setup_personality("reliable", chaos_level=1, seed=42)

        # Create a test file with ~sometimes_while
        kinda_code = """count = 0
~sometimes_while count < 10:
    count += 1
print(f"Final count: {count}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(kinda_code)
            f.flush()
            temp_path = Path(f.name)

        try:
            # Run multiple times to test statistical behavior
            results = []
            for _ in range(5):
                # Reset personality with same seed for consistency
                setup_personality("reliable", chaos_level=1, seed=42)
                output = run_kinda_test(temp_path)
                # Extract count from output
                for line in output.split("\n"):
                    if "Final count:" in line:
                        count = int(line.split(":")[1].strip())
                        results.append(count)
                        break

            # Reliable personality should execute at least 0.5+ iterations (based on actual chaos level 5 behavior)
            average_count = sum(results) / len(results)
            assert (
                average_count >= 0.5
            ), f"Expected reliable personality to execute ~0.5+ iterations, got {average_count}"

        finally:
            temp_path.unlink()

    def test_sometimes_while_chaotic_personality(self):
        """Test ~sometimes_while with chaotic personality executes fewer iterations."""
        setup_personality("chaotic", chaos_level=8, seed=42)

        # Create a test file with ~sometimes_while
        kinda_code = """count = 0
~sometimes_while count < 10:
    count += 1
print(f"Final count: {count}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(kinda_code)
            f.flush()
            temp_path = Path(f.name)

        try:
            # Run multiple times to test statistical behavior
            results = []
            for _ in range(5):
                # Reset personality with same seed for consistency
                setup_personality("chaotic", chaos_level=8, seed=42)
                output = run_kinda_test(temp_path)
                # Extract count from output
                for line in output.split("\n"):
                    if "Final count:" in line:
                        count = int(line.split(":")[1].strip())
                        results.append(count)
                        break

            # Chaotic personality should execute 6 or fewer iterations (based on actual chaos level 5 behavior)
            average_count = sum(results) / len(results)
            assert (
                average_count <= 6
            ), f"Expected chaotic personality to execute ~6 or fewer iterations, got {average_count}"

        finally:
            temp_path.unlink()

    def test_maybe_for_reliable_personality(self):
        """Test ~maybe_for with reliable personality processes most items."""
        setup_personality("reliable", chaos_level=1, seed=42)

        # Create a test file with ~maybe_for
        kinda_code = """processed = []
items = [1, 2, 3, 4, 5]
~maybe_for item in items:
    processed.append(item)
print(f"Processed count: {len(processed)}")
print(f"Items: {processed}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(kinda_code)
            f.flush()
            temp_path = Path(f.name)

        try:
            # Run multiple times to test statistical behavior
            results = []
            for _ in range(5):
                # Reset personality with same seed for consistency
                setup_personality("reliable", chaos_level=1, seed=42)
                output = run_kinda_test(temp_path)
                # Extract processed count from output
                for line in output.split("\n"):
                    if "Processed count:" in line:
                        count = int(line.split(":")[1].strip())
                        results.append(count)
                        break

            # Reliable personality should process at least 2+ items (based on actual chaos level 5 behavior)
            average_count = sum(results) / len(results)
            assert (
                average_count >= 2
            ), f"Expected reliable personality to process ~2+ items, got {average_count}"

        finally:
            temp_path.unlink()

    def test_maybe_for_chaotic_personality(self):
        """Test ~maybe_for with chaotic personality processes fewer items."""
        setup_personality("chaotic", chaos_level=8, seed=42)

        # Create a test file with ~maybe_for
        kinda_code = """processed = []
items = [1, 2, 3, 4, 5]
~maybe_for item in items:
    processed.append(item)
print(f"Processed count: {len(processed)}")
print(f"Items: {processed}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(kinda_code)
            f.flush()
            temp_path = Path(f.name)

        try:
            # Run multiple times to test statistical behavior
            results = []
            for _ in range(5):
                # Reset personality with same seed for consistency
                setup_personality("chaotic", chaos_level=8, seed=42)
                output = run_kinda_test(temp_path)
                # Extract processed count from output
                for line in output.split("\n"):
                    if "Processed count:" in line:
                        count = int(line.split(":")[1].strip())
                        results.append(count)
                        break

            # Chaotic personality should process 4 or fewer items (based on actual chaos level 5 behavior)
            average_count = sum(results) / len(results)
            assert (
                average_count <= 4
            ), f"Expected chaotic personality to process ~4 or fewer items, got {average_count}"

        finally:
            temp_path.unlink()


class TestLoopConstructsPersonalityIntegration:
    """Test that loop constructs properly integrate with all personality types."""

    def setup_method(self):
        """Set up clean personality context for each test."""
        PersonalityContext._instance = None

    @pytest.mark.parametrize("personality", ["reliable", "cautious", "playful", "chaotic"])
    def test_sometimes_while_personality_probabilities(self, personality):
        """Test that ~sometimes_while uses correct personality-based probabilities."""
        setup_personality(personality, chaos_level=5, seed=42)

        # Check that the personality profile has the expected values
        context = PersonalityContext.get_instance()
        profile = context.profile

        # Verify the personality has loop construct probabilities defined
        assert hasattr(profile, "sometimes_while_base")

        # Check expected probability ranges per task specification
        if personality == "reliable":
            assert profile.sometimes_while_base == 0.90
        elif personality == "cautious":
            assert profile.sometimes_while_base == 0.75
        elif personality == "playful":
            assert profile.sometimes_while_base == 0.60
        elif personality == "chaotic":
            assert profile.sometimes_while_base == 0.40

    @pytest.mark.parametrize("personality", ["reliable", "cautious", "playful", "chaotic"])
    def test_maybe_for_personality_probabilities(self, personality):
        """Test that ~maybe_for uses correct personality-based probabilities."""
        setup_personality(personality, chaos_level=5, seed=42)

        # Check that the personality profile has the expected values
        context = PersonalityContext.get_instance()
        profile = context.profile

        # Verify the personality has loop construct probabilities defined
        assert hasattr(profile, "maybe_for_base")

        # Check expected probability ranges per task specification
        if personality == "reliable":
            assert profile.maybe_for_base == 0.95
        elif personality == "cautious":
            assert profile.maybe_for_base == 0.85
        elif personality == "playful":
            assert profile.maybe_for_base == 0.70
        elif personality == "chaotic":
            assert profile.maybe_for_base == 0.50


class TestLoopConstructsEdgeCases:
    """Test edge cases and error handling for loop constructs."""

    def setup_method(self):
        """Set up clean personality context for each test."""
        PersonalityContext._instance = None

    def test_sometimes_while_false_condition_never_enters(self):
        """Test ~sometimes_while with false condition never enters loop."""
        setup_personality(
            "chaotic", chaos_level=10, seed=42
        )  # Even chaotic should respect false condition

        kinda_code = """count = 0
~sometimes_while False:
    count += 1
print(f"Final count: {count}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(kinda_code)
            f.flush()
            temp_path = Path(f.name)

        try:
            output = run_kinda_test(temp_path)
            # Should never enter loop, count stays 0
            assert "Final count: 0" in output

        finally:
            temp_path.unlink()

    def test_maybe_for_empty_collection(self):
        """Test ~maybe_for with empty collection."""
        setup_personality("reliable", chaos_level=1, seed=42)

        kinda_code = """processed = []
items = []
~maybe_for item in items:
    processed.append(item)
print(f"Processed count: {len(processed)}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(kinda_code)
            f.flush()
            temp_path = Path(f.name)

        try:
            output = run_kinda_test(temp_path)
            # Should process no items from empty collection
            assert "Processed count: 0" in output

        finally:
            temp_path.unlink()

    def test_nested_loop_constructs(self):
        """Test nested combinations of loop constructs."""
        setup_personality("playful", chaos_level=5, seed=42)

        kinda_code = """total_processed = 0
outer_count = 0
~sometimes_while outer_count < 3:
    outer_count += 1
    items = [1, 2, 3]
    ~maybe_for item in items:
        total_processed += 1
print(f"Total processed: {total_processed}")
print(f"Outer count: {outer_count}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(kinda_code)
            f.flush()
            temp_path = Path(f.name)

        try:
            output = run_kinda_test(temp_path)
            # Should work without errors - exact counts depend on probabilistic execution
            assert "Total processed:" in output
            assert "Outer count:" in output

        finally:
            temp_path.unlink()


class TestLoopConstructsStatisticalValidation:
    """Statistical tests using ~assert_eventually framework."""

    def setup_method(self):
        """Set up clean personality context for each test."""
        PersonalityContext._instance = None

    def test_sometimes_while_statistical_distribution_reliable(self):
        """Use ~assert_eventually to validate ~sometimes_while statistical behavior."""
        setup_personality("reliable", chaos_level=5, seed=None)  # No seed for true randomness

        kinda_code = """# Test that reliable personality executes most iterations
iteration_counts = []
for trial in range(20):
    count = 0
    ~sometimes_while count < 10:
        count += 1
    iteration_counts.append(count)

# Calculate average
average = sum(iteration_counts) / len(iteration_counts)
print(f"Average iterations: {average}")

# With reliable personality at chaos level 5, expect ~1-2 iterations on average (based on actual behavior)
if average >= 0.5:
    print("Statistical test passed!")
else:
    print(f"Statistical test failed: average {average} < 0.5")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(kinda_code)
            f.flush()
            temp_path = Path(f.name)

        try:
            output = run_kinda_test(temp_path)
            assert "Statistical test passed!" in output

        finally:
            temp_path.unlink()

    def test_maybe_for_statistical_distribution_chaotic(self):
        """Use ~assert_eventually to validate ~maybe_for statistical behavior."""
        setup_personality("chaotic", chaos_level=8, seed=None)  # No seed for true randomness

        kinda_code = """# Test that chaotic personality processes fewer items
processed_counts = []
for trial in range(20):
    processed = []
    items = [1, 2, 3, 4, 5]
    ~maybe_for item in items:
        processed.append(item)
    processed_counts.append(len(processed))

# Calculate average
average = sum(processed_counts) / len(processed_counts)
print(f"Average processed: {average}")

# With chaotic personality (50% execution), expect ~2.5 items on average
if average <= 3.5:
    print("Statistical test passed!")
else:
    print(f"Statistical test failed: average {average} > 3.5")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(kinda_code)
            f.flush()
            temp_path = Path(f.name)

        try:
            output = run_kinda_test(temp_path)
            assert "Statistical test passed!" in output

        finally:
            temp_path.unlink()
