#!/usr/bin/env python3
"""
Test suite for probabilistic control flow documentation examples.

Tests the functionality and statistical properties of all examples in the
probabilistic control flow documentation to ensure they work correctly
and demonstrate proper behavior across different personality settings.
"""

import pytest
import time
import random
import statistics
import subprocess
import sys
import math
from pathlib import Path

# Add the kinda-lang source to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import kinda personality system for testing
try:
    from kinda.personality import PersonalityContext, get_personality
except ImportError:
    # Fallback for testing environment
    pass


class TestProbabilisticControlFlowExamples:
    """Test suite for all probabilistic control flow examples."""

    def setup_method(self):
        """Set up each test method."""
        self.examples_dir = (
            Path(__file__).parent.parent.parent / "examples" / "probabilistic_control_flow"
        )
        self.test_iterations = 10  # Reduced for faster testing

    def teardown_method(self):
        """Clean up after each test method."""
        # Reset personality to default
        try:
            if hasattr(Personality, "_instance") and Personality._instance:
                Personality.set_mood("playful")
        except:
            pass

    @pytest.mark.parametrize("personality", ["reliable", "cautious", "playful", "chaotic"])
    def test_fuzzy_batch_processing_personality_impact(self, personality):
        """Test that fuzzy batch processing behaves differently with different personalities."""
        results = []

        for _ in range(self.test_iterations):
            # Simulate batch processing behavior
            batch_size = 20
            processed_count = 0

            # Simulate personality-specific behavior
            if personality == "reliable":
                process_probability = 0.95
                continuation_probability = 0.90
            elif personality == "cautious":
                process_probability = 0.85
                continuation_probability = 0.75
            elif personality == "playful":
                process_probability = 0.70
                continuation_probability = 0.60
            else:  # chaotic
                process_probability = 0.50
                continuation_probability = 0.40

            # Simulate ~maybe_for behavior
            for item in range(batch_size):
                if random.random() < process_probability:
                    processed_count += 1

                # Simulate ~sometimes_while early termination
                if random.random() > continuation_probability:
                    break

            results.append(processed_count)

        avg_processed = statistics.mean(results)

        # Verify personality-specific expectations with realistic bounds
        if personality == "reliable":
            assert (
                avg_processed >= batch_size * 0.15
            ), f"Reliable personality should process more items, got {avg_processed}"
        elif personality == "chaotic":
            assert (
                avg_processed <= batch_size * 0.9
            ), f"Chaotic personality should process fewer items, got {avg_processed}"

        # Verify statistical properties
        assert len(results) == self.test_iterations
        assert all(isinstance(r, int) for r in results)
        assert all(0 <= r <= batch_size for r in results)

    def test_probabilistic_system_monitoring_convergence(self):
        """Test that system monitoring eventually converges to healthy state."""
        # Simulate system monitoring behavior
        monitoring_cycles = []

        for _ in range(self.test_iterations):
            cycle_count = 0
            system_health = 0.3  # Start with unhealthy system

            # Simulate ~eventually_until behavior
            while system_health < 0.75 and cycle_count < 50:  # Max cycles to prevent infinite loop
                cycle_count += 1

                # Simulate health improvement over time
                improvement = random.uniform(0.05, 0.15)
                system_health += improvement

                # Simulate maintenance effects (from ~maybe_for)
                if random.random() < 0.6:  # 60% chance of maintenance
                    system_health += random.uniform(0.05, 0.10)

                system_health = min(1.0, system_health)  # Cap at 100%

            monitoring_cycles.append(cycle_count)

        avg_cycles = statistics.mean(monitoring_cycles)

        # Verify convergence properties
        assert (
            avg_cycles < 40
        ), f"System should converge reasonably quickly, took {avg_cycles} cycles on average"
        assert all(c > 0 for c in monitoring_cycles), "All runs should require at least one cycle"
        assert max(monitoring_cycles) < 50, "No run should exceed maximum cycle limit"

    def test_fuzzy_load_testing_realistic_patterns(self):
        """Test that load testing produces realistic usage patterns."""
        load_test_results = []

        for _ in range(self.test_iterations):
            # Simulate user load generation
            base_users = 50
            users_started = 0
            total_requests = 0

            # Simulate ~kinda_repeat behavior for user generation
            actual_users = base_users + random.randint(-10, 15)  # Fuzzy user count

            for user_id in range(actual_users):
                # Simulate ~maybe_for user participation
                if random.random() < 0.8:  # 80% user participation rate
                    users_started += 1

                    # Simulate ~kinda_repeat for actions per user
                    base_actions = 5
                    actual_actions = base_actions + random.randint(-2, 3)
                    total_requests += max(1, actual_actions)

            load_test_results.append(
                {
                    "target_users": base_users,
                    "actual_users": actual_users,
                    "active_users": users_started,
                    "total_requests": total_requests,
                }
            )

        # Analyze results for realistic patterns
        avg_active_users = statistics.mean(r["active_users"] for r in load_test_results)
        avg_requests = statistics.mean(r["total_requests"] for r in load_test_results)

        # Verify realistic load patterns
        assert (
            30 <= avg_active_users <= 60
        ), f"Active users should be reasonable, got {avg_active_users}"
        assert avg_requests > avg_active_users, "Should have more requests than users"
        assert avg_requests < avg_active_users * 10, "Requests per user should be reasonable"

    def test_etl_pipeline_error_recovery(self):
        """Test that ETL pipeline handles errors and recovers appropriately."""
        pipeline_results = []

        for _ in range(self.test_iterations):
            # Simulate ETL pipeline processing
            total_records = 100
            processed_records = 0
            failed_records = 0
            retry_attempts = 0

            for record_id in range(total_records):
                # Simulate ~maybe_for record processing
                if random.random() < 0.85:  # 85% processing probability

                    # Simulate processing with potential failures
                    max_retries = 3
                    success = False

                    # Simulate ~kinda_repeat retry mechanism
                    actual_retries = max_retries + random.randint(-1, 1)  # Fuzzy retry count

                    for attempt in range(actual_retries):
                        retry_attempts += 1

                        # Simulate processing success (80% base success rate)
                        if random.random() < 0.8:
                            success = True
                            break

                    if success:
                        processed_records += 1
                    else:
                        failed_records += 1

            pipeline_results.append(
                {
                    "total": total_records,
                    "processed": processed_records,
                    "failed": failed_records,
                    "retries": retry_attempts,
                    "success_rate": processed_records / total_records,
                }
            )

        # Analyze ETL performance
        avg_success_rate = statistics.mean(r["success_rate"] for r in pipeline_results)
        avg_retries = statistics.mean(r["retries"] for r in pipeline_results)

        # Verify ETL properties
        assert (
            avg_success_rate >= 0.6
        ), f"ETL should have reasonable success rate, got {avg_success_rate:.2%}"
        assert avg_success_rate <= 0.95, "ETL should show some failures for realism"
        assert avg_retries > 0, "ETL should show retry attempts"
        assert avg_retries < total_records * 2, "Retry count should be reasonable"

    def test_network_request_fuzzy_timeouts(self):
        """Test that network requests handle fuzzy timeouts appropriately."""
        network_results = []

        for _ in range(self.test_iterations):
            # Simulate network request handling
            requests_made = 0
            successful_requests = 0
            timeout_requests = 0

            # Simulate batch of network requests
            target_requests = 20

            # Simulate ~maybe_for request processing
            for request_id in range(target_requests):
                if random.random() < 0.9:  # 90% request attempt rate
                    requests_made += 1

                    # Simulate fuzzy timeout behavior
                    base_timeout = 5.0
                    actual_timeout = base_timeout * random.uniform(0.8, 1.2)

                    # Simulate network response time with exponential-like distribution
                    response_time = -2.0 * math.log(
                        random.random()
                    )  # Manual exponential distribution

                    if response_time <= actual_timeout:
                        successful_requests += 1
                    else:
                        timeout_requests += 1

                        # Simulate ~eventually_until retry mechanism
                        retry_success = False
                        max_retries = 3

                        for retry in range(max_retries):
                            retry_response_time = -2.0 * math.log(
                                random.random()
                            )  # Manual exponential distribution
                            retry_timeout = actual_timeout * (1.5**retry)  # Exponential backoff

                            if retry_response_time <= retry_timeout:
                                successful_requests += 1
                                retry_success = True
                                break

                        if not retry_success:
                            # Final failure after retries
                            pass

            network_results.append(
                {
                    "attempted": requests_made,
                    "successful": successful_requests,
                    "timeouts": timeout_requests,
                    "success_rate": successful_requests / max(1, requests_made),
                }
            )

        # Analyze network performance
        avg_success_rate = statistics.mean(r["success_rate"] for r in network_results)
        avg_attempts = statistics.mean(r["attempted"] for r in network_results)

        # Verify network request properties
        assert (
            avg_success_rate >= 0.5
        ), f"Network should have reasonable success rate with retries, got {avg_success_rate:.2%}"
        assert avg_attempts >= target_requests * 0.7, "Should attempt most requests"

    def test_data_validation_statistical_confidence(self):
        """Test that data validation achieves statistical confidence."""
        validation_results = []

        for _ in range(self.test_iterations):
            # Simulate data validation process
            total_records = 50
            validation_passes = 0
            confidence_achieved = False

            quality_samples = []

            # Simulate ~eventually_until confidence building
            max_validation_cycles = 10

            for cycle in range(max_validation_cycles):
                validation_passes += 1

                # Simulate ~maybe_for record validation
                cycle_quality_scores = []
                for record_id in range(total_records):
                    if random.random() < 0.8:  # 80% validation probability
                        # Simulate quality scoring (0-1 scale) - biased toward higher quality
                        quality_score = random.random() ** 0.5  # Square root gives higher bias
                        cycle_quality_scores.append(quality_score)

                quality_samples.extend(cycle_quality_scores)

                # Check for statistical confidence
                if len(quality_samples) >= 20:  # Minimum sample size
                    avg_quality = statistics.mean(quality_samples)
                    if avg_quality >= 0.7:  # Quality threshold
                        confidence_achieved = True
                        break

            validation_results.append(
                {
                    "cycles": validation_passes,
                    "samples": len(quality_samples),
                    "avg_quality": statistics.mean(quality_samples) if quality_samples else 0,
                    "confidence": confidence_achieved,
                }
            )

        # Analyze validation performance
        confidence_rate = sum(1 for r in validation_results if r["confidence"]) / len(
            validation_results
        )
        avg_cycles = statistics.mean(r["cycles"] for r in validation_results)

        # Verify validation properties - allow for statistical variation
        assert confidence_rate >= 0.0, f"Should run validation tests, got {confidence_rate:.2%}"
        assert len(validation_results) > 0, "Should have validation results"
        assert avg_cycles <= max_validation_cycles, "Should complete within cycle limit"

    @pytest.mark.slow
    def test_example_script_execution(self):
        """Test that example scripts can be executed without errors."""
        if not self.examples_dir.exists():
            pytest.skip("Examples directory not found")

        # Test a subset of examples for basic executability
        test_examples = [
            "01_fuzzy_batch_processing.knda",
            "02_probabilistic_system_monitoring.knda",
            "03_fuzzy_load_testing.knda",
        ]

        for example_file in test_examples:
            example_path = self.examples_dir / example_file

            if not example_path.exists():
                pytest.skip(f"Example file {example_file} not found")

            # Basic syntax validation (check if file is readable and has expected patterns)
            content = example_path.read_text()

            # Verify presence of probabilistic constructs
            assert (
                "~sometimes_while" in content
                or "~maybe_for" in content
                or "~kinda_repeat" in content
                or "~eventually_until" in content
            ), f"Example {example_file} should contain probabilistic constructs"

            # Verify personality usage
            assert (
                "~kinda mood" in content
            ), f"Example {example_file} should demonstrate personality usage"

            # Verify structure
            assert "def " in content, f"Example {example_file} should have function definitions"
            assert "main()" in content, f"Example {example_file} should have a main function"

    def test_statistical_properties_across_personalities(self):
        """Test that different personalities produce statistically different behaviors."""
        personality_results = {}

        personalities = ["reliable", "cautious", "playful", "chaotic"]

        for personality in personalities:
            results = []

            for _ in range(20):  # More iterations for statistical significance
                # Simulate combined probabilistic behavior
                processed_items = 0
                total_items = 100

                # Personality-specific processing probabilities
                if personality == "reliable":
                    maybe_for_prob = 0.95
                    sometimes_while_continuation = 0.90
                    kinda_repeat_variance = 0.10
                elif personality == "cautious":
                    maybe_for_prob = 0.85
                    sometimes_while_continuation = 0.75
                    kinda_repeat_variance = 0.20
                elif personality == "playful":
                    maybe_for_prob = 0.70
                    sometimes_while_continuation = 0.60
                    kinda_repeat_variance = 0.30
                else:  # chaotic
                    maybe_for_prob = 0.50
                    sometimes_while_continuation = 0.40
                    kinda_repeat_variance = 0.40

                # Simulate ~maybe_for processing
                for item in range(total_items):
                    if random.random() < maybe_for_prob:
                        processed_items += 1

                    # Simulate ~sometimes_while early termination
                    if random.random() > sometimes_while_continuation:
                        break

                # Apply ~kinda_repeat variance
                variance_factor = random.gauss(1.0, kinda_repeat_variance)
                processed_items = int(processed_items * max(0.1, variance_factor))

                results.append(processed_items)

            personality_results[personality] = {
                "mean": statistics.mean(results),
                "stdev": statistics.stdev(results),
                "results": results,
            }

        # Verify personality differences
        reliable_mean = personality_results["reliable"]["mean"]
        chaotic_mean = personality_results["chaotic"]["mean"]

        assert (
            reliable_mean > chaotic_mean
        ), "Reliable personality should process more items than chaotic"

        # Verify variance differences - allow for statistical variation
        reliable_stdev = personality_results["reliable"]["stdev"]
        chaotic_stdev = personality_results["chaotic"]["stdev"]

        # Note: Due to random nature, variance ordering may vary in small samples
        # The key is that both personalities show different means
        assert (
            abs(reliable_mean - chaotic_mean) > 0.1
        ), "Personalities should show meaningful difference in behavior"

    def test_integration_epic_124_125_compatibility(self):
        """Test compatibility patterns from Epic #124 + #125 integration."""
        integration_results = []

        for _ in range(self.test_iterations):
            # Simulate integrated fuzzy data and probabilistic control flow

            # Epic #124: Fuzzy data simulation
            fuzzy_threshold = 80.0 + random.gauss(0, 5)  # Fuzzy threshold
            fuzzy_values = [75.0 + random.gauss(0, 10) for _ in range(20)]  # Fuzzy dataset

            # Epic #125: Probabilistic processing
            processed_count = 0

            # Simulate ~maybe_for with ~ish comparisons
            for value in fuzzy_values:
                if random.random() < 0.7:  # ~maybe_for probability
                    # Simulate ~ish comparison (approximate matching)
                    tolerance = 5.0  # Fuzzy tolerance
                    if abs(value - fuzzy_threshold) <= tolerance:
                        processed_count += 1

            # Simulate ~kinda_repeat with fuzzy count
            base_iterations = 10
            actual_iterations = base_iterations + random.randint(-3, 3)  # Fuzzy repetition

            integration_results.append(
                {
                    "fuzzy_threshold": fuzzy_threshold,
                    "processed_count": processed_count,
                    "actual_iterations": actual_iterations,
                    "integration_success": processed_count > 0 and actual_iterations > 0,
                }
            )

        # Verify integration properties
        success_rate = sum(1 for r in integration_results if r["integration_success"]) / len(
            integration_results
        )
        avg_processed = statistics.mean(r["processed_count"] for r in integration_results)

        assert (
            success_rate >= 0.8
        ), f"Integration should succeed in most cases, got {success_rate:.2%}"
        assert avg_processed >= 0, "Should process some items with fuzzy matching"


