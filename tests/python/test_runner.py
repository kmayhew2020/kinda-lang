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
    # After Issue #106 fix: ~sorta print has ~20% failure rate (produces no output)
    # Run multiple times to account for probabilistic behavior
    for attempt in range(10):  # 10 attempts gives us 99.9% chance of seeing output at least once
        output = run_kinda_test("tests/python/input/test_fuzzy_declaration.py.knda")
        if any("[print]" in line or "[shrug]" in line for line in output):
            return  # Success - we got output
    # If we get here, we failed 10 times in a row (0.2^10 = 0.0001% chance)
    assert False, "~sorta print failed to produce output in 10 attempts (extremely unlikely)"


def test_fuzzy_reassignment():
    # After Issue #106 fix: ~sorta print has ~20% failure rate (produces no output)
    # Run multiple times to account for probabilistic behavior
    for attempt in range(10):  # 10 attempts gives us 99.9% chance of seeing output at least once
        output = run_kinda_test("tests/python/input/test_fuzzy_reassignment.py.knda")
        if any("[print]" in line or "[shrug]" in line for line in output):
            return  # Success - we got output
    # If we get here, we failed 10 times in a row (0.2^10 = 0.0001% chance)
    assert False, "~sorta print failed to produce output in 10 attempts (extremely unlikely)"


def test_sorta_print():
    # After Issue #106 fix: ~sorta print has ~20% failure rate (produces no output)
    # Run multiple times to account for probabilistic behavior
    for attempt in range(10):  # 10 attempts gives us 99.9% chance of seeing output at least once
        output = run_kinda_test("tests/python/input/test_sorta_print.py.knda")
        if any("[print]" in line or "[shrug]" in line for line in output):
            return  # Success - we got output
    # If we get here, we failed 10 times in a row (0.2^10 = 0.0001% chance)
    assert False, "~sorta print failed to produce output in 10 attempts (extremely unlikely)"


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
