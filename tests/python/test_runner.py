# tests/test_runner.py

import subprocess

def run_kinda_test(path):
    result = subprocess.run(
        ["python", "-m", "kinda", "interpret", path],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()

def test_fuzzy_declaration():
    output = run_kinda_test("tests/python/input/test_fuzzy_declaration.py.knda")
    assert "x ~=" in output
    assert "[print]" in output

def test_fuzzy_reassignment():
    output = run_kinda_test("tests/python/input/test_fuzzy_reassignment.py.knda")
    assert output.count("x ~=") == 2
    assert "[print]" in output

def test_sorta_print():
    output = run_kinda_test("tests/python/input/test_sorta_print.py.knda")
    assert "[print]" in output

def test_sometimes_block():
    output = run_kinda_test("tests/python/input/test_sometimes_block.py.knda")
    assert "[sometimes]" in output or "[assign]" in output or "[print]" in output
