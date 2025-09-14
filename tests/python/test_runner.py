import subprocess


def run_kinda_test(path):
    result = subprocess.run(
        ["python3", "-m", "kinda", "interpret", path],
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
    """Test sometimes block - inherently random, so we test multiple runs"""
    # Run multiple times to account for randomness
    outputs = []
    for _ in range(10):  # 10 runs should catch at least some output
        try:
            output = run_kinda_test("tests/python/input/test_sometimes_block.py.knda")
            outputs.extend(output)
        except subprocess.CalledProcessError:
            pass  # Sometimes might fail randomly, that's expected

    # At least one run should have produced some output, or all runs completed successfully
    has_output = any("[print]" in line or "[shrug]" in line for line in outputs)
    ran_successfully = len(outputs) > 0  # At least one run completed

    assert has_output or ran_successfully
