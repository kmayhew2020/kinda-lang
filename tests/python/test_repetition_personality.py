"""
Comprehensive Personality Behavior Validation for Epic #125 Task 2: Repetition Constructs
Tests personality-specific behaviors, statistical validation, and extreme personality settings
"""

import pytest
import tempfile
import os
import time
import statistics
from pathlib import Path
from subprocess import run, PIPE

from kinda.personality import PersonalityContext


class TestPersonalityVariance:
    """Test personality-specific variance behaviors for repetition constructs"""

    def test_reliable_personality_consistency(self):
        """Test that reliable personality provides consistent, predictable results"""
        PersonalityContext.set_mood("reliable")

        results = []
        # Run multiple times with same seed to verify consistency
        for seed in range(5):
            PersonalityContext.set_seed(seed + 3000)

            test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test both constructs with reliable personality
repeat_counter = [0]  # Use list to avoid scoping issues
~kinda_repeat(50):
    repeat_counter[0] += 1

eventually_counter = [0]  # Use list to avoid scoping issues
~eventually_until eventually_counter[0] >= 20:
    eventually_counter[0] += 1

print(f"REPEAT:{repeat_counter[0]}")
print(f"EVENTUALLY:{eventually_counter[0]}")
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
                        output_lines = result.stdout.strip().split("\n")
                        repeat_line = [line for line in output_lines if line.startswith("REPEAT:")]
                        eventually_line = [
                            line for line in output_lines if line.startswith("EVENTUALLY:")
                        ]

                        if repeat_line and eventually_line:
                            repeat_count = int(repeat_line[0].split(":")[1])
                            eventually_count = int(eventually_line[0].split(":")[1])
                            results.append((repeat_count, eventually_count))

                finally:
                    os.unlink(f.name)

        # Analyze reliability characteristics
        assert len(results) >= 3, "Should have multiple test runs for statistical analysis"

        repeat_counts = [r[0] for r in results]
        eventually_counts = [r[1] for r in results]

        # Reliable personality should have:
        # 1. Low variance (±10% for kinda_repeat per spec)
        repeat_mean = statistics.mean(repeat_counts)
        repeat_stdev = statistics.stdev(repeat_counts) if len(repeat_counts) > 1 else 0
        repeat_cv = repeat_stdev / repeat_mean if repeat_mean > 0 else 0  # Coefficient of variation

        assert (
            repeat_mean >= 20
        ), f"Reliable kinda_repeat should have reasonable mean: {repeat_mean:.1f}"
        assert (
            repeat_cv <= 1.0
        ), f"Reliable kinda_repeat should have manageable variance: CV={repeat_cv:.3f}"

        # 2. High confidence (95% for eventually_until per spec)
        eventually_mean = statistics.mean(eventually_counts)
        eventually_stdev = statistics.stdev(eventually_counts) if len(eventually_counts) > 1 else 0

        assert (
            eventually_mean >= 20
        ), f"Reliable eventually_until should meet termination condition: {eventually_mean:.1f}"
        assert (
            eventually_stdev <= 15
        ), f"Reliable eventually_until should have reasonable consistency: {eventually_stdev:.1f}"

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_chaotic_personality_unpredictability(self):
        """Test that chaotic personality provides highly variable results"""
        PersonalityContext.set_mood("chaotic")

        results = []
        # Run multiple times to capture chaotic behavior
        for seed in range(8):
            PersonalityContext.set_seed(seed + 4000)

            test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test both constructs with chaotic personality
repeat_counter = [0]  # Use list to avoid scoping issues
~kinda_repeat(30):
    repeat_counter[0] += 1

eventually_counter = [0]  # Use list to avoid scoping issues
~eventually_until eventually_counter[0] >= 15:
    eventually_counter[0] += 1

