# tests/conftest.py
import subprocess
import shutil
from pathlib import Path
import pytest

SRC_DIRS = ["tests/python/input", "tests"]
BUILD_DIR = Path("build/python")
RUNTIME_OUT = Path("kinda/runtime/python")


def generate_runtime():
    # Clean old runtime
    if RUNTIME_OUT.exists():
        shutil.rmtree(RUNTIME_OUT)
    RUNTIME_OUT.mkdir(parents=True, exist_ok=True)

    # Run Python codegen
    result = subprocess.run(
        ["python", "-m", "kinda.codegen.python", "--out", str(RUNTIME_OUT)],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("Runtime generation failed:")
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)
        raise RuntimeError("Runtime codegen failed")


@pytest.fixture(scope="session", autouse=True)
def regenerate_build():
    # Step 1: Regenerate runtime
    generate_runtime()

    # Step 2: Clean and recreate build/ folder
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir()

    # Step 3: Run transformer on all .knda files in each src dir
    for src_dir in SRC_DIRS:
        lang = "python" if "python" in src_dir else "c"  # crude but effective
        result = subprocess.run(
            ["python", "-m", "kinda", "transform", src_dir, "--out", str(BUILD_DIR), "--lang", lang],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("Transformer failed:")
            print("STDOUT:\n", result.stdout)
            print("STDERR:\n", result.stderr)
            raise RuntimeError("Transformer failed during test setup")