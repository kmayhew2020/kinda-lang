# tests/test_runner.py

import subprocess

def run_kinda_test(filepath):
    result = subprocess.run(
        ["python", "-m", "kinda.interpreter", "--test", filepath],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout + result.stderr

def test_fuzzy_declaration():
    output = run_kinda_test("tests/test_fuzzy_declaration.knda")
    assert "x ~=" in output
    assert "[print]" in output

def test_fuzzy_reassignment():
    output = run_kinda_test("tests/test_fuzzy_reassignment.knda")
    assert output.count("x ~=") == 2
    assert "[print]" in output

def test_sorta_print():
    output = run_kinda_test("tests/test_sorta_print.knda")
    assert "[print]" in output

def test_sometimes_block():
    output = run_kinda_test("tests/test_sometimes_block.knda")
    assert "[sometimes]" in output or "[assign]" in output or "[print]" in output
