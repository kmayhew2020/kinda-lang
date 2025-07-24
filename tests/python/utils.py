import os
import subprocess
from pathlib import Path

def run_python_file(filepath):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())  # Ensure project root is on PYTHONPATH
    result = subprocess.run(
        ["python", filepath],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    return result.stdout.strip()