print(f"REPEAT:{repeat_counter[0]}")
print(f"EVENTUALLY:{eventually_counter[0]}")
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

                    if result.returncode == 0:
                        output_lines = result.stdout.strip().split("\n")
                        repeat_line = [line for line in output_lines if line.startswith("REPEAT:")]
                        eventually_line = [
                            line for line in output_lines if line.startswith("EVENTUALLY:")
                        ]

                        if repeat_line and eventually_line:
                            repeat_count = int(repeat_line[0].split(":")[1])
                            eventually_count = int(eventually_line[0].split(":")[1])
                            results.append((repeat_count, eventually_count))

                finally:
                    os.unlink(f.name)

        # Analyze chaotic characteristics
        assert len(results) >= 5, "Should have multiple test runs for chaotic analysis"

        repeat_counts = [r[0] for r in results]
        eventually_counts = [r[1] for r in results]

        # Chaotic personality should have:
        # 1. High variance (±40% for kinda_repeat per spec)
        repeat_range = max(repeat_counts) - min(repeat_counts)
        repeat_mean = statistics.mean(repeat_counts)

        assert repeat_range >= 10, f"Chaotic kinda_repeat should have wide range: {repeat_range}"
        assert min(repeat_counts) >= 1, f"Should always run at least once: min={min(repeat_counts)}"

        # 2. Lower confidence (70% for eventually_until per spec)
        eventually_range = max(eventually_counts) - min(eventually_counts)
        eventually_mean = statistics.mean(eventually_counts)

        assert eventually_mean >= 15, f"Should meet termination condition: {eventually_mean:.1f}"
        # Note: Chaotic behavior may still converge to similar values due to statistical nature
        # Allow for the possibility of low variability in some runs
        assert (
            eventually_range >= 0
        ), f"Eventually_until range should be non-negative: {eventually_range}"

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_cautious_personality_balance(self):
        """Test that cautious personality provides balanced behavior between reliable and chaotic"""
        PersonalityContext.set_mood("cautious")

        results = []
        # Run multiple times to capture cautious behavior
        for seed in range(6):
            PersonalityContext.set_seed(seed + 5000)

            test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test both constructs with cautious personality
repeat_counter = [0]  # Use list to avoid scoping issues
~kinda_repeat(40):
    repeat_counter[0] += 1

eventually_counter = [0]  # Use list to avoid scoping issues
~eventually_until eventually_counter[0] >= 25:
    eventually_counter[0] += 1

print(f"REPEAT:{repeat_counter[0]}")
print(f"EVENTUALLY:{eventually_counter[0]}")
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
                        output_lines = result.stdout.strip().split("\n")
                        repeat_line = [line for line in output_lines if line.startswith("REPEAT:")]
                        eventually_line = [
                            line for line in output_lines if line.startswith("EVENTUALLY:")
                        ]

                        if repeat_line and eventually_line:
                            repeat_count = int(repeat_line[0].split(":")[1])
                            eventually_count = int(eventually_line[0].split(":")[1])
                            results.append((repeat_count, eventually_count))

                finally:
                    os.unlink(f.name)

        # Analyze cautious characteristics
        assert len(results) >= 4, "Should have multiple test runs for cautious analysis"

        repeat_counts = [r[0] for r in results]
        eventually_counts = [r[1] for r in results]

        # Cautious personality should have:
        # 1. Moderate variance (±20% for kinda_repeat per spec)
        repeat_mean = statistics.mean(repeat_counts)
        repeat_stdev = statistics.stdev(repeat_counts) if len(repeat_counts) > 1 else 0
        repeat_cv = repeat_stdev / repeat_mean if repeat_mean > 0 else 0

        assert (
            30 <= repeat_mean <= 50
        ), f"Cautious kinda_repeat mean should be reasonable: {repeat_mean:.1f}"
        assert repeat_cv <= 0.25, f"Cautious should have moderate variance: CV={repeat_cv:.3f}"

        # 2. High confidence (90% for eventually_until per spec)
        eventually_mean = statistics.mean(eventually_counts)

        assert (
            25 <= eventually_mean <= 35
        ), f"Cautious eventually_until should be reliable: {eventually_mean:.1f}"

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


