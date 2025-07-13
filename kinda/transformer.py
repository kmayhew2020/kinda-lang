# kinda/transformer.py

import re
import sys
from pathlib import Path
from kinda.grammar.matchers import match_construct
from kinda.grammar.constructs import KindaConstructs

# Track which helpers to import
used_helpers = set()

def transform_line(line):
    stripped = line.strip()

    if not stripped:
        return ""  # ignore blank lines

    if stripped.startswith("//"):
        return f"# {stripped[2:].strip()}"  # or just return "" to drop comment

    key, groups = match_construct(line)
    if not key:
        return line  # fallback to original line

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


def transform_file(path, target_language="python"):
    lines = Path(path).read_text().splitlines()
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
            output_lines.append(transform_line(line))
        i += 1

    header = ""
    if used_helpers:
        helpers = ", ".join(sorted(used_helpers))
        header = f"from kinda.runtime.{target_language}.fuzzy import {helpers}\n\n"

    return header + "\n".join(output_lines)

# ───────────────────────────────────────────────
# CLI Entry Point
# ───────────────────────────────────────────────

import os

BUILD_DIR = "build"

def write_transformed_file(input_path, transformed_code):
    input_path = Path(input_path)
    output_path = Path(BUILD_DIR) / input_path.with_suffix(".py").name
    Path(BUILD_DIR).mkdir(exist_ok=True)
    output_path.write_text(transformed_code)
    return output_path

def transform(input_path: Path, out_dir: Path = Path("build")):
    """
    Public API to transform a .knda file or directory.
    Returns list of output paths.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    output_files = []

    if input_path.is_dir():
        for file in input_path.rglob("*.knda"):
            transformed = transform_file(file)
            output_path = out_dir / file.with_suffix(".py").name
            write_transformed_file(file, transformed)
            output_files.append(output_path)
    elif input_path.is_file():
        transformed = transform_file(input_path)
        output_path = out_dir / input_path.with_suffix(".py").name
        write_transformed_file(input_path, transformed)
        output_files.append(output_path)
    else:
        raise ValueError(f"{input_path} is neither a file nor a directory.")

    return output_files

if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to .knda file or directory")
    parser.add_argument("--out", default="build", help="Output directory")

    args = parser.parse_args()
    input_path = Path(args.input)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_dir():
        for file in input_path.rglob("*.knda"):
            transformed = transform_file(file)
            output_path = out_dir / file.with_suffix(".py").name
            write_transformed_file(output_path, transformed)
            print(f"✅ Transformed: {file} → {output_path}")
    elif input_path.is_file():
        transformed = transform_file(input_path)
        output_path = out_dir / input_path.with_suffix(".py").name
        write_transformed_file(output_path, transformed)
        print(f"✅ Transformed: {input_path} → {output_path}")
    else:
        print(f"❌ Error: {input_path} is neither a file nor a directory.")
