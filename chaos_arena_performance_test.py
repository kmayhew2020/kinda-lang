#!/usr/bin/env python3
"""
Chaos Arena Performance Testing - Stress test with most complex examples
"""

import time
import subprocess
import statistics
from pathlib import Path

def time_transformation(file_path, iterations=10):
    """Time transformation of a specific file multiple times."""
    times = []
    
    for i in range(iterations):
        start = time.perf_counter()
        result = subprocess.run(
            ["python", "-m", "kinda.cli", "transform", str(file_path)],
            capture_output=True,
            text=True
        )
        end = time.perf_counter()
        
        if result.returncode != 0:
            print(f"❌ Transformation failed: {result.stderr}")
            return None
        
        times.append((end - start) * 1000)  # Convert to milliseconds
    
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'min': min(times),
        'max': max(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'times': times
    }

def analyze_file_complexity(file_path):
    """Analyze complexity metrics of a .knda file."""
    if not file_path.exists():
        return None
    
    content = file_path.read_text()
    lines = content.split('\n')
    
    metrics = {
        'total_lines': len(lines),
        'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
        'kinda_constructs': content.count('~kinda'),
        'sorta_constructs': content.count('~sorta'),
        'maybe_constructs': content.count('~maybe'),
        'sometimes_constructs': content.count('~sometimes'),
        'ish_constructs': content.count('~ish'),
        'welp_constructs': content.count('~welp'),
        'binary_constructs': content.count('kinda_binary'),
        'fuzzy_assigns': content.count('~='),
        'total_constructs': (
            content.count('~kinda') + content.count('~sorta') + 
            content.count('~maybe') + content.count('~sometimes') +
            content.count('~ish') + content.count('~welp') +
            content.count('kinda_binary') + content.count('~=')
        ),
        'complexity_score': None
    }
    
    # Calculate complexity score (constructs per line of code)
    if metrics['code_lines'] > 0:
        metrics['complexity_score'] = metrics['total_constructs'] / metrics['code_lines']
    
    return metrics

def run_chaos_arena_performance_test():
    """Run comprehensive performance test on chaos arena examples."""
    
    print("🎪 CHAOS ARENA PERFORMANCE STRESS TEST")
    print("=" * 60)
    
    chaos_files = [
        Path("examples/python/chaos_arena.py.knda"),
        Path("examples/python/chaos_arena2.py.knda"),
        Path("examples/python/comprehensive/chaos_arena_complete.py.knda"),
        Path("examples/python/comprehensive/chaos_arena2_complete.py.knda"),
        Path("examples/python/comprehensive/fuzzy_game_logic.py.knda"),
        Path("examples/python/comprehensive/simple_chaos_battle.py.knda"),
    ]
    
    # Filter to existing files
    existing_files = [f for f in chaos_files if f.exists()]
    
    print(f"Found {len(existing_files)} chaos arena files:")
    for f in existing_files:
        print(f"  📁 {f}")
    
    results = {}
    
    for file_path in existing_files:
        print(f"\n🔬 Testing: {file_path.name}")
        print("-" * 40)
        
        # Analyze file complexity
        complexity = analyze_file_complexity(file_path)
        if complexity:
            print(f"📊 Complexity Analysis:")
            print(f"   Total lines: {complexity['total_lines']}")
            print(f"   Code lines: {complexity['code_lines']}")
            print(f"   Total constructs: {complexity['total_constructs']}")
            print(f"   Complexity score: {complexity['complexity_score']:.3f}")
            
            # Breakdown by construct type
            constructs = []
            if complexity['kinda_constructs']: constructs.append(f"~kinda({complexity['kinda_constructs']})")
            if complexity['sorta_constructs']: constructs.append(f"~sorta({complexity['sorta_constructs']})")
            if complexity['maybe_constructs']: constructs.append(f"~maybe({complexity['maybe_constructs']})")
            if complexity['sometimes_constructs']: constructs.append(f"~sometimes({complexity['sometimes_constructs']})")
            if complexity['ish_constructs']: constructs.append(f"~ish({complexity['ish_constructs']})")
            if complexity['welp_constructs']: constructs.append(f"~welp({complexity['welp_constructs']})")
            if complexity['binary_constructs']: constructs.append(f"binary({complexity['binary_constructs']})")
            if complexity['fuzzy_assigns']: constructs.append(f"~=({complexity['fuzzy_assigns']})")
            
            print(f"   Construct breakdown: {', '.join(constructs)}")
        
        # Performance test
        print(f"\n⚡ Performance Test (10 iterations):")
        perf_result = time_transformation(file_path, iterations=10)
        
        if perf_result:
            print(f"   Mean: {perf_result['mean']:.1f}ms ± {perf_result['stdev']:.1f}ms")
            print(f"   Median: {perf_result['median']:.1f}ms")
            print(f"   Range: {perf_result['min']:.1f}ms - {perf_result['max']:.1f}ms")
            
            if complexity and complexity['code_lines'] > 0:
                lines_per_ms = complexity['code_lines'] / perf_result['mean']
                constructs_per_ms = complexity['total_constructs'] / perf_result['mean']
                print(f"   Processing speed: {lines_per_ms:.2f} lines/ms")
                print(f"   Construct processing: {constructs_per_ms:.2f} constructs/ms")
            
            results[file_path.name] = {
                'complexity': complexity,
                'performance': perf_result
            }
        else:
            print("   ❌ Failed to measure performance")
    
    # Summary analysis
    print(f"\n🏆 CHAOS ARENA PERFORMANCE SUMMARY")
    print("=" * 60)
    
    if results:
        # Sort by complexity score
        sorted_results = sorted(results.items(), 
                               key=lambda x: x[1]['complexity']['complexity_score'] if x[1]['complexity'] else 0,
                               reverse=True)
        
        print("📈 Performance vs Complexity Ranking:")
        for i, (name, data) in enumerate(sorted_results, 1):
            complexity = data['complexity']
            perf = data['performance']
            
            efficiency = complexity['total_constructs'] / perf['mean'] if complexity else 0
            
            print(f"  {i}. {name}")
            print(f"     Complexity: {complexity['complexity_score']:.3f} | "
                  f"Time: {perf['mean']:.1f}ms | "
                  f"Efficiency: {efficiency:.2f} constructs/ms")
        
        # Overall stats
        all_times = [r['performance']['mean'] for r in results.values()]
        all_complexities = [r['complexity']['complexity_score'] for r in results.values() if r['complexity']]
        
        print(f"\n📊 Overall Chaos Arena Statistics:")
        print(f"   Average transformation time: {statistics.mean(all_times):.1f}ms")
        print(f"   Average complexity score: {statistics.mean(all_complexities):.3f}")
        print(f"   Performance consistency: ±{statistics.stdev(all_times):.1f}ms")
        
        # Find the most demanding file
        max_time_file = max(results.items(), key=lambda x: x[1]['performance']['mean'])
        max_complexity_file = max(results.items(), key=lambda x: x[1]['complexity']['complexity_score'] if x[1]['complexity'] else 0)
        
        print(f"\n🎯 Stress Test Champions:")
        print(f"   Most time-consuming: {max_time_file[0]} ({max_time_file[1]['performance']['mean']:.1f}ms)")
        print(f"   Most complex: {max_complexity_file[0]} (score: {max_complexity_file[1]['complexity']['complexity_score']:.3f})")
    
    print(f"\n✅ Chaos Arena Performance Test Complete!")
    return results

if __name__ == "__main__":
    run_chaos_arena_performance_test()