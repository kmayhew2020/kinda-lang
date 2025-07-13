# tests/test_transformer.py
from pathlib import Path

def test_transformer_generates_output():
    build_file = Path("build/simple_example.py")
    assert build_file.exists(), "Expected build/simple_example.py to be created"

    contents = build_file.read_text()

    # Check that it was transformed correctly (not raw Kinda anymore)
    assert "kinda_int(" in contents, "Expected kinda_int in transformed output"
    assert "sorta_print(" in contents, "Expected sorta_print in transformed output"