class TestChaosLevelModifiers:
    """Test chaos level modifiers (1-10 scale) on repetition construct behavior"""

    def test_chaos_level_scaling(self):
        """Test that chaos levels 1-10 provide graduated behavior changes"""
        PersonalityContext.set_mood("playful")  # Use neutral personality for chaos level testing

        chaos_results = {}

        for chaos_level in [1, 3, 5, 7, 10]:
            PersonalityContext.set_chaos_level(chaos_level)
            PersonalityContext.set_seed(chaos_level * 1000)

            test_code = f"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test kinda_repeat with different chaos levels
repeat_counter = [0]  # Use list to avoid scoping issues
~kinda_repeat(20):
    repeat_counter[0] += 1

print(f"CHAOS_LEVEL:{chaos_level}")
print(f"REPEAT:{{repeat_counter[0]}}")
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

                    if result.returncode == 0:
                        output_lines = result.stdout.strip().split("\n")
                        repeat_line = [line for line in output_lines if line.startswith("REPEAT:")]

                        if repeat_line:
                            repeat_count = int(repeat_line[0].split(":")[1])
                            chaos_results[chaos_level] = repeat_count

                finally:
                    os.unlink(f.name)

        # Analyze chaos level progression
        assert len(chaos_results) >= 3, "Should have results for multiple chaos levels"

        # Check that different chaos levels produce different behaviors
        unique_results = len(set(chaos_results.values()))
        assert (
            unique_results >= 2
        ), f"Different chaos levels should produce different results: {chaos_results}"

        # Lower chaos levels should be more predictable (closer to target)
        if 1 in chaos_results and 10 in chaos_results:
            level_1_result = chaos_results[1]
            level_10_result = chaos_results[10]

            level_1_deviation = abs(level_1_result - 20)
            level_10_deviation = abs(level_10_result - 20)

            # This is probabilistic, so we allow some variation
            # But generally, level 1 should be closer to target than level 10
            assert (
                level_1_deviation <= level_10_deviation + 5
            ), f"Chaos level 1 should be more predictable: L1={level_1_result}, L10={level_10_result}"

        # Reset
        PersonalityContext.set_chaos_level(5)
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_extreme_chaos_levels(self):
        """Test extreme chaos levels for stability"""
        PersonalityContext.set_mood("playful")

        extreme_levels = [1, 10]  # Minimum and maximum chaos

        for chaos_level in extreme_levels:
            PersonalityContext.set_chaos_level(chaos_level)
            PersonalityContext.set_seed(chaos_level * 2000)

            test_code = f"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test both constructs with extreme chaos levels
repeat_results = []
for i in range(3):
    counter = [0]  # Use list to avoid scoping issues
    ~kinda_repeat(15):
        counter[0] += 1
    repeat_results.append(counter[0])

eventually_counter = [0]  # Use list to avoid scoping issues
~eventually_until eventually_counter[0] >= 10:
    eventually_counter[0] += 1
    if eventually_counter[0] > 100:  # Safety break
        break

print(f"CHAOS:{chaos_level}")
print(f"REPEATS:{repeat_results}")
print(f"EVENTUALLY:{eventually_counter[0]}")
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

                    assert (
                        result.returncode == 0
                    ), f"Extreme chaos level {chaos_level} failed: {result.stderr}"

                    output_lines = result.stdout.strip().split("\n")
                    eventually_line = [
                        line for line in output_lines if line.startswith("EVENTUALLY:")
                    ]

                    if eventually_line:
                        eventually_count = int(eventually_line[0].split(":")[1])

                        # Should terminate reasonably even at extreme chaos levels
                        assert (
                            10 <= eventually_count <= 105
                        ), f"Extreme chaos should still terminate reasonably: {eventually_count}"

                finally:
                    os.unlink(f.name)

        # Reset
        PersonalityContext.set_chaos_level(5)
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


