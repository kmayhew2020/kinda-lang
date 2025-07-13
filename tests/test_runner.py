import subprocess
import os

def run_kinda_test(script_path):
    full_path = os.path.abspath(script_path)
    result = subprocess.run(
        ['python3', 'interpreter.py', full_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.dirname(__file__) + "/.."
    )
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    return result.stdout + result.stderr

def test_fuzzy_assignments():
    output = run_kinda_test('tests/test_fuzzy_assignments.knda')
    print("---- DEBUG OUTPUT ----")
    print(output)
    print("----------------------")
    assert "x ~=" in output
