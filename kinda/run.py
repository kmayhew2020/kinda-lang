# kinda/run.py

import subprocess
import os
from pathlib import Path
from kinda import transformer

def execute(input_path: str, out_dir: str = "build"):
    """
    Transforms a .knda file and runs the resulting .py file.
    """
    input_path = Path(input_path)
    out_dir = Path(out_dir)

    output_paths = transformer.transform(input_path, out_dir=out_dir)

    if isinstance(output_paths, list):
        if len(output_paths) != 1:
            raise ValueError("Expected one transformed file, got multiple.")
        output_path = output_paths[0]
    else:
        output_path = output_paths

    print(f"[kinda] Running transformed file: {output_path}")

    # Ensure Python can find the kinda runtime
    env = os.environ.copy()
    project_root = Path(__file__).parent.parent.resolve()
    env["PYTHONPATH"] = str(project_root)

    subprocess.run(["python", str(output_path)], env=env)