# Root conftest.py - Ensures runtime generation happens before any test collection
# This is critical because many test files import from kinda.langs.python.runtime.fuzzy

import shutil
from pathlib import Path

# Import and run runtime generation IMMEDIATELY when pytest loads this conftest
from kinda.langs.python.runtime_gen import generate_runtime as generate_runtime_code

# Runtime path
RUNTIME_OUT = Path("kinda/langs/python/runtime")


def ensure_runtime_exists():
    """Ensure runtime is generated before any test collection happens."""
    # Clean old runtime
    if RUNTIME_OUT.exists():
        shutil.rmtree(RUNTIME_OUT)
    RUNTIME_OUT.mkdir(parents=True, exist_ok=True)

    # Generate runtime immediately
    generate_runtime_code(RUNTIME_OUT)
    print(f"[conftest] Generated runtime at {RUNTIME_OUT}")


# Generate runtime IMMEDIATELY when this module is imported
ensure_runtime_exists()
