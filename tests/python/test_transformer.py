# tests/test_transformer.py
from pathlib import Path
import pytest
from kinda.langs.python.transformer import transform_line


def test_transformer_generates_output():
    runtime_file = Path("kinda/langs/python/runtime/fuzzy.py")
    assert runtime_file.exists(), "Expected kinda/langs/python/runtime/fuzzy.py to be created"

    contents = runtime_file.read_text()
    assert "kinda_int(" in contents, "Expected kinda_int in transformed output"
    assert "sorta_print(" in contents, "Expected sorta_print in transformed output"


def test_blank_line_passthrough():
    line = "\n"
    result = transform_line(line)
    assert result == [""], f"Expected [''] but got {result}"


def test_comment_line_passthrough():
    line = "  # this is a comment\n"
    result = transform_line(line)
    assert result == [line], f"Expected [{line!r}] but got {result}"


@pytest.mark.parametrize(
    "line",
    [
        "x = 42\n",
        "    if x > 0:\n",
        "def my_func():\n",
        "import math\n",
        '"""This is a docstring"""\n',
    ],
)
def test_normal_python_lines_passthrough(line):
    result = transform_line(line)
    assert result == [line], f"Line should be unchanged: {line.strip()}"
