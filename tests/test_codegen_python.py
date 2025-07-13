# tests/test_codegen_python.py
import shutil
from pathlib import Path
from kinda.codegen.python import generate_runtime

def test_generate_python_runtime(tmp_path):
    output_dir = tmp_path / "runtime"
    generate_runtime(output_dir)

    runtime_file = output_dir / "fuzzy.py"
    assert runtime_file.exists(), "fuzzy.py was not generated"

    contents = runtime_file.read_text()
    assert "def sorta_print" in contents, "sorta_print missing from runtime"
    assert "def sometimes" in contents, "sometimes missing from runtime"