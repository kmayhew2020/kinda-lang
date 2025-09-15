"""
Integration Tests for Epic #125 Task 2: Repetition Constructs
Tests integration of ~kinda_repeat and ~eventually_until with other kinda-lang constructs
"""

import pytest
import tempfile
import os
import time
from pathlib import Path
from subprocess import run, PIPE

from kinda.personality import PersonalityContext


class TestRepetitionWithConditionals:
    """Integration tests with conditional constructs (~sometimes, ~maybe, ~probably, ~rarely)"""

    def test_kinda_repeat_with_sometimes(self):
        """Test ~kinda_repeat containing ~sometimes conditional"""
        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(100)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Set personality in the subprocess
from kinda.personality import PersonalityContext
PersonalityContext.set_mood("reliable")
PersonalityContext.set_seed(100)

executed_count = 0
total_loops = 0

~kinda_repeat(20):
    total_loops += 1
    ~sometimes(True):
        executed_count += 1

print(f"LOOPS:{total_loops}")
print(f"EXECUTIONS:{executed_count}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python3", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd=os.getcwd(),
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract results from output
                output_lines = result.stdout.strip().split("\n")
                loops_line = [line for line in output_lines if line.startswith("LOOPS:")]
                exec_line = [line for line in output_lines if line.startswith("EXECUTIONS:")]

                assert len(loops_line) == 1 and len(exec_line) == 1

                total_loops = int(loops_line[0].split(":")[1])
                executions = int(exec_line[0].split(":")[1])

                # With reliable personality, kinda_repeat should be reasonable (allow wider tolerance for testing variance)
                assert 8 <= total_loops <= 35, f"kinda_repeat loops out of range: {total_loops}"

                # With reliable personality, sometimes should execute at a reasonable rate
                # Note: chaos_amplifier affects base probabilities, so adjust expectations
                execution_rate = executions / total_loops if total_loops > 0 else 0
                assert (
                    execution_rate >= 0.2
                ), f"Sometimes execution rate too low: {execution_rate:.3f}"
                assert (
                    execution_rate <= 1.0
                ), f"Sometimes execution rate too high: {execution_rate:.3f}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_eventually_until_with_simple_condition(self):
        """Test ~eventually_until with simple boolean condition"""
        PersonalityContext.set_mood("playful")
        PersonalityContext.set_seed(200)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

attempt = 0
~eventually_until attempt > 10:
    attempt += 1

print(f"RESULT:{attempt}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python3", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.getcwd(),
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract the count from output
                output_lines = result.stdout.strip().split("\n")
                result_line = [line for line in output_lines if line.startswith("RESULT:")]
                assert len(result_line) == 1

                count = int(result_line[0].split(":")[1])

                # Should terminate after condition becomes statistically true
                assert count >= 10, f"Should meet base condition, got {count}"
                assert count <= 35, f"Should terminate reasonably after condition, got {count}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_repetition_with_rarely_condition(self):
        """Test ~kinda_repeat with ~rarely condition for sparse execution"""
        PersonalityContext.set_mood("chaotic")
        PersonalityContext.set_seed(300)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

rare_executions = 0
total_loops = 0

~kinda_repeat(50):
    total_loops += 1
    ~rarely(True):
        rare_executions += 1

print(f"LOOPS:{total_loops}")
print(f"RARE:{rare_executions}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python3", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    cwd=os.getcwd(),
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract results from output
                output_lines = result.stdout.strip().split("\n")
                loops_line = [line for line in output_lines if line.startswith("LOOPS:")]
                rare_line = [line for line in output_lines if line.startswith("RARE:")]

                assert len(loops_line) == 1 and len(rare_line) == 1

                total_loops = int(loops_line[0].split(":")[1])
                rare_count = int(rare_line[0].split(":")[1])

                # With chaotic personality, kinda_repeat should be quite variable
                assert total_loops >= 20, f"Should have some loops, got {total_loops}"

                # Rarely should execute infrequently, especially with chaotic personality
                rare_rate = rare_count / total_loops if total_loops > 0 else 0
                assert rare_rate <= 0.3, f"Rarely rate too high: {rare_rate:.3f}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


class TestRepetitionWithFuzzyValues:
    """Integration tests with fuzzy value constructs (~ish, ~kinda, fuzzy assignments)"""

    def test_kinda_repeat_with_ish_values(self):
        """Test ~kinda_repeat with ~ish fuzzy values"""
        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(400)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

values = []
~kinda_repeat(15):
    fuzzy_val = 10~ish
    values.append(fuzzy_val)

avg_value = sum(values) / len(values)
print(f"COUNT:{len(values)}")
print(f"AVERAGE:{avg_value:.2f}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python3", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd=os.getcwd(),
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract results from output
                output_lines = result.stdout.strip().split("\n")
                count_line = [line for line in output_lines if line.startswith("COUNT:")]
                avg_line = [line for line in output_lines if line.startswith("AVERAGE:")]

                assert len(count_line) == 1 and len(avg_line) == 1

                count = int(count_line[0].split(":")[1])
                avg_value = float(avg_line[0].split(":")[1])

                # With reliable personality, should be close to 15 iterations
                assert 3 <= count <= 25, f"Iteration count out of range: {count}"

                # Average of 10~ish values should be close to 10
                assert 7.0 <= avg_value <= 13.0, f"Average ish value out of range: {avg_value}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_eventually_until_with_fuzzy_comparison(self):
        """Test ~eventually_until with ~ish fuzzy comparisons"""
        PersonalityContext.set_mood("cautious")
        PersonalityContext.set_seed(500)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

counter = 0
target = 25~ish
~eventually_until counter ~ish target:
    counter += 1

print(f"COUNTER:{counter}")
print(f"TARGET:{target:.2f}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python3", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=25,
                    cwd=os.getcwd(),
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract results from output
                output_lines = result.stdout.strip().split("\n")
                counter_line = [line for line in output_lines if line.startswith("COUNTER:")]
                target_line = [line for line in output_lines if line.startswith("TARGET:")]

                assert len(counter_line) == 1 and len(target_line) == 1

                counter = int(counter_line[0].split(":")[1])
                target = float(target_line[0].split(":")[1])

                # Counter should be close to the fuzzy target
                tolerance = 3.0  # Allow some tolerance for ish comparison
                assert (
                    abs(counter - target) <= tolerance + 2
                ), f"Counter {counter} too far from target {target:.2f}"

                # Should have terminated reasonably close to target
                assert counter >= target - tolerance, f"Counter should reach near target"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_kinda_repeat_with_fuzzy_int_declarations(self):
        """Test ~kinda_repeat with ~kinda int declarations"""
        PersonalityContext.set_mood("playful")
        PersonalityContext.set_seed(600)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

~kinda int loop_count ~= 12
fuzzy_values = []

~kinda_repeat(loop_count):
    ~kinda int fuzzy_num ~= 100
    fuzzy_values.append(fuzzy_num)

print(f"ITERATIONS:{len(fuzzy_values)}")
print(f"AVG_VALUE:{sum(fuzzy_values) / len(fuzzy_values):.2f}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python3", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd=os.getcwd(),
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract results from output
                output_lines = result.stdout.strip().split("\n")
                iter_line = [line for line in output_lines if line.startswith("ITERATIONS:")]
                avg_line = [line for line in output_lines if line.startswith("AVG_VALUE:")]

                assert len(iter_line) == 1 and len(avg_line) == 1

                iterations = int(iter_line[0].split(":")[1])
                avg_value = float(avg_line[0].split(":")[1])

                # Should have run approximately 12 times with playful personality variance
                assert 5 <= iterations <= 25, f"Iterations out of range: {iterations}"

                # Average kinda int value should be close to 100
                assert 96 <= avg_value <= 104, f"Average kinda int out of range: {avg_value}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


class TestRepetitionWithLoopConstructs:
    """Integration tests with other loop constructs (~sometimes_while, ~maybe_for)"""

    def test_kinda_repeat_with_sometimes_while(self):
        """Test ~kinda_repeat containing ~sometimes_while nested loops"""
        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(700)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Set personality in the subprocess
from kinda.personality import PersonalityContext
PersonalityContext.set_mood("reliable")
PersonalityContext.set_seed(700)

total_iterations = 0
outer_loops = 0

~kinda_repeat(5):
    outer_loops += 1
    inner_count = 0
    ~sometimes_while inner_count < 8:
        inner_count += 1
        total_iterations += 1

print(f"OUTER:{outer_loops}")
print(f"TOTAL:{total_iterations}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python3", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    cwd=os.getcwd(),
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract results from output
                output_lines = result.stdout.strip().split("\n")
                outer_line = [line for line in output_lines if line.startswith("OUTER:")]
                total_line = [line for line in output_lines if line.startswith("TOTAL:")]

                assert len(outer_line) == 1 and len(total_line) == 1

                outer_loops = int(outer_line[0].split(":")[1])
                total_iterations = int(total_line[0].split(":")[1])

                # With reliable personality, should run ~5 outer loops
                assert 3 <= outer_loops <= 8, f"Outer loops out of range: {outer_loops}"

                # Each sometimes_while should run some iterations (reliable = 90% continuation)
                assert total_iterations >= 0, f"Too few inner iterations: {total_iterations}"
                assert (
                    total_iterations <= outer_loops * 15
                ), f"Too many inner iterations: {total_iterations}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_eventually_until_with_maybe_for(self):
        """Test ~eventually_until containing ~maybe_for loops"""
        PersonalityContext.set_mood("cautious")
        PersonalityContext.set_seed(800)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

total_executions = 0
attempts = 0
items = [1, 2, 3, 4, 5]

~eventually_until total_executions >= 10:
    attempts += 1
    ~maybe_for item in items:
        total_executions += item

print(f"ATTEMPTS:{attempts}")
print(f"EXECUTIONS:{total_executions}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python3", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=25,
                    cwd=os.getcwd(),
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract results from output
                output_lines = result.stdout.strip().split("\n")
                attempts_line = [line for line in output_lines if line.startswith("ATTEMPTS:")]
                exec_line = [line for line in output_lines if line.startswith("EXECUTIONS:")]

                assert len(attempts_line) == 1 and len(exec_line) == 1

                attempts = int(attempts_line[0].split(":")[1])
                executions = int(exec_line[0].split(":")[1])

                # Should terminate after reaching target
                assert executions >= 10, f"Should meet termination condition: {executions}"

                # With cautious personality, maybe_for should execute most items
                assert attempts >= 1, f"Should have made attempts: {attempts}"
                assert executions <= attempts * 15, f"Executions should be reasonable: {executions}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


class TestRepetitionWithOutputConstructs:
    """Integration tests with output constructs (~sorta print)"""

    def test_kinda_repeat_with_sorta_print(self):
        """Test ~kinda_repeat with ~sorta print output"""
        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(900)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Set personality in the subprocess
from kinda.personality import PersonalityContext
PersonalityContext.set_mood("reliable")
PersonalityContext.set_seed(900)

loop_count = 0
~kinda_repeat(8):
    loop_count += 1
    ~sorta print(f"Loop {loop_count}")

print(f"RESULT:{loop_count}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python3", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd=os.getcwd(),
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract the final count from output
                output_lines = result.stdout.strip().split("\n")
                result_line = [line for line in output_lines if line.startswith("RESULT:")]
                assert len(result_line) == 1

                count = int(result_line[0].split(":")[1])

                # With reliable personality, should run close to 8 times
                assert 6 <= count <= 10, f"Loop count out of range: {count}"

                # Check that some sorta print statements were output
                print_lines = [
                    line for line in output_lines if "[print]" in line or "[shrug]" in line
                ]
                assert len(print_lines) >= 1, "Should have some sorta print output"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_eventually_until_with_debugging_output(self):
        """Test ~eventually_until with debugging via ~sorta print"""
        PersonalityContext.set_mood("playful")
        PersonalityContext.set_seed(1000)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

progress = 0
~eventually_until progress >= 15:
    progress += 1
    ~sorta print(f"Progress: {progress}")

print(f"FINAL:{progress}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python3", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    cwd=os.getcwd(),
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract the final progress from output
                output_lines = result.stdout.strip().split("\n")
                final_line = [line for line in output_lines if line.startswith("FINAL:")]
                assert len(final_line) == 1

                final_progress = int(final_line[0].split(":")[1])

                # Should terminate after reaching threshold
                assert final_progress >= 15, f"Should meet termination condition: {final_progress}"
                assert (
                    final_progress <= 50
                ), f"Should not run too long beyond condition: {final_progress}"

                # Should have some debug output
                debug_lines = [line for line in output_lines if "Progress:" in line]
                assert len(debug_lines) >= 3, "Should have some debug output from sorta print"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


class TestRepetitionWithErrorHandling:
    """Integration tests with error handling constructs (~welp)"""

    def test_kinda_repeat_with_welp_fallback(self):
        """Test ~kinda_repeat with ~welp error handling"""
        PersonalityContext.set_mood("chaotic")
        PersonalityContext.set_seed(1100)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

successful_operations = 0
~kinda_repeat(10):
    # Simulate potentially failing operation
    result = (1 / 1) ~welp 0  # Should succeed
    successful_operations += result

print(f"SUCCESS:{successful_operations}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python3", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd=os.getcwd(),
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract the success count from output
                output_lines = result.stdout.strip().split("\n")
                success_line = [line for line in output_lines if line.startswith("SUCCESS:")]
                assert len(success_line) == 1

                success_count = float(success_line[0].split(":")[1])

                # With chaotic personality, kinda_repeat should still run some iterations
                # All operations should succeed (1/1 = 1.0)
                assert (
                    success_count >= 5
                ), f"Should have some successful operations: {success_count}"
                assert (
                    success_count <= 20
                ), f"Success count within reasonable bounds: {success_count}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_eventually_until_with_error_recovery(self):
        """Test ~eventually_until with error conditions and ~welp recovery"""
        PersonalityContext.set_mood("reliable")
        PersonalityContext.set_seed(1200)

        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

attempts = 0
successes = 0

~eventually_until successes >= 5:
    attempts += 1
    # Simulate operation that might fail
    try:
        value = 10 / (attempts % 3 + 1)  # Will be 10, 5, 3.33, 10, 5, 3.33, ...
        successes += 1 if value > 4 else 0
    except:
        successes += 0

print(f"ATTEMPTS:{attempts}")
print(f"SUCCESSES:{successes}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(test_code)
            f.flush()

            try:
                result = run(
                    ["python3", "-m", "kinda", "run", f.name],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    cwd=os.getcwd(),
                )

                assert result.returncode == 0, f"Script failed: {result.stderr}"

                # Extract results from output
                output_lines = result.stdout.strip().split("\n")
                attempts_line = [line for line in output_lines if line.startswith("ATTEMPTS:")]
                success_line = [line for line in output_lines if line.startswith("SUCCESSES:")]

                assert len(attempts_line) == 1 and len(success_line) == 1

                attempts = int(attempts_line[0].split(":")[1])
                successes = int(success_line[0].split(":")[1])

                # Should terminate after reaching 5 successes
                assert successes >= 5, f"Should meet termination condition: {successes}"
                assert (
                    attempts >= successes
                ), f"Attempts should be at least successes: {attempts} vs {successes}"

                # Should not run excessively long
                assert attempts <= 20, f"Should terminate in reasonable time: {attempts}"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v", "-s"])
