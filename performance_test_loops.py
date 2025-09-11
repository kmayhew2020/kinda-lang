#!/usr/bin/env python3
"""
Performance testing for Epic #125 Task 1 loop constructs.
Validates that performance overhead is <15% compared to standard loops.
"""

import sys
import os
import time
import tempfile
import subprocess
from pathlib import Path
import statistics

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath("."))

from kinda.cli import setup_personality


def run_kinda_code(code, timeout=10):
    """Run kinda code and measure execution time."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
        f.write(code)
        f.flush()
        temp_path = Path(f.name)

    try:
        start_time = time.time()
        result = subprocess.run(
            ["python", "-m", "kinda", "interpret", str(temp_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/home/kevin/kinda-lang",
        )
        end_time = time.time()

        if result.returncode != 0:
            print(f"Error running code: {result.stderr}")
            return None

        return end_time - start_time
    except subprocess.TimeoutExpired:
        print(f"Test timed out after {timeout}s")
        return None
    finally:
        temp_path.unlink()


def run_python_code(code, timeout=10):
    """Run pure Python code and measure execution time."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        temp_path = Path(f.name)

    try:
        start_time = time.time()
        result = subprocess.run(
            ["python", str(temp_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/home/kevin/kinda-lang",
        )
        end_time = time.time()

        if result.returncode != 0:
            print(f"Error running Python code: {result.stderr}")
            return None

        return end_time - start_time
    except subprocess.TimeoutExpired:
        print(f"Python test timed out after {timeout}s")
        return None
    finally:
        temp_path.unlink()


def benchmark_sometimes_while():
    """Benchmark ~sometimes_while vs standard while loop."""
    print("=== Benchmarking ~sometimes_while ===")

    # Set up reliable personality for consistent performance
    setup_personality("reliable", chaos_level=1, seed=42)

    # Kinda code with ~sometimes_while
    kinda_code = """
import time
count = 0
iterations = 0
start = time.time()
~sometimes_while count < 1000:
    count += 1
    iterations += 1
    if iterations > 2000:  # Safety break
        break
end = time.time()
print(f"Kinda iterations: {iterations}, Time: {end - start:.4f}s")
"""

    # Equivalent Python code
    python_code = """
import time
count = 0
iterations = 0
start = time.time()
while count < 1000:
    count += 1
    iterations += 1
    if iterations > 2000:  # Safety break
        break
end = time.time()
print(f"Python iterations: {iterations}, Time: {end - start:.4f}s")
"""

    kinda_times = []
    python_times = []

    # Run multiple trials
    trials = 5
    print(f"Running {trials} trials...")

    for i in range(trials):
        print(f"  Trial {i+1}/{trials}")

        # Benchmark kinda
        kinda_time = run_kinda_code(kinda_code)
        if kinda_time is not None:
            kinda_times.append(kinda_time)

        # Benchmark Python
        python_time = run_python_code(python_code)
        if python_time is not None:
            python_times.append(python_time)

    if not kinda_times or not python_times:
        print("❌ Benchmark failed - could not collect timing data")
        return False

    # Calculate averages
    avg_kinda = statistics.mean(kinda_times)
    avg_python = statistics.mean(python_times)
    overhead = ((avg_kinda - avg_python) / avg_python) * 100 if avg_python > 0 else 0

    print(f"\nResults:")
    print(f"  Average Kinda time: {avg_kinda:.4f}s")
    print(f"  Average Python time: {avg_python:.4f}s")
    print(f"  Overhead: {overhead:.1f}%")

    if overhead <= 15:
        print(f"✓ Performance target met: {overhead:.1f}% <= 15%")
        return True
    else:
        print(f"❌ Performance target missed: {overhead:.1f}% > 15%")
        return False


def benchmark_maybe_for():
    """Benchmark ~maybe_for vs standard for loop."""
    print("\n=== Benchmarking ~maybe_for ===")

    # Set up reliable personality for consistent performance
    setup_personality("reliable", chaos_level=1, seed=42)

    # Kinda code with ~maybe_for
    kinda_code = """
import time
processed = 0
items = list(range(1000))
start = time.time()
~maybe_for item in items:
    processed += 1
end = time.time()
print(f"Kinda processed: {processed}, Time: {end - start:.4f}s")
"""

    # Equivalent Python code
    python_code = """
import time
processed = 0
items = list(range(1000))
start = time.time()
for item in items:
    processed += 1
end = time.time()
print(f"Python processed: {processed}, Time: {end - start:.4f}s")
"""

    kinda_times = []
    python_times = []

    # Run multiple trials
    trials = 5
    print(f"Running {trials} trials...")

    for i in range(trials):
        print(f"  Trial {i+1}/{trials}")

        # Benchmark kinda
        kinda_time = run_kinda_code(kinda_code)
        if kinda_time is not None:
            kinda_times.append(kinda_time)

        # Benchmark Python
        python_time = run_python_code(python_code)
        if python_time is not None:
            python_times.append(python_time)

    if not kinda_times or not python_times:
        print("❌ Benchmark failed - could not collect timing data")
        return False

    # Calculate averages
    avg_kinda = statistics.mean(kinda_times)
    avg_python = statistics.mean(python_times)
    overhead = ((avg_kinda - avg_python) / avg_python) * 100 if avg_python > 0 else 0

    print(f"\nResults:")
    print(f"  Average Kinda time: {avg_kinda:.4f}s")
    print(f"  Average Python time: {avg_python:.4f}s")
    print(f"  Overhead: {overhead:.1f}%")

    if overhead <= 15:
        print(f"✓ Performance target met: {overhead:.1f}% <= 15%")
        return True
    else:
        print(f"❌ Performance target missed: {overhead:.1f}% > 15%")
        return False


def benchmark_nested_constructs():
    """Benchmark nested loop constructs for worst-case performance."""
    print("\n=== Benchmarking Nested Constructs ===")

    # Set up playful personality for moderate performance
    setup_personality("playful", chaos_level=5, seed=42)

    # Kinda code with nested constructs
    kinda_code = """
import time
total = 0
outer = 0
start = time.time()
~sometimes_while outer < 50:
    outer += 1
    items = [1, 2, 3, 4, 5]
    ~maybe_for item in items:
        total += item
    if outer > 100:  # Safety break
        break
end = time.time()
print(f"Kinda total: {total}, outer: {outer}, Time: {end - start:.4f}s")
"""

    # Equivalent Python code
    python_code = """
import time
total = 0
outer = 0
start = time.time()
while outer < 50:
    outer += 1
    items = [1, 2, 3, 4, 5]
    for item in items:
        total += item
    if outer > 100:  # Safety break
        break
end = time.time()
print(f"Python total: {total}, outer: {outer}, Time: {end - start:.4f}s")
"""

    kinda_times = []
    python_times = []

    # Run multiple trials
    trials = 3  # Fewer trials for nested case
    print(f"Running {trials} trials...")

    for i in range(trials):
        print(f"  Trial {i+1}/{trials}")

        # Benchmark kinda
        kinda_time = run_kinda_code(kinda_code)
        if kinda_time is not None:
            kinda_times.append(kinda_time)

        # Benchmark Python
        python_time = run_python_code(python_code)
        if python_time is not None:
            python_times.append(python_time)

    if not kinda_times or not python_times:
        print("❌ Benchmark failed - could not collect timing data")
        return False

    # Calculate averages
    avg_kinda = statistics.mean(kinda_times)
    avg_python = statistics.mean(python_times)
    overhead = ((avg_kinda - avg_python) / avg_python) * 100 if avg_python > 0 else 0

    print(f"\nResults:")
    print(f"  Average Kinda time: {avg_kinda:.4f}s")
    print(f"  Average Python time: {avg_python:.4f}s")
    print(f"  Overhead: {overhead:.1f}%")

    if overhead <= 15:
        print(f"✓ Performance target met: {overhead:.1f}% <= 15%")
        return True
    else:
        print(f"❌ Performance target missed: {overhead:.1f}% > 15%")
        return False


def main():
    """Run performance benchmarks for loop constructs."""
    print("=== Epic #125 Task 1 Performance Testing ===")
    print("Target: <15% overhead compared to standard Python loops")
    print()

    results = []

    # Run all benchmarks
    results.append(benchmark_sometimes_while())
    results.append(benchmark_maybe_for())
    results.append(benchmark_nested_constructs())

    # Summary
    passed = sum(results)
    total = len(results)

    print(f"\n=== Performance Test Summary ===")
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 ALL PERFORMANCE TARGETS MET!")
        print("✓ Loop constructs meet <15% overhead requirement")
        return True
    else:
        print("❌ Some performance targets missed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
