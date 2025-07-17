from pathlib import Path
from tests.utils import run_python_file


def test_simple_example_output():
    source_file = Path("build/chaotic_greeter.py.py")
    runtime_file = Path("kinda/runtime/python/fuzzy.py")

    # Sanity checks
    assert source_file.exists(), "Transformed file does not exist."
    assert runtime_file.exists(), "fuzzy.py runtime was not generated."

    # Run the transformed Python file
    output = run_python_file(str(source_file))

    # Output checks (fuzzy output, but we expect something printed)
    assert "[print]" in output or "This is greet" in output
    assert "kinda_int" not in output  # implementation detail shouldn't leak

    # Check that fuzzy.py includes expected helper functions
    fuzzy_code = runtime_file.read_text()

    assert "def kinda_int" in fuzzy_code, "Missing 'kinda_int' in fuzzy.py"
    assert "def sorta_print" in fuzzy_code, "Missing 'sorta_print' in fuzzy.py"
    assert "def sometimes" in fuzzy_code, "Missing 'sometimes' in fuzzy.py"
