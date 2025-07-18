# tests/test_build_output.py

import os
import subprocess
from pathlib import Path

def run_python_file(filepath):
    env = os.environ.copy()
    repo_root = str(Path.cwd())
    existing_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = repo_root + os.pathsep + existing_path if existing_path else repo_root

    result = subprocess.run(
        ["python", filepath],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    return result.stdout.strip()


def test_simple_example_output():
    source_file = Path("build/simple_example.py")
    assert source_file.exists(), "Transformed file does not exist."

    output = run_python_file(str(source_file))

    # Expect some fuzzy behaviors like `[print]`, etc.
    assert "[print]" in output
    assert "kinda_int" not in output  # should not be printed as text