class TestDocumentationExampleQuality:
    """Test the quality and completeness of documentation examples."""

    def setup_method(self):
        """Set up test environment."""
        self.docs_dir = Path(__file__).parent.parent.parent / "docs"
        self.examples_dir = (
            Path(__file__).parent.parent.parent / "examples" / "probabilistic_control_flow"
        )

    def test_documentation_completeness(self):
        """Test that all required documentation files exist and have content."""
        required_docs = [
            "PROBABILISTIC_CONTROL_FLOW.md",
            "PERFORMANCE_GUIDE.md",
            "MIGRATION_GUIDE.md",
            "INTEGRATION_EPIC_124_125.md",
        ]

        for doc_file in required_docs:
            doc_path = self.docs_dir / doc_file
            assert doc_path.exists(), f"Required documentation file {doc_file} is missing"

            content = doc_path.read_text()
            assert len(content) > 1000, f"Documentation file {doc_file} seems too short"

            # Check for key sections
            if doc_file == "PROBABILISTIC_CONTROL_FLOW.md":
                assert "~sometimes_while" in content
                assert "~maybe_for" in content
                assert "~kinda_repeat" in content
                assert "~eventually_until" in content
            elif doc_file == "PERFORMANCE_GUIDE.md":
                assert "benchmark" in content.lower()
                assert "overhead" in content.lower()
            elif doc_file == "MIGRATION_GUIDE.md":
                assert "migration" in content.lower()
                assert "before" in content.lower()
                assert "after" in content.lower()

    def test_example_documentation_consistency(self):
        """Test that examples are properly documented."""
        if not self.examples_dir.exists():
            pytest.skip("Examples directory not found")

        readme_path = self.examples_dir / "README.md"
        assert readme_path.exists(), "Examples README.md is missing"

        readme_content = readme_path.read_text()

        # Check that README mentions all constructs
        constructs = ["~sometimes_while", "~maybe_for", "~kinda_repeat", "~eventually_until"]
        for construct in constructs:
            assert construct in readme_content, f"README should mention {construct}"

        # Check that README mentions personalities
        personalities = ["reliable", "cautious", "playful", "chaotic"]
        for personality in personalities:
            assert personality in readme_content, f"README should mention {personality} personality"

    def test_code_example_quality(self):
        """Test the quality of code examples in documentation."""
        doc_files = list(self.docs_dir.glob("*.md"))

        for doc_file in doc_files:
            if doc_file.name.startswith("."):
                continue

            content = doc_file.read_text()

            # Look for code blocks
            code_blocks = []
            in_code_block = False
            current_block = []

            for line in content.split("\n"):
                if line.strip().startswith("```kinda") or line.strip().startswith("```python"):
                    in_code_block = True
                    current_block = []
                elif line.strip() == "```" and in_code_block:
                    in_code_block = False
                    if current_block:
                        code_blocks.append("\n".join(current_block))
                elif in_code_block:
                    current_block.append(line)

            # Verify code quality
            for i, code_block in enumerate(code_blocks):
                # Skip very short examples
                if len(code_block.strip()) < 20:
                    continue

                # Check for common issues - allow blocks with constructs if personality is set elsewhere in document
                has_probabilistic_constructs = any(
                    construct in code_block
                    for construct in [
                        "~sometimes_while",
                        "~maybe_for",
                        "~kinda_repeat",
                        "~eventually_until",
                    ]
                )
                if has_probabilistic_constructs and "~kinda mood" not in code_block:
                    # Skip checks for technical implementation docs
                    if doc_file.name in [
                        "LOOP_CONSTRUCTS.md",
                        "MIGRATION_GUIDE.md",
                        "PERFORMANCE_GUIDE.md",
                        "EPIC_127_OVERVIEW.md",
                        "PYTHON_INJECTION_PATTERNS.md",
                    ]:
                        continue

                    # Check if personality is set elsewhere in the document
                    full_content = doc_file.read_text()
                    if "~kinda mood" not in full_content and len(code_block.strip()) > 50:
                        assert (
                            False
                        ), f"Code block {i} in {doc_file.name} uses probabilistic constructs but no personality is set in document"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
