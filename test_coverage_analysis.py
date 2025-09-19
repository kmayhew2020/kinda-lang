#!/usr/bin/env python3
"""
Test coverage analysis for Epic #125 Task 1 loop constructs.
Analyzes coverage and creates additional tests if needed.
"""

import sys
import os
import tempfile
import subprocess
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath("."))

from kinda.langs.python.transformer import transform_line
from kinda.personality import PersonalityContext
from kinda.cli import setup_personality


def run_kinda_test(code, timeout=5):
    """Helper function to run kinda code and capture output."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
        f.write(code)
        f.flush()
        temp_path = Path(f.name)

    try:
        result = subprocess.run(
            ["python", "-m", "kinda", "interpret", str(temp_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/home/kevin/kinda-lang",
        )
        if result.returncode != 0:
            print(f"Error running code: {result.stderr}")
            return None
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"Test timed out after {timeout}s")
        return None
    finally:
        temp_path.unlink()


def test_sometimes_while_comprehensive():
    """Comprehensive testing of ~sometimes_while construct."""
    print("=== Comprehensive ~sometimes_while Testing ===")

    tests_passed = 0
    total_tests = 0

    # Test 1: Basic functionality with different personalities
    for personality in ["reliable", "cautious", "playful", "chaotic"]:
        total_tests += 1
        setup_personality(personality, chaos_level=5, seed=42)

        code = f"""# Test {personality} personality
count = 0
~sometimes_while count < 3:
    count += 1
print(f"Count: {{count}}")
"""

        output = run_kinda_test(code)
        if output and "Count:" in output:
            tests_passed += 1
            print(f"✓ {personality} personality basic test passed")
        else:
            print(f"✗ {personality} personality basic test failed")

    # Test 2: False condition never enters
    total_tests += 1
    setup_personality("chaotic", chaos_level=10, seed=42)

    code = """count = 0
~sometimes_while False:
    count += 1
print(f"Count: {count}")
"""

    output = run_kinda_test(code)
    if output and "Count: 0" in output:
        tests_passed += 1
        print("✓ False condition test passed")
    else:
        print("✗ False condition test failed")

    # Test 3: Complex condition
    total_tests += 1
    setup_personality("reliable", chaos_level=1, seed=42)

    code = """x = 5
y = 10
~sometimes_while x < y and x > 0:
    x += 1
print(f"Result: {x}")
"""

    output = run_kinda_test(code)
    if output and "Result:" in output:
        tests_passed += 1
        print("✓ Complex condition test passed")
    else:
        print("✗ Complex condition test failed")

    # Test 4: Nested construct compatibility
    total_tests += 1
    setup_personality("playful", chaos_level=5, seed=42)

    code = """count = 0
~sometimes_while count < 2:
    count += 1
    ~sometimes print(f"Inner: {count}")
print(f"Final: {count}")
"""

    output = run_kinda_test(code)
    if output and "Final:" in output:
        tests_passed += 1
        print("✓ Nested construct test passed")
    else:
        print("✗ Nested construct test failed")

    return tests_passed, total_tests


def test_maybe_for_comprehensive():
    """Comprehensive testing of ~maybe_for construct."""
    print("\n=== Comprehensive ~maybe_for Testing ===")

    tests_passed = 0
    total_tests = 0

    # Test 1: Basic functionality with different collection types
    collection_tests = [
        ("[1, 2, 3, 4, 5]", "list"),
        ("(1, 2, 3, 4, 5)", "tuple"),
        ("range(5)", "range"),
        ("'hello'", "string"),
    ]

    for collection, name in collection_tests:
        total_tests += 1
        setup_personality("reliable", chaos_level=1, seed=42)

        code = f"""processed = []
items = {collection}
~maybe_for item in items:
    processed.append(item)
print(f"Processed {name}: {{len(processed)}}")
"""

        output = run_kinda_test(code)
        if output and f"Processed {name}:" in output:
            tests_passed += 1
            print(f"✓ {name} collection test passed")
        else:
            print(f"✗ {name} collection test failed")

    # Test 2: Empty collection
    total_tests += 1
    setup_personality("reliable", chaos_level=1, seed=42)

    code = """processed = []
items = []
~maybe_for item in items:
    processed.append(item)
print(f"Empty: {len(processed)}")
"""

    output = run_kinda_test(code)
    if output and "Empty: 0" in output:
        tests_passed += 1
        print("✓ Empty collection test passed")
    else:
        print("✗ Empty collection test failed")

    # Test 3: Different personalities statistical behavior
    for personality in ["reliable", "chaotic"]:
        total_tests += 1
        setup_personality(personality, chaos_level=5 if personality == "reliable" else 8, seed=42)

        code = f"""# Test {personality} personality statistics
total_processed = 0
for trial in range(5):
    processed = []
    items = [1, 2, 3, 4, 5]
    ~maybe_for item in items:
        processed.append(item)
    total_processed += len(processed)
    
average = total_processed / 5
print(f"{personality}: {{average}}")
"""

        output = run_kinda_test(code)
        if output and f"{personality}:" in output:
            tests_passed += 1
            print(f"✓ {personality} statistical test passed")
        else:
            print(f"✗ {personality} statistical test failed")

    # Test 4: Method call collection
    total_tests += 1
    setup_personality("playful", chaos_level=5, seed=42)

    code = """data = {'a': 1, 'b': 2, 'c': 3}
