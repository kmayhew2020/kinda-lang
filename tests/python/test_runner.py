import subprocess

def run_kinda_test(path):
    result = subprocess.run(
        ["python", "-m", "kinda", "interpret", path],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().splitlines()

def test_fuzzy_declaration():
    output = run_kinda_test("tests/python/input/test_fuzzy_declaration.py.knda")
    assert any("[print]" in line or "[shrug]" in line for line in output)

def test_fuzzy_reassignment():
    output = run_kinda_test("tests/python/input/test_fuzzy_reassignment.py.knda")
    # We can’t predict exact count due to chaos, so check that at least one line printed something
    assert any("[print]" in line or "[shrug]" in line for line in output)

def test_sorta_print():
    output = run_kinda_test("tests/python/input/test_sorta_print.py.knda")
    assert any("[print]" in line or "[shrug]" in line for line in output)

def test_sometimes_block():
    output = run_kinda_test("tests/python/input/test_sometimes_block.py.knda")
    assert any("[print]" in line or "[shrug]" in line for line in output)