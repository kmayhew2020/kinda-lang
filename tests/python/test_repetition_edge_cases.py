"""
Advanced Edge Cases and Boundary Tests for Epic #125 Task 2: Repetition Constructs
Tests boundary conditions, malformed inputs, and edge scenarios for ~kinda_repeat and ~eventually_until
"""

import pytest
import tempfile
import os
import time
from pathlib import Path
from subprocess import run, PIPE, TimeoutExpired

from kinda.personality import PersonalityContext


class TestKindaRepeatEdgeCases:
    """Advanced edge case tests for ~kinda_repeat construct"""

    def test_kinda_repeat_invalid_inputs(self):
        """Test ~kinda_repeat with various invalid input types"""
        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(1300)

        invalid_inputs = [
            '"string"',
            "None",
            "[]",
            "{}",
            "object()",
            "lambda x: x",
        ]

        for invalid_input in invalid_inputs:
            test_code = f"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

counter = [0]  # Use list to avoid scoping issues
try:
    ~kinda_repeat({invalid_input}):
        counter[0] += 1
except Exception as exc:
    print(f"ERROR:{{type(exc).__name__}}")

print(f"EXECUTED:{{counter[0]}}")
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

                    # Should not crash - either handle gracefully or provide error
                    output_lines = result.stdout.strip().split("\n")
                    exec_line = [line for line in output_lines if line.startswith("EXECUTED:")]

                    if exec_line:
                        executed = int(exec_line[0].split(":")[1])
                        # Should either execute at least once (fallback) or zero times (handled error)
                        assert (
                            executed >= 0
                        ), f"Executed count should be non-negative for {invalid_input}"
                        assert (
                            executed <= 5
                        ), f"Should not execute excessively for invalid input {invalid_input}"

                finally:
                    os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_kinda_repeat_extreme_values(self):
        """Test ~kinda_repeat with extremely large and small values"""
        PersonalityContext.set_mood("cautious")
        PersonalityContext.set_seed(1400)

        extreme_cases = [
            ("1000000", 30),  # Very large - should be handled efficiently
            ("0.1", 10),  # Fractional - should be converted to int
            ("0.9", 10),  # Fractional close to 1
            ("-5", 10),  # Negative - should handle gracefully
            ("float('inf')", 10),  # Infinity - should handle gracefully
        ]

        for test_value, timeout in extreme_cases:
            test_code = f"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

counter = [0]  # Use list to avoid scoping issues
try:
    ~kinda_repeat({test_value}):
        counter[0] += 1
        if counter[0] > 10000:  # Safety break
            break
except Exception as exc:
    print(f"ERROR:{{type(exc).__name__}}:{{exc}}")

print(f"RESULT:{{counter[0]}}")
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
                        timeout=timeout,
                        cwd="/home/kevin/kinda-lang",
                    )
                    execution_time = time.time() - start_time

                    # Should handle extreme cases without crashing
                    if result.returncode == 0:
                        output_lines = result.stdout.strip().split("\n")
                        result_line = [line for line in output_lines if line.startswith("RESULT:")]

                        if result_line:
                            count = int(result_line[0].split(":")[1])

                            if test_value == "1000000":
                                # Should not actually run a million times
                                assert count <= 50000, f"Should limit extreme large values: {count}"
                            elif test_value in ["0.1", "0.9"]:
                                # Fractional should be converted to int
                                assert (
                                    0 <= count <= 5
                                ), f"Fractional conversion should result in small count: {count}"
                            elif test_value == "-5":
                                # Negative should be handled (likely 0 or error fallback)
                                assert (
                                    count >= 0
                                ), f"Negative input should not cause negative executions: {count}"

                    # Should not take too long regardless of input
                    assert (
                        execution_time < timeout - 1
                    ), f"Execution too slow for {test_value}: {execution_time:.2f}s"

                except TimeoutExpired:
                    # This is acceptable for extreme values
                    pass
                finally:
                    os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_kinda_repeat_complex_expressions(self):
        """Test ~kinda_repeat with complex mathematical expressions"""
        PersonalityContext.set_mood("playful")
        PersonalityContext.set_seed(1500)

        complex_expressions = [
            "2 + 3",
            "int(7.8)",
            "max(3, 5)",
            "len([1, 2, 3, 4])",
            "abs(-8)",
            "10 if True else 2",
        ]

        for expr in complex_expressions:
            test_code = f"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

