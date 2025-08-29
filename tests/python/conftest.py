import subprocess
import shutil
from pathlib import Path
import pytest

# ✅ Rename imported function to avoid name conflict
from kinda.langs.python.runtime_gen import generate_runtime as generate_runtime_code

SRC_DIRS = ["tests/python/input", "tests"]
BUILD_DIR = Path("build/python")
RUNTIME_OUT = Path("kinda/langs/python/runtime")


def generate_runtime():
    # Clean old runtime
    if RUNTIME_OUT.exists():
        shutil.rmtree(RUNTIME_OUT)
    RUNTIME_OUT.mkdir(parents=True, exist_ok=True)

    # Run Python runtime generation directly
    generate_runtime_code(RUNTIME_OUT)


@pytest.fixture(scope="session", autouse=True)
def regenerate_build():
    # Step 1: Regenerate runtime
    generate_runtime()

    # Step 2: Clean and recreate build/ folder
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # Step 3: Run transformer on all .knda files in each src dir
    for src_dir in SRC_DIRS:
        # Only use Python language since C support is disabled in v0.3.0
        lang = "python"
        result1 = subprocess.run(
            [
                "python",
                "-m",
                "kinda",
                "transform",
                src_dir,
                "--out",
                str(BUILD_DIR),
                "--lang",
                lang,
            ],
            capture_output=True,
            text=True,
        )
        result2 = subprocess.run(
            ["kinda", "transform", src_dir, "--out", str(BUILD_DIR), "--lang", lang],
            capture_output=True,
            text=True,
        )
        if result1.returncode != 0:
            print("Transformer failed:")
            print("STDOUT:\n", result1.stdout)
            print("STDERR:\n", result1.stderr)
            raise RuntimeError("Transformer failed during test setup")
        if result2.returncode != 0:
            print("Transformer failed:")
            print("STDOUT:\n", result2.stdout)
            print("STDERR:\n", result2.stderr)
            raise RuntimeError("Transformer failed during test setup")
