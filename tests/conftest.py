# tests/conftest.py
import subprocess
import shutil
from pathlib import Path
import pytest

SRC_DIRS = ["examples", "tests"]
BUILD_DIR = Path("build")

@pytest.fixture(scope="session", autouse=True)
def regenerate_build():
    # Clean build/ folder first
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir()

    # Regenerate from all .knda files
    for src_dir in SRC_DIRS:
        result = subprocess.run(
            ["python", "-m", "kinda.transformer", src_dir, "--out", str(BUILD_DIR)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("STDOUT:\n", result.stdout)
            print("STDERR:\n", result.stderr)
            raise RuntimeError("Transformer failed during test setup")