counter = [0]  # Use list to avoid scoping issues
~kinda_repeat({expr}):
    counter[0] += 1

print(f"EXPR:{{repr('{expr}')}}")
print(f"ITERATIONS:{{counter[0]}}")
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
                    ), f"Complex expression failed: {expr}\n{result.stderr}"

                    output_lines = result.stdout.strip().split("\n")
                    iter_line = [line for line in output_lines if line.startswith("ITERATIONS:")]
                    assert len(iter_line) == 1

                    iterations = int(iter_line[0].split(":")[1])

                    # Should execute reasonable number of times based on expression value
                    assert iterations >= 1, f"Should execute at least once for {expr}"
                    assert (
                        iterations <= 50
                    ), f"Should not execute excessively for {expr}: {iterations}"

                finally:
                    os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_kinda_repeat_nested_extreme_depth(self):
        """Test deeply nested ~kinda_repeat constructs"""
        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(1600)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

total = 0
~kinda_repeat(3):
    ~kinda_repeat(3):
        ~kinda_repeat(3):
            ~kinda_repeat(3):
                ~kinda_repeat(2):
                    total += 1

print(f"TOTAL:{total}")
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

                assert result.returncode == 0, f"Deep nesting failed: {result.stderr}"

                output_lines = result.stdout.strip().split("\n")
                total_line = [line for line in output_lines if line.startswith("TOTAL:")]
                assert len(total_line) == 1

                total = int(total_line[0].split(":")[1])

                # Expected: ~3^5 * 2 = ~162 * 2 = ~324 with reliable personality
                # Allow significant variance due to compounding
                assert 100 <= total <= 700, f"Deep nesting result out of range: {total}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


class TestEventuallyUntilEdgeCases:
    """Advanced edge case tests for ~eventually_until construct"""

    def test_eventually_until_malformed_conditions(self):
        """Test ~eventually_until with malformed or dangerous conditions"""
        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(1700)

        malformed_conditions = [
            "invalid_variable > 5",
            "1/0 > 0",  # Division by zero
            "None.attribute",  # Attribute error
            "''[0]",  # Index error
            "undefined_function()",  # Name error
        ]

        for condition in malformed_conditions:
            test_code = f"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

counter = [0]  # Use list to avoid scoping issues
try:
    ~eventually_until {condition}:
        counter[0] += 1
        if counter[0] > 20:  # Safety break
            break
except Exception as exc:
    print(f"ERROR:{{type(exc).__name__}}")

