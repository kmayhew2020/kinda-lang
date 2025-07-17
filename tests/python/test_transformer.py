# tests/test_transformer.py
from pathlib import Path

def test_transformer_generates_output():
    runtime_file = Path("kinda/runtime/python/fuzzy.py")
    assert runtime_file.exists(), "Expected kinda/runtime/python/fuzzy.py to be created"

    contents = runtime_file.read_text()

    # Check that it was transformed correctly (not raw Kinda anymore)
    assert "kinda_int(" in contents, "Expected kinda_int in transformed output"
    assert "sorta_print(" in contents, "Expected sorta_print in transformed output"
