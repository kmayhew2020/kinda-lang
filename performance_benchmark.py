#!/usr/bin/env python3
"""
Performance benchmarking script for kinda-lang transformations.
Run this to measure baseline performance metrics.
"""

import time
import sys
import subprocess
from pathlib import Path
import tempfile
import statistics

def time_command(command, iterations=5):
    """Time a command multiple times and return statistics."""
    times = []
    for i in range(iterations):
        start = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        end = time.time()
        if result.returncode != 0:
            print(f"Command failed: {command}")
            print(result.stderr)
            return None
        times.append((end - start) * 1000)  # Convert to milliseconds
    
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'min': min(times),
        'max': max(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0
    }

def benchmark_transformation_speed():
    """Benchmark various kinda-lang operations."""
    print("🚀 Kinda-Lang Performance Benchmark")
    print("=" * 50)
    
    test_cases = [
        ("CLI startup (help)", "kinda --help"),
        ("Simple transformation", "kinda transform examples/python/individual/welp_example.py.knda"),
        ("Complex transformation", "kinda transform examples/python/comprehensive/chaos_arena_complete.py.knda"), 
        ("Full run (simple)", "kinda run examples/python/individual/welp_example.py.knda"),
        ("Full run (complex)", "kinda run examples/python/comprehensive/chaos_arena_complete.py.knda"),
    ]
    
    results = {}
    for name, command in test_cases:
        print(f"\n📊 Benchmarking: {name}")
        result = time_command(command, iterations=10)
        if result:
            results[name] = result
            print(f"   Mean: {result['mean']:.1f}ms ± {result['stdev']:.1f}ms")
            print(f"   Range: {result['min']:.1f}ms - {result['max']:.1f}ms")
        else:
            print("   ❌ Failed")
    
    # Test transformation speed on various input sizes
    print(f"\n📈 Input Size Performance Analysis")
    
    # Create test files of different sizes
    test_code_small = """
# Simple test
result = api_call() ~welp 'default'
score ~ish 100
~sorta print("Done")
"""
    
    test_code_large = test_code_small * 20  # 20x larger
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
        f.write(test_code_small)
        small_file = f.name
        
    with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
        f.write(test_code_large)
        large_file = f.name
        
    try:
        small_result = time_command(f"kinda transform {small_file}", iterations=20)
        large_result = time_command(f"kinda transform {large_file}", iterations=20)
        
        if small_result and large_result:
            print(f"   Small file (~4 lines): {small_result['mean']:.1f}ms")
            print(f"   Large file (~80 lines): {large_result['mean']:.1f}ms") 
            print(f"   Scaling factor: {large_result['mean'] / small_result['mean']:.2f}x")
            print(f"   Lines per millisecond: {80 / large_result['mean']:.1f}")
            
    finally:
        Path(small_file).unlink()
        Path(large_file).unlink()
    
    print(f"\n✅ Benchmark Complete")
    return results

if __name__ == "__main__":
    benchmark_transformation_speed()