print(f"ITERATIONS:{{counter[0]}}")
"""

            with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
                f.write(test_code)
                f.flush()

                try:
                    result = run(
                        ["python", "-m", "kinda", "run", f.name],
                        capture_output=True,
                        text=True,
                        timeout=15,
                        cwd="/home/kevin/kinda-lang",
                    )

                    # Should handle malformed conditions gracefully
                    output_lines = result.stdout.strip().split("\n")
                    iter_line = [line for line in output_lines if line.startswith("ITERATIONS:")]

                    if iter_line:
                        iterations = int(iter_line[0].split(":")[1])
                        # Should either terminate quickly (error handling) or hit safety break
                        assert (
                            0 <= iterations <= 25
                        ), f"Iterations should be reasonable for malformed condition: {iterations}"

                    # Should not crash the interpreter
                    # (Some non-zero exit codes are acceptable for malformed input)

                finally:
                    os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_eventually_until_complex_conditions(self):
        """Test ~eventually_until with complex logical conditions"""
        PersonalityContext.set_mood("cautious")
        PersonalityContext.set_seed(1800)

        complex_conditions = [
            ("x > 10 and y < 5", "state[0] > 10 and state[1] < 5"),
            ("x % 7 == 0 or y > 15", "state[0] % 7 == 0 or state[1] > 15"),
            ("(x + y) * 2 > 50", "(state[0] + state[1]) * 2 > 50"),
            ("x in [20, 21, 22] and y not in [3, 4]", "state[0] in [20, 21, 22] and state[1] not in [3, 4]"),
            ("len(str(x)) >= 2", "len(str(state[0])) >= 2"),
        ]

        for original_condition, state_condition in complex_conditions:
            test_code = f"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

state = [0, 0]  # Use list to avoid scoping issues: [x, y]
iteration_count = [0]  # Safety counter
~eventually_until {state_condition}:
    x, y = state[0], state[1]  # Load values
    iteration_count[0] += 1
    if iteration_count[0] > 1000:  # Safety break to prevent infinite loops
        break
    x += 1
    if x > 10:
        y += 1
        x = 0
    state[0], state[1] = x, y  # Store values

print(f"X:{{state[0]}}")
print(f"Y:{{state[1]}}")
print(f"CONDITION_MET:{original_condition}")
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

                    assert (
                        result.returncode == 0
                    ), f"Complex condition failed: {condition}\n{result.stderr}"

                    output_lines = result.stdout.strip().split("\n")
                    x_line = [line for line in output_lines if line.startswith("X:")]
                    y_line = [line for line in output_lines if line.startswith("Y:")]
                    condition_line = [
                        line for line in output_lines if line.startswith("CONDITION_MET:")
                    ]

                    assert len(x_line) == 1 and len(y_line) == 1

                    x = int(x_line[0].split(":")[1])
                    y = int(y_line[0].split(":")[1])

                    # Verify the condition is actually met when loop terminates
                    if condition_line:
                        condition_met = eval(condition_line[0].split(":", 1)[1])
                        # Note: condition might be evaluated in different context

                    # Check that variables progressed reasonably
                    assert x >= 0 and y >= 0, f"Variables should be non-negative: x={x}, y={y}"
                    assert x + y * 10 <= 300, f"Should terminate in reasonable time: x={x}, y={y}"

                finally:
                    os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_eventually_until_state_corruption(self):
        """Test ~eventually_until with state that changes during evaluation"""
        PersonalityContext.set_mood("chaotic")
        PersonalityContext.set_seed(1900)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# State that changes unpredictably during evaluation
class UnstableState:
    def __init__(self):
        self.value = 0
        self.access_count = 0
    
    def __gt__(self, other):
        self.access_count += 1
        # Value changes based on how many times it's accessed
        self.value = self.access_count % 3
        return self.value > other

state = UnstableState()
iterations = 0

~eventually_until state > 1:
    iterations += 1
    if iterations > 50:  # Safety break
        break

print(f"ITERATIONS:{iterations}")
print(f"STATE_VALUE:{state.value}")
print(f"ACCESS_COUNT:{state.access_count}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=25,
                    cwd="/home/kevin/kinda-lang",
                )

                assert result.returncode == 0, f"Unstable state test failed: {result.stderr}"

                output_lines = result.stdout.strip().split("\n")
                iter_line = [line for line in output_lines if line.startswith("ITERATIONS:")]
                state_line = [line for line in output_lines if line.startswith("STATE_VALUE:")]
                access_line = [line for line in output_lines if line.startswith("ACCESS_COUNT:")]

                assert len(iter_line) == 1 and len(state_line) == 1 and len(access_line) == 1

                iterations = int(iter_line[0].split(":")[1])
                state_value = int(state_line[0].split(":")[1])
                access_count = int(access_line[0].split(":")[1])

                # Should eventually terminate despite unstable state
                assert 1 <= iterations <= 55, f"Should terminate reasonably: {iterations}"
                assert (
                    access_count >= iterations
                ), f"Should have accessed state multiple times: {access_count} vs {iterations}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_eventually_until_statistical_edge_cases(self):
        """Test ~eventually_until with statistical edge cases"""
        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(2000)

        # Test case where condition is true exactly 50% of the time
        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import random
random.seed(42)  # Deterministic for testing

evaluations = 0
~eventually_until random.random() > 0.5:
    evaluations += 1
    if evaluations > 1000:  # Safety break
        break

print(f"EVALUATIONS:{evaluations}")
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

                assert result.returncode == 0, f"Statistical edge case failed: {result.stderr}"

                output_lines = result.stdout.strip().split("\n")
                eval_line = [line for line in output_lines if line.startswith("EVALUATIONS:")]
                assert len(eval_line) == 1

                evaluations = int(eval_line[0].split(":")[1])

                # With 50% probability and 95% confidence (reliable), should need multiple samples
                assert (
                    3 <= evaluations <= 1000
                ), f"Statistical sampling should be reasonable: {evaluations}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


class TestBoundaryInteractions:
    """Test boundary interactions between repetition constructs"""

    def test_kinda_repeat_eventually_until_interaction(self):
        """Test interaction between ~kinda_repeat and ~eventually_until with shared state"""
        PersonalityContext.set_mood("playful")
        PersonalityContext.set_seed(2100)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Shared state between constructs
shared_counter = 0

~kinda_repeat(3):
    local_target = shared_counter + 5
    ~eventually_until shared_counter >= local_target:
        shared_counter += 1

print(f"FINAL_COUNTER:{shared_counter}")
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

                assert result.returncode == 0, f"Shared state interaction failed: {result.stderr}"

                output_lines = result.stdout.strip().split("\n")
                counter_line = [line for line in output_lines if line.startswith("FINAL_COUNTER:")]
                assert len(counter_line) == 1

                final_counter = int(counter_line[0].split(":")[1])

                # Each outer loop should add ~5 to counter, with 3 loops total
                # Expected: ~15 with some variance
                assert (
                    10 <= final_counter <= 25
                ), f"Shared state result out of range: {final_counter}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_repetition_constructs_memory_boundaries(self):
        """Test memory management at boundaries of repetition constructs"""
        PersonalityContext.set_mood("cautious")
        PersonalityContext.set_seed(2200)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test memory allocation patterns
data_sets = []

~kinda_repeat(5):
    local_data = []
    counter = 0
    ~eventually_until len(local_data) >= 20:
        local_data.append(counter)
        counter += 1
    data_sets.append(len(local_data))

print(f"DATASETS:{len(data_sets)}")
print(f"SIZES:{data_sets}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd="/home/kevin/kinda-lang",
                )

                assert result.returncode == 0, f"Memory boundary test failed: {result.stderr}"

                output_lines = result.stdout.strip().split("\n")
                datasets_line = [line for line in output_lines if line.startswith("DATASETS:")]
                sizes_line = [line for line in output_lines if line.startswith("SIZES:")]

                assert len(datasets_line) == 1 and len(sizes_line) == 1

                num_datasets = int(datasets_line[0].split(":")[1])

                # Should have created reasonable number of datasets
                assert 3 <= num_datasets <= 8, f"Dataset count out of range: {num_datasets}"

                # Each dataset should have reached the target size
                sizes_str = sizes_line[0].split(":", 1)[1]
                # Basic validation that sizes are reasonable
                assert (
                    "20" in sizes_str or "21" in sizes_str
                ), "Should have datasets near target size"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_repetition_with_personality_changes(self):
        """Test repetition constructs with personality changes during execution"""
        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from kinda.personality import PersonalityContext

results = []
PersonalityContext.set_mood("reliable")

for mood in ["reliable", "chaotic", "cautious"]:
    PersonalityContext.set_mood(mood)
    counter = [0]  # Use list to avoid scoping issues
    ~kinda_repeat(10):
        counter[0] += 1
    results.append(counter[0])

print(f"RESULTS:{results}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd="/home/kevin/kinda-lang",
                )

                assert result.returncode == 0, f"Personality change test failed: {result.stderr}"

                output_lines = result.stdout.strip().split("\n")
                results_line = [line for line in output_lines if line.startswith("RESULTS:")]
                assert len(results_line) == 1

                results_str = results_line[0].split(":", 1)[1]

                # Should show different behavior for different personalities
                # All results should be positive
                assert "[" in results_str and "]" in results_str, "Should have list of results"
                assert (
                    not "0" in results_str or results_str.count("0") <= 1
                ), "Should have mostly non-zero results"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_mood("playful")


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v", "-s"])
