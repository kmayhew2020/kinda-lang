# tests/test_transformer.py
from pathlib import Path
import pytest
from kinda.langs.python.transformer_py import transform_line

def test_transformer_generates_output():
    runtime_file = Path("kinda/runtime/python/fuzzy.py")
    assert runtime_file.exists(), "Expected kinda/runtime/python/fuzzy.py to be created"

    contents = runtime_file.read_text()

    # Check that it was transformed correctly (not raw Kinda anymore)
    assert "kinda_int(" in contents, "Expected kinda_int in transformed output"
    assert "sorta_print(" in contents, "Expected sorta_print in transformed output"

def test_blank_line_passthrough():
    from kinda.langs.python.transformer_py import transform_line
    line = "\n"
    result = transform_line(line)
    assert result == "", "Blank lines should return empty string"

def test_comment_line_passthrough():
        from kinda.langs.python.transformer_py import transform_line
        line = "  # this is a comment\n"
        result = transform_line(line)
        assert result == line, "Comment lines should be returned unchanged"

@pytest.mark.parametrize("line", [
    "x = 42\n",
    "    if x > 0:\n",
    "def my_func():\n",
    "import math\n",
    "\"\"\"This is a docstring\"\"\"\n"
])

def test_normal_python_lines_passthrough(line):
    result = transform_line(line)
    assert result == line, f"Line should be unchanged: {line.strip()}"
