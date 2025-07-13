import subprocess
import os

def run_kinda_test(filename):
    result = subprocess.run(
        ['python', 'interpreter.py', filename],
        capture_output=True,
        text=True
    )
    return result.stdout

def test_fuzzy_assignment():
    output = run_kinda_test('tests/test_fuzzy_assignment.knda')
    assert "x ~=" in output  # crude check that assignment ran
    assert "[print]" in output