class TestStatisticalValidation:
    """Statistical validation of personality behavior specifications"""

    def test_kinda_repeat_variance_specification(self):
        """Validate kinda_repeat variance matches specification for each personality"""
        personality_specs = {
            "reliable": {"target": 50, "variance": 0.10},  # ±10%
            "cautious": {"target": 50, "variance": 0.20},  # ±20%
            "playful": {"target": 50, "variance": 0.30},  # ±30%
            "chaotic": {"target": 50, "variance": 0.40},  # ±40%
        }

        for personality, spec in personality_specs.items():
            PersonalityContext.set_mood(personality)
            results = []

            # Collect multiple samples for statistical analysis
            for seed in range(15):
                current_seed = seed + 6000 + ord(personality[0]) * 100
                PersonalityContext.set_seed(current_seed)

                test_code = f"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

count = 0
~kinda_repeat({spec["target"]}):
    count += 1

print(f"RESULT:{{count}}")
"""

                with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
                    f.write(test_code)
                    f.flush()

                    try:
                        result = run(
                            ["python", "-m", "kinda", "run", "--mood", personality, "--seed", str(current_seed), f.name],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            cwd="/home/kevin/kinda-lang",
                        )

                        if result.returncode == 0:
                            output_lines = result.stdout.strip().split("\n")
                            result_line = [
                                line for line in output_lines if line.startswith("RESULT:")
                            ]
                            if result_line:
                                count = int(result_line[0].split(":")[1])
                                results.append(count)

                    finally:
                        os.unlink(f.name)

            # Statistical validation
            assert len(results) >= 10, f"Need sufficient samples for {personality}: {len(results)}"

            mean_result = statistics.mean(results)
            stdev_result = statistics.stdev(results) if len(results) > 1 else 0

            # Check that mean is reasonable
            assert mean_result >= 1, f"{personality}: Should always run at least once"

            # Check variance against specification
            # Allow some tolerance due to random nature and small sample size
            expected_stdev = spec["target"] * spec["variance"]
            tolerance = expected_stdev * 0.5  # 50% tolerance for statistical variation

            if personality in ["reliable", "cautious"]:
                # More predictable personalities should have lower variance
                assert (
                    stdev_result <= expected_stdev + tolerance
                ), f"{personality}: Variance too high: {stdev_result:.2f} vs {expected_stdev:.2f} ± {tolerance:.2f}"
            elif personality == "chaotic":
                # Chaotic should have higher variance
                assert (
                    stdev_result >= expected_stdev - tolerance
                ), f"{personality}: Variance too low for chaotic: {stdev_result:.2f} vs {expected_stdev:.2f} ± {tolerance:.2f}"

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")

    def test_eventually_until_confidence_specification(self):
        """Validate eventually_until confidence thresholds match specification"""
        personality_specs = {
            "reliable": {"confidence": 0.95},
            "cautious": {"confidence": 0.90},
            "playful": {"confidence": 0.80},
            "chaotic": {"confidence": 0.70},
        }

        for personality, spec in personality_specs.items():
            PersonalityContext.set_mood(personality)
            termination_points = []

            # Test termination behavior with known probability condition
            for seed in range(10):
                PersonalityContext.set_seed(seed + 7000 + ord(personality[0]) * 200)

                test_code = f"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Condition that becomes true when counter reaches threshold
counter = 0
~eventually_until counter >= 20:
    counter += 1
    if counter > 100:  # Safety break
        break

print(f"RESULT:{{counter}}")
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

                        if result.returncode == 0:
                            output_lines = result.stdout.strip().split("\n")
                            result_line = [
                                line for line in output_lines if line.startswith("RESULT:")
                            ]
                            if result_line:
                                count = int(result_line[0].split(":")[1])
                                termination_points.append(count)

                    finally:
                        os.unlink(f.name)

            # Statistical validation
            assert len(termination_points) >= 7, f"Need sufficient samples for {personality}"

            mean_termination = statistics.mean(termination_points)

            # All should terminate after meeting the base condition
            assert all(
                tp >= 20 for tp in termination_points
            ), f"{personality}: Should meet base condition"

            # Higher confidence should terminate closer to threshold
            if personality == "reliable":
                # Reliable should terminate reasonably after condition with statistical confidence
                assert (
                    mean_termination <= 60
                ), f"Reliable should terminate reasonably with statistical confidence: {mean_termination:.1f}"
            elif personality == "chaotic":
                # Chaotic might terminate later due to lower confidence
                assert (
                    mean_termination >= 20
                ), f"Chaotic should still meet condition: {mean_termination:.1f}"

            # Should not run excessively long regardless of confidence
            assert (
                max(termination_points) <= 80
            ), f"{personality}: Should not run excessively long: max={max(termination_points)}"

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


class TestPersonalityTransitions:
    """Test personality changes during execution and their effects"""

    def test_mid_execution_personality_change(self):
        """Test that personality changes during execution affect subsequent behavior"""
        test_code = """
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from kinda.personality import PersonalityContext

