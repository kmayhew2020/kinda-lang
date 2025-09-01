#!/usr/bin/env python3
"""
Debug script to test seed reproducibility issues seen in CI
"""
import sys
from pathlib import Path

# Add the kinda package to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from kinda.personality import PersonalityContext
from kinda.langs.python.runtime.fuzzy import kinda_binary, maybe, sometimes

def test_kinda_binary_reproducibility():
    """Test the specific failure seen in CI"""
    print("=== Testing kinda_binary reproducibility ===")
    
    # First run with seed 77777
    print("Creating first PersonalityContext...")
    PersonalityContext._instance = PersonalityContext("playful", 5, seed=77777)
    ctx1 = PersonalityContext._instance
    print(f"First context seed: {ctx1.seed}, RNG state: {ctx1.rng.getstate()[1][0]}")
    
    result1 = kinda_binary()
    print(f"First result: {result1}")
    print(f"First context RNG state after call: {ctx1.rng.getstate()[1][0]}")
    
    # Second run with same seed
    print("Creating second PersonalityContext...")
    PersonalityContext._instance = PersonalityContext("playful", 5, seed=77777)
    ctx2 = PersonalityContext._instance
    print(f"Second context seed: {ctx2.seed}, RNG state: {ctx2.rng.getstate()[1][0]}")
    
    result2 = kinda_binary()
    print(f"Second result: {result2}")
    print(f"Second context RNG state after call: {ctx2.rng.getstate()[1][0]}")
    
    print(f"Results equal: {result1 == result2}")
    return result1 == result2

def test_maybe_reproducibility():
    """Test maybe reproducibility"""
    print("=== Testing maybe reproducibility ===")
    
    # First run with seed 12121
    PersonalityContext._instance = PersonalityContext("playful", 5, seed=12121)
    result1 = maybe(True)
    print(f"First result: {result1}")
    
    # Second run with same seed
    PersonalityContext._instance = PersonalityContext("playful", 5, seed=12121)
    result2 = maybe(True)
    print(f"Second result: {result2}")
    
    print(f"Results equal: {result1 == result2}")
    return result1 == result2

def test_sometimes_reproducibility():
    """Test sometimes reproducibility"""
    print("=== Testing sometimes reproducibility ===")
    
    # First run with seed 15151
    PersonalityContext._instance = PersonalityContext("playful", 5, seed=15151)
    result1 = sometimes(True)
    print(f"First result: {result1}")
    
    # Second run with same seed
    PersonalityContext._instance = PersonalityContext("playful", 5, seed=15151)
    result2 = sometimes(True)
    print(f"Second result: {result2}")
    
    print(f"Results equal: {result1 == result2}")
    return result1 == result2

def main():
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    results = [
        test_kinda_binary_reproducibility(),
        test_maybe_reproducibility(), 
        test_sometimes_reproducibility()
    ]
    
    if all(results):
        print("\n✅ All tests passed - seed reproducibility working!")
    else:
        print("\n❌ Some tests failed - seed reproducibility broken!")
        sys.exit(1)

if __name__ == "__main__":
    main()