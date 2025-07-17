from pathlib import Path

def test_runtime_python_exists():
    runtime_dir = Path("kinda/runtime/python")
    assert runtime_dir.exists(), "Expected runtime directory was not generated."
    assert any(runtime_dir.glob("*.py")), "No Python files found in runtime output."