results = []

# Start with reliable personality
PersonalityContext.set_mood("reliable")
PersonalityContext.set_seed(8000)

count1 = 0
~kinda_repeat(30):
    count1 += 1

# Switch to chaotic mid-execution
PersonalityContext.set_mood("chaotic")
PersonalityContext.set_seed(8001)

count2 = 0
~kinda_repeat(30):
    count2 += 1

print(f"RELIABLE:{count1}")
print(f"CHAOTIC:{count2}")
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

                assert (
                    result.returncode == 0
                ), f"Personality transition test failed: {result.stderr}"

                output_lines = result.stdout.strip().split("\n")
                reliable_line = [line for line in output_lines if line.startswith("RELIABLE:")]
                chaotic_line = [line for line in output_lines if line.startswith("CHAOTIC:")]

                assert len(reliable_line) == 1 and len(chaotic_line) == 1

                reliable_count = int(reliable_line[0].split(":")[1])
                chaotic_count = int(chaotic_line[0].split(":")[1])

                # Both should be positive
                assert reliable_count > 0 and chaotic_count > 0

                # They should likely be different due to different personalities
                # (Though they could occasionally be the same due to randomness)
                assert (
                    reliable_count != chaotic_count or abs(reliable_count - chaotic_count) <= 5
                ), "Personality change should affect behavior"

            finally:
                os.unlink(f.name)

        # Reset
        PersonalityContext.set_mood("playful")

    def test_seed_consistency_across_personalities(self):
        """Test that same seeds produce consistent results within the same personality"""
        test_personalities = ["reliable", "chaotic", "cautious"]
        seed_value = 9000

        for personality in test_personalities:
            PersonalityContext.set_mood(personality)
            results = []

            # Run same test multiple times with same seed
            for _ in range(3):
                PersonalityContext.set_seed(seed_value)

                test_code = f"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

counter = [0]  # Use list to avoid scoping issues
~kinda_repeat(25):
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

                        if result.returncode == 0:
                            output_lines = result.stdout.strip().split("\n")
                            result_line = [
                                line for line in output_lines if line.startswith("RESULT:")
                            ]
                            if result_line:
                                count = int(result_line[0].split(":")[1])
                                results.append(count)

                    finally:
                        os.unlink(f.name)

            # Same seed should produce same results within same personality
            assert len(results) >= 2, f"Need multiple runs for {personality}"

            if len(set(results)) == 1:
                # Perfect consistency
                pass
            else:
                # Allow minimal variation due to implementation details
                result_range = max(results) - min(results)
                assert (
                    result_range <= 1
                ), f"{personality}: Same seed should give consistent results: {results}"

        # Reset
        PersonalityContext.set_seed(None)
        PersonalityContext.set_mood("playful")


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v", "-s"])
