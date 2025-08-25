#!/usr/bin/env python3
"""
Ensure the fuzzy runtime is properly generated with all required functions.
This script can be called during CI to fix import issues.
"""

from pathlib import Path
from kinda.langs.python.runtime_gen import generate_runtime

def main():
    """Regenerate the fuzzy runtime to ensure all functions are available."""
    output_dir = Path('kinda/langs/python/runtime')
    print(f"Regenerating runtime in {output_dir}")
    generate_runtime(output_dir)
    
    # Verify the regenerated runtime has required functions
    try:
        from kinda.langs.python.runtime.fuzzy import ish_comparison, ish_value, welp_fallback, env
        print("✓ All required functions available after regeneration")
        print(f"✓ Environment contains {len(env)} functions")
    except ImportError as e:
        print(f"✗ Import error after regeneration: {e}")
        return 1
    
    print("✓ Runtime generation successful")
    return 0

if __name__ == "__main__":
    exit(main())