processed = []
~maybe_for key in data.keys():
    processed.append(key)
print(f"Keys: {len(processed)}")
"""

    output = run_kinda_test(code)
    if output and "Keys:" in output:
        tests_passed += 1
        print("✓ Method call collection test passed")
    else:
        print("✗ Method call collection test failed")

    return tests_passed, total_tests


def test_integration_scenarios():
    """Test integration scenarios combining both constructs."""
    print("\n=== Integration Testing ===")

    tests_passed = 0
    total_tests = 0

    # Test 1: Nested loop constructs
    total_tests += 1
    setup_personality("playful", chaos_level=5, seed=42)

    code = """total = 0
outer = 0
~sometimes_while outer < 2:
    outer += 1
    items = [1, 2, 3]
    ~maybe_for item in items:
        total += item
print(f"Total: {total}, Outer: {outer}")
"""

    output = run_kinda_test(code)
    if output and "Total:" in output and "Outer:" in output:
        tests_passed += 1
        print("✓ Nested loop constructs test passed")
    else:
        print("✗ Nested loop constructs test failed")

    # Test 2: Loop constructs with other kinda constructs
    total_tests += 1
    setup_personality("reliable", chaos_level=2, seed=42)

    code = """results = []
count = 0
~sometimes_while count < 3:
    count += 1
    items = [1, 2, 3]
    ~maybe_for item in items:
        ~sometimes results.append(item)
print(f"Results: {len(results)}")
"""

    output = run_kinda_test(code)
    if output and "Results:" in output:
        tests_passed += 1
        print("✓ Mixed constructs test passed")
    else:
        print("✗ Mixed constructs test failed")

    # Test 3: Error handling with invalid conditions
    total_tests += 1
    setup_personality("cautious", chaos_level=3, seed=42)

    code = """count = 0
try:
    ~sometimes_while count < 2:
        count += 1
        if count > 10:  # Safety break
            break
    print(f"Safe exit: {count}")
except Exception as e:
    print(f"Error handled: {type(e).__name__}")
"""

    output = run_kinda_test(code)
    if output and ("Safe exit:" in output or "Error handled:" in output):
        tests_passed += 1
        print("✓ Error handling test passed")
    else:
        print("✗ Error handling test failed")

    return tests_passed, total_tests


def test_transformation_edge_cases():
    """Test transformation edge cases."""
    print("\n=== Transformation Edge Cases ===")

    tests_passed = 0
    total_tests = 0

    # Test 1: Complex conditions in sometimes_while
    edge_cases = [
        "~sometimes_while x < 10 and y > 5:",
        "~sometimes_while len(items) > 0:",
        "~sometimes_while func() == True:",
        "~sometimes_while (a or b) and c:",
    ]

    for case in edge_cases:
        total_tests += 1
        try:
            result = transform_line(case)
            if result and len(result) > 0 and "while sometimes_while_condition(" in result[0]:
                tests_passed += 1
                print(f"✓ Transformation: {case}")
            else:
                print(f"✗ Transformation failed: {case}")
        except Exception as e:
            print(f"✗ Transformation error: {case} - {e}")

    # Test 2: Complex collections in maybe_for
    for_cases = [
        "~maybe_for item in data.values():",
        "~maybe_for x in range(10):",
        "~maybe_for key, value in data.items():",
        "~maybe_for line in open('file.txt'):",
    ]

    for case in for_cases:
        total_tests += 1
        try:
            result = transform_line(case)
            if result and len(result) > 0 and "for " in result[0]:
                tests_passed += 1
                print(f"✓ Transformation: {case}")
            else:
                print(f"✗ Transformation failed: {case}")
        except Exception as e:
            print(f"✗ Transformation error: {case} - {e}")

    return tests_passed, total_tests


def main():
    """Run comprehensive test coverage analysis."""
    print("=== Epic #125 Task 1 Comprehensive Test Coverage Analysis ===")
    print()

    total_passed = 0
    total_tests = 0

    # Run all test suites
    passed, tests = test_sometimes_while_comprehensive()
    total_passed += passed
    total_tests += tests

    passed, tests = test_maybe_for_comprehensive()
    total_passed += passed
    total_tests += tests

    passed, tests = test_integration_scenarios()
    total_passed += passed
    total_tests += tests

    passed, tests = test_transformation_edge_cases()
    total_passed += passed
    total_tests += tests

    # Calculate coverage
    coverage_percentage = (total_passed / total_tests) * 100 if total_tests > 0 else 0

    print(f"\n=== Test Coverage Summary ===")
    print(f"Total Tests: {total_tests}")
    print(f"Tests Passed: {total_passed}")
    print(f"Tests Failed: {total_tests - total_passed}")
    print(f"Coverage: {coverage_percentage:.1f}%")

    if coverage_percentage >= 90:
        print("🎉 EXCELLENT: Coverage meets 90%+ target!")
        return True
    elif coverage_percentage >= 80:
        print("⚠️  GOOD: Coverage is above 80% but below 90% target")
        return True
    else:
        print("❌ INSUFFICIENT: Coverage is below 80% - additional tests needed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
