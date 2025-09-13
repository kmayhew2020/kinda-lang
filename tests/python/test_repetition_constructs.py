"""
Test suite for Epic #125 Task 2: Repetition Constructs
Tests ~kinda_repeat(n) and ~eventually_until constructs
"""

import pytest
import tempfile
import os
from pathlib import Path

from kinda.personality import PersonalityContext


def test_kinda_repeat_basic_functionality():
    """Test basic ~kinda_repeat(n) functionality"""
    from kinda.langs.python.transformer import transform_file

    test_code = """
count = 0
~kinda_repeat(5):
    count += 1
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
        f.write(test_code)
        f.flush()

        try:
            result = transform_file(Path(f.name))
            assert "for _ in range(kinda_repeat_count(5)):" in result
            assert "kinda_repeat_count" in result
        finally:
            os.unlink(f.name)


def test_kinda_repeat_personality_variance():
    """Test that ~kinda_repeat shows personality-based variance"""
    # Set reliable personality for predictable testing
    PersonalityContext.set_mood("reliable")

    from kinda.personality import get_kinda_repeat_variance

    reliable_variance = get_kinda_repeat_variance()

    # Reliable personality should have low variance (±10% per spec)
    assert reliable_variance <= 0.12  # Small tolerance for chaos multiplier

    # Test chaotic personality
    PersonalityContext.set_mood("chaotic")
    chaotic_variance = get_kinda_repeat_variance()

    # Chaotic personality should have higher variance (±40% per spec)
    assert chaotic_variance >= 0.35  # Should be around 0.4 or higher

    # Reset to default
    PersonalityContext.set_mood("playful")


def test_kinda_repeat_edge_cases():
    """Test ~kinda_repeat edge cases"""
    from kinda.langs.python.transformer import transform_file

    # Test with n=0
    test_code_zero = """
~kinda_repeat(0):
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
        f.write(test_code_zero)
        f.flush()

        try:
            result = transform_file(Path(f.name))
            assert "kinda_repeat_count(0)" in result
        finally:
            os.unlink(f.name)

    # Test with n=1
    test_code_one = """
~kinda_repeat(1):
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
        f.write(test_code_one)
        f.flush()

        try:
            result = transform_file(Path(f.name))
            assert "kinda_repeat_count(1)" in result
        finally:
            os.unlink(f.name)


def test_eventually_until_basic_functionality():
    """Test basic ~eventually_until functionality"""
    from kinda.langs.python.transformer import transform_file

    test_code = """
count = 0
~eventually_until count > 5:
    count += 1
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
        f.write(test_code)
        f.flush()

        try:
            result = transform_file(Path(f.name))
            assert "while eventually_until_condition(count > 5):" in result
            assert "eventually_until_condition" in result
        finally:
            os.unlink(f.name)


def test_eventually_until_confidence_levels():
    """Test that ~eventually_until respects personality confidence levels"""
    # Set reliable personality
    PersonalityContext.set_mood("reliable")

    from kinda.personality import get_eventually_until_confidence

    reliable_confidence = get_eventually_until_confidence()

    # Reliable personality should have high confidence (95% per spec)
    assert reliable_confidence >= 0.90

    # Test chaotic personality
    PersonalityContext.set_mood("chaotic")
    chaotic_confidence = get_eventually_until_confidence()

    # Chaotic personality should have lower confidence (70% per spec)
    assert chaotic_confidence <= 0.80

    # Reset to default
    PersonalityContext.set_mood("playful")


def test_construct_integration():
    """Test that both constructs can be used together"""
    from kinda.langs.python.transformer import transform_file

    test_code = """
total = 0
~kinda_repeat(3):
    count = 0
    ~eventually_until count > 2:
        count += 1
    total += count
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
        f.write(test_code)
        f.flush()

        try:
            result = transform_file(Path(f.name))
            # Both constructs should be properly transformed
            assert "kinda_repeat_count(3)" in result
            assert "eventually_until_condition(count > 2)" in result
        finally:
            os.unlink(f.name)


def test_runtime_execution_kinda_repeat():
    """Test actual runtime execution of ~kinda_repeat through file execution"""
    from kinda.personality import PersonalityContext
    import subprocess
    import tempfile
    import os

    # Set deterministic seed for testing
    PersonalityContext.set_seed(42)
    PersonalityContext.set_mood("reliable")

    test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

count = 0
~kinda_repeat(5):
    count += 1

print(f"RESULT:{count}")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
        f.write(test_code)
        f.flush()

        try:
            # Run the test through kinda
            result = subprocess.run(
                ["python", "-m", "kinda", "run", f.name],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Extract the count from output
            output_lines = result.stdout.strip().split("\n")
            result_line = [line for line in output_lines if line.startswith("RESULT:")]
            assert len(result_line) == 1

            count = int(result_line[0].split(":")[1])
            assert isinstance(count, int)
            assert count >= 1  # Always at least 1
            assert 3 <= count <= 7  # Should be close to 5 for reliable personality

        finally:
            os.unlink(f.name)

    # Reset
    PersonalityContext.set_seed(None)
    PersonalityContext.set_mood("playful")


def test_runtime_execution_eventually_until():
    """Test actual runtime execution of ~eventually_until through file execution"""
    from kinda.personality import PersonalityContext
    import subprocess
    import tempfile
    import os

    # Set deterministic seed for testing
    PersonalityContext.set_seed(42)
    PersonalityContext.set_mood("reliable")

    test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

count = 0
~eventually_until count > 5:
    count += 1

print(f"RESULT:{count}")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
        f.write(test_code)
        f.flush()

        try:
            # Run the test through kinda
            result = subprocess.run(
                ["python", "-m", "kinda", "run", f.name],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Extract the count from output
            output_lines = result.stdout.strip().split("\n")
            result_line = [line for line in output_lines if line.startswith("RESULT:")]
            assert len(result_line) == 1

            count = int(result_line[0].split(":")[1])
            assert isinstance(count, int)
            # eventually_until should terminate when statistically confident count > 5
            # So count should be greater than 5 but not too much higher
            assert count > 5
            assert count < 20  # Reasonable upper bound

        finally:
            os.unlink(f.name)

    # Reset
    PersonalityContext.set_seed(None)
    PersonalityContext.set_mood("playful")


def test_construct_patterns():
    """Test that construct patterns match correctly"""
    from kinda.grammar.python.matchers import match_python_construct

    # Test kinda_repeat pattern
    kinda_repeat_line = "~kinda_repeat(5):"
    key, groups = match_python_construct(kinda_repeat_line)
    assert key == "kinda_repeat"
    assert groups[0].strip() == "5"

    # Test eventually_until pattern
    eventually_until_line = "~eventually_until count > 10:"
    key, groups = match_python_construct(eventually_until_line)
    assert key == "eventually_until"
    assert "count > 10" in groups[0]

    # Test complex conditions
    complex_line = "~eventually_until (x > 5 and y < 3) or z == 0:"
    key, groups = match_python_construct(complex_line)
    assert key == "eventually_until"
    assert "(x > 5 and y < 3) or z == 0" in groups[0]


def test_error_handling():
    """Test error handling in constructs through transformation"""
    from kinda.langs.python.transformer import transform_file

    # Test kinda_repeat with invalid input (should still transform correctly)
    test_code = """
~kinda_repeat("invalid"):
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
        f.write(test_code)
        f.flush()

        try:
            result = transform_file(Path(f.name))
            # Should still transform - error handling happens at runtime
            assert "kinda_repeat_count" in result
            assert '"invalid"' in result
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])
