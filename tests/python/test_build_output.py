from pathlib import Path
from tests.python.utils import run_python_file


def test_simple_example_output():
    source_file = Path("build/python/chaotic_greeter.knda.py")
    runtime_file = Path("kinda/langs/python/runtime/fuzzy.py")

    # Sanity checks
    assert source_file.exists(), "Transformed file does not exist."
    assert runtime_file.exists(), "fuzzy.py runtime was not generated."

    # Run multiple times to account for ~sorta print's ~20% silence
    found_output = False
    for _ in range(10):
        output = run_python_file(str(source_file))

        # ~sorta print may be silent ~20% of the time (correct behavior)
        if "[print]" in output or "This is greet" in output:
            found_output = True
            assert "kinda_int" not in output  # implementation detail shouldn't leak
            break

    # With 10 runs at 80% success rate, probability of all failing is 0.2^10 ≈ 0.0000001%
    assert found_output, "~sorta print should execute at least once in 10 runs"

    # Check that fuzzy.py includes expected helper functions
    fuzzy_code = runtime_file.read_text()

    assert "def kinda_int" in fuzzy_code, "Missing 'kinda_int' in fuzzy.py"
    assert "def sorta_print" in fuzzy_code, "Missing 'sorta_print' in fuzzy.py"
    assert "def sometimes" in fuzzy_code, "Missing 'sometimes' in fuzzy.py"
