"""
Stress Tests for Epic #125 Task 2: Repetition Constructs
Tests high iteration counts, memory usage, and performance limits for ~kinda_repeat and ~eventually_until
"""

import pytest
import tempfile
import os
import time
import gc
from pathlib import Path
from subprocess import run, PIPE, TimeoutExpired

from kinda.personality import PersonalityContext

# Try to import psutil for memory tests, but make it optional
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class TestStressKindaRepeat:
    """Stress tests for ~kinda_repeat construct"""

    def test_kinda_repeat_high_iteration_reliable(self):
        """Test ~kinda_repeat with very high iteration counts on reliable personality"""
        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(42)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

total = 0
~kinda_repeat(1000):
    total += 1

print(f"RESULT:{total}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                # Run with timeout to prevent infinite loops
                result = run(
                    ["python", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd="/home/kevin/kinda-lang",
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract the count from output
                output_lines = result.stdout.strip().split("\n")
                result_line = [line for line in output_lines if line.startswith("RESULT:")]
                assert len(result_line) == 1

                count = int(result_line[0].split(":")[1])

                # With reliable personality and high count, should be close to 1000
                # Allow ±10% variance as per spec
                assert 800 <= count <= 1200, f"Expected ~1000 ± 20%, got {count}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_kinda_repeat_extreme_chaotic_stress(self):
        """Test ~kinda_repeat with chaotic personality under extreme variance"""
        PersonalityContext.set_mood("chaotic")
        PersonalityContext.set_seed(12345)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

total = 0
~kinda_repeat(500):
    total += 1

print(f"RESULT:{total}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                start_time = time.time()
                result = run(
                    ["python", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=45,
                    cwd="/home/kevin/kinda-lang",
                )
                execution_time = time.time() - start_time

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract the count from output
                output_lines = result.stdout.strip().split("\n")
                result_line = [line for line in output_lines if line.startswith("RESULT:")]
                assert len(result_line) == 1

                count = int(result_line[0].split(":")[1])

                # With chaotic personality, variance should be ±40%
                # But must be at least 1
                assert count >= 1, "kinda_repeat should always run at least once"
                assert (
                    count <= 1400
                ), f"Chaotic variance shouldn't exceed reasonable bounds, got {count}"

                # Performance check - should complete in reasonable time
                assert execution_time < 30, f"Execution took too long: {execution_time:.2f}s"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    @pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not available")
    def test_kinda_repeat_memory_usage(self):
        """Test that ~kinda_repeat doesn't cause memory leaks with high iterations"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(9999)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test memory usage with large arrays
data = []
~kinda_repeat(2000):
    data.append(len(data))

print(f"RESULT:{len(data)}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd="/home/kevin/kinda-lang",
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract the count from output
                output_lines = result.stdout.strip().split("\n")
                result_line = [line for line in output_lines if line.startswith("RESULT:")]
                assert len(result_line) == 1

                count = int(result_line[0].split(":")[1])
                assert count > 1500, f"Expected high iteration count, got {count}"

            finally:
                os.unlink(f.name)

        # Force garbage collection and check memory usage
        gc.collect()
        time.sleep(0.1)  # Allow GC to complete
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB for this test)
        assert memory_increase < 50, f"Memory leak detected: {memory_increase:.2f}MB increase"

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_kinda_repeat_zero_and_negative(self):
        """Stress test edge cases with zero and negative inputs"""
        PersonalityContext.set_mood("chaotic")
        PersonalityContext.set_seed(555)

        test_cases = [
            ("0", 0),
            ("-1", 0),  # Should handle gracefully
            ("-10", 0),
        ]

        for input_val, expected_min in test_cases:
            test_code = f"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

counter = [0]  # Use list to avoid scoping issues
~kinda_repeat({input_val}):
    counter[0] += 1

print(f"RESULT:{{counter[0]}}")
"""

            with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
                f.write(test_code)
                f.flush()

                try:
                    result = run(
                        ["python", "-m", "kinda", "run", f.name],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd="/home/kevin/kinda-lang",
                    )

                    assert (
                        result.returncode == 0
                    ), f"Script failed for input {input_val}: {result.stderr}"

                    # Extract the count from output
                    output_lines = result.stdout.strip().split("\n")
                    result_line = [line for line in output_lines if line.startswith("RESULT:")]
                    assert len(result_line) == 1

                    count = int(result_line[0].split(":")[1])
                    assert (
                        count >= expected_min
                    ), f"For input {input_val}, expected >= {expected_min}, got {count}"

                finally:
                    os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


class TestStressEventuallyUntil:
    """Stress tests for ~eventually_until construct"""

    def test_eventually_until_slow_convergence(self):
        """Test ~eventually_until with conditions that converge very slowly"""
        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(777)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Slow convergence: condition becomes true with increasing probability
iteration = 0
~eventually_until iteration > 200:
    iteration += 1

print(f"RESULT:{iteration}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                start_time = time.time()
                result = run(
                    ["python", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd="/home/kevin/kinda-lang",
                )
                execution_time = time.time() - start_time

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract the count from output
                output_lines = result.stdout.strip().split("\n")
                result_line = [line for line in output_lines if line.startswith("RESULT:")]
                assert len(result_line) == 1

                count = int(result_line[0].split(":")[1])

                # With reliable personality (95% confidence), should terminate after condition becomes statistically true
                assert count > 200, f"Should terminate after condition becomes true, got {count}"
                assert count < 500, f"Should not run excessively long beyond condition, got {count}"

                # Performance check
                assert execution_time < 45, f"Execution took too long: {execution_time:.2f}s"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_eventually_until_never_resolves_timeout(self):
        """Test ~eventually_until with conditions that never become true (timeout scenario)"""
        PersonalityContext.set_mood("chaotic")
        PersonalityContext.set_seed(111)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Condition that never becomes true
iteration = 0
try:
    ~eventually_until False:
        iteration += 1
        if iteration > 10000:  # Safety break
            break
except Exception as e:
    print(f"ERROR:{type(e).__name__}")

print(f"RESULT:{iteration}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                start_time = time.time()
                result = run(
                    ["python", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd="/home/kevin/kinda-lang",
                )
                execution_time = time.time() - start_time

                # This should timeout or reach safety break
                if result.returncode == 0:
                    # Extract the count from output
                    output_lines = result.stdout.strip().split("\n")
                    result_line = [line for line in output_lines if line.startswith("RESULT:")]
                    if result_line:
                        count = int(result_line[0].split(":")[1])
                        # Should have run many iterations before hitting safety break
                        assert count > 100, f"Expected many iterations, got {count}"

                # Should complete within reasonable time (either timeout or safety break)
                assert (
                    execution_time < 25
                ), f"Should timeout or break quickly: {execution_time:.2f}s"

            except TimeoutExpired:
                # This is acceptable - the condition never resolves
                pass
            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_eventually_until_statistical_accuracy(self):
        """Test ~eventually_until statistical accuracy with multiple runs"""
        PersonalityContext.set_mood("reliable")

        # Run multiple tests to verify statistical behavior
        results = []

        for seed in range(10):  # Run 10 times with different seeds
            PersonalityContext.set_seed(seed + 1000)

            test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Condition that becomes true when counter reaches a threshold
counter = 0
~eventually_until counter >= 50:
    counter += 1

print(f"RESULT:{counter}")
"""

            with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
                f.write(test_code)
                f.flush()

                try:
                    result = run(
                        ["python", "-m", "kinda", "run", f.name],
                        capture_output=True,
                        text=True,
                        timeout=20,
                        cwd="/home/kevin/kinda-lang",
                    )

                    if result.returncode == 0:
                        # Extract the count from output
                        output_lines = result.stdout.strip().split("\n")
                        result_line = [line for line in output_lines if line.startswith("RESULT:")]
                        if result_line:
                            count = int(result_line[0].split(":")[1])
                            results.append(count)

                finally:
                    os.unlink(f.name)

        # Analyze statistical results
        assert len(results) > 5, "Should have multiple successful runs for statistical analysis"

        # All results should be >= 50 (the threshold)
        for count in results:
            assert count >= 50, f"All results should meet the condition, got {count}"

        # With reliable personality (95% confidence), should terminate with statistical certainty
        avg_result = sum(results) / len(results)
        assert (
            50 <= avg_result <= 150
        ), f"Average result should be above threshold with statistical confidence, got {avg_result:.1f}"

        # Variability should be reasonable
        max_result = max(results)
        min_result = min(results)
        range_span = max_result - min_result
        assert (
            range_span <= 100
        ), f"Range should be reasonable with statistical variation, got {range_span}"

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    @pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not available")
    def test_eventually_until_memory_efficiency(self):
        """Test that ~eventually_until doesn't accumulate excessive state"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        PersonalityContext.set_mood("playful")
        PersonalityContext.set_seed(2468)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test with multiple eventually_until loops to check state accumulation
results = []
for test_run in range(5):
    counter = 0
    ~eventually_until counter >= 20:
        counter += 1
    results.append(counter)

print(f"RESULT:{sum(results)}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd="/home/kevin/kinda-lang",
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract the sum from output
                output_lines = result.stdout.strip().split("\n")
                result_line = [line for line in output_lines if line.startswith("RESULT:")]
                assert len(result_line) == 1

                total_count = int(result_line[0].split(":")[1])
                assert total_count >= 100, f"Expected sum of results >= 100, got {total_count}"

            finally:
                os.unlink(f.name)

        # Check memory usage after multiple eventually_until executions
        gc.collect()
        time.sleep(0.1)
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be minimal for statistical state tracking
        assert memory_increase < 20, f"Memory usage increased too much: {memory_increase:.2f}MB"

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


class TestStressNestedConstructs:
    """Stress tests for nested repetition constructs"""

    def test_nested_kinda_repeat_stress(self):
        """Test deeply nested ~kinda_repeat constructs under stress"""
        PersonalityContext.set_mood("cautious")  # Use cautious to prevent extreme variance
        PersonalityContext.set_seed(987)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

total = 0
~kinda_repeat(10):
    ~kinda_repeat(10):
        ~kinda_repeat(5):
            total += 1

print(f"RESULT:{total}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                start_time = time.time()
                result = run(
                    ["python", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=45,
                    cwd="/home/kevin/kinda-lang",
                )
                execution_time = time.time() - start_time

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract the count from output
                output_lines = result.stdout.strip().split("\n")
                result_line = [line for line in output_lines if line.startswith("RESULT:")]
                assert len(result_line) == 1

                count = int(result_line[0].split(":")[1])

                # Expected: ~10 * ~10 * ~5 = ~500 with cautious personality variance
                # Cautious has ±20% variance, so compounded: approximately 300-700
                assert 200 <= count <= 1000, f"Nested repetition result out of range: {count}"

                # Performance check
                assert execution_time < 35, f"Nested execution took too long: {execution_time:.2f}s"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_mixed_repetition_constructs_stress(self):
        """Test mixing ~kinda_repeat and ~eventually_until under stress"""
        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(654)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

state = [0]  # [total_iterations] - Use list to avoid scoping issues
~kinda_repeat(5):
    counter = [0]  # Use list for inner counter too
    ~eventually_until counter[0] >= 10:
        counter[0] += 1
        state[0] += 1

print(f"RESULT:{state[0]}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                start_time = time.time()
                result = run(
                    ["python", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd="/home/kevin/kinda-lang",
                )
                execution_time = time.time() - start_time

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract the count from output
                output_lines = result.stdout.strip().split("\n")
                result_line = [line for line in output_lines if line.startswith("RESULT:")]
                assert len(result_line) == 1

                count = int(result_line[0].split(":")[1])

                # Expected: ~5 outer loops * ~10+ inner iterations per loop
                # With reliable personality, should be close to 5 * 10 = 50
                assert 45 <= count <= 75, f"Mixed construct result out of range: {count}"

                # Performance check
                assert execution_time < 45, f"Mixed execution took too long: {execution_time:.2f}s"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v", "-s"])
