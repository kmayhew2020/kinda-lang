# kinda/langs/python/transformer_py.py

from pathlib import Path
from kinda.grammar.matchers import match_construct
from kinda.grammar.constructs import KindaConstructs

used_helpers = set()

def transform_line(line):
    stripped = line.strip()

    if not stripped:
        return ""

    if stripped.startswith("#"):  # python-style comment
        return stripped

    key, groups = match_construct(line)
    if not key:
        return line

    if key == "kinda int":
        var, expr = groups
        used_helpers.add("kinda_int")
        return f"{var} = kinda_int('{var}', {expr})"

    elif key == "~=":
        var, expr = groups
        used_helpers.add("kinda_int")
        return f"{var} = kinda_int('{var}', {expr})"

    elif key == "sorta print":
        (expr,) = groups
        used_helpers.add("sorta_print")
        return f"sorta_print({expr})"

    elif key == "sometimes":
        (cond,) = groups
        used_helpers.add("sometimes")
        return f"if sometimes({cond}):"

    return line


def transform_file(path: Path, target_language="python"):
    lines = path.read_text().splitlines()
    output_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("sometimes"):
            block_lines = []
            transformed = transform_line(line)
            output_lines.append(transformed)
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("}"):
                block_lines.append("    " + transform_line(lines[i].strip()))
                i += 1
            output_lines.extend(block_lines)
        else:
            output_lines.append(transform_line(lines[i]))
        i += 1

    header = ""
    if used_helpers:
        helpers = ", ".join(sorted(used_helpers))
        header = f"from kinda.runtime.{target_language}.fuzzy import {helpers}\n\n"

    return header + "\n".join(output_lines)