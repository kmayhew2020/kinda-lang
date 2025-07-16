# kinda/run.py

import subprocess
import os
from pathlib import Path

def execute(input_path, out_dir="build", transformer=None):
    """
    Transforms a .knda file and runs the resulting .py file.
    """
    input_path = Path(input_path)
    out_dir = Path(out_dir)

    if transformer is None:
        raise ValueError("No transformer provided to execute(). CLI should supply one.")

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

    # Force the repo root (where kinda/ lives) into the path
    project_root = Path(__file__).resolve().parent.parent
    pythonpath = os.pathsep.join([
        str(project_root),
        env.get("PYTHONPATH", "")
    ]).strip(os.pathsep)

    env["PYTHONPATH"] = pythonpath

    print(f"[debug] PYTHONPATH for subprocess: {env['PYTHONPATH']}")



    subprocess.run(["python", str(output_path)], env=env)
