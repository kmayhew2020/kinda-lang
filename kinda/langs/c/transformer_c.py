# kinda/langs/c/transformer_c.py

"""
Kinda-Lang C Transformer
Transforms .knda files to native C code with fuzzy logic support.
"""

import re
import sys
from pathlib import Path
from typing import List, Set
from kinda.grammar.c.matchers_c import match_c_construct
from kinda.grammar.c.constructs_c import KindaCConstructs

used_helpers: Set[str] = set()

def _process_conditional_block(lines: List[str], start_index: int, output_lines: List[str], indent: str) -> int:
    """
    Process a conditional block (sometimes or maybe) with proper nesting support.
    Returns the index after processing the block.
    """
    i = start_index
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Stop at closing brace
        if stripped == "}":
            output_lines.append(indent[:-4] + "}")  # Reduce indent for closing brace
            i += 1
            break
        
        # Empty lines or comments - pass through with indentation
        if not stripped or stripped.startswith("//"):
            if stripped.startswith("//"):
                output_lines.append(indent + "// " + stripped[2:].strip())
            else:
                output_lines.append("")
            i += 1
            continue

        # Handle nested conditional constructs
        if stripped.startswith("sometimes") or stripped.startswith("maybe"):
            transformed_nested = transform_line(line)
            output_lines.extend([indent + l for l in transformed_nested])
            i += 1
            # Recursively process nested block with increased indentation
            i = _process_conditional_block(lines, i, output_lines, indent + "    ")
        else:
            # Regular kinda constructs or normal C code
            transformed_block = transform_line(line)
            output_lines.extend([indent + l for l in transformed_block])
            i += 1

    return i

def transform_line(line: str) -> List[str]:
    """Transform a single line from kinda-lang C to native C."""
    original_line = line
    stripped = line.strip()

    if not stripped:
        return [""]
    if stripped.startswith("//"):
        return [original_line]

    key, groups = match_c_construct(stripped)
    if not key:
        return [original_line]

    if key == "kinda_int":
        var, val = groups
        used_helpers.add("kinda_int")
        transformed_code = f"int {var} = kinda_int({val});"

    elif key == "kinda_int_decl":
        var, val = groups
        used_helpers.add("kinda_int") 
        transformed_code = f"int {var} = kinda_int({val});"

    elif key == "kinda_binary":
        if len(groups) == 2 and groups[1]:  # Custom probabilities provided
            var, probs = groups
            used_helpers.add("kinda_binary_custom")
            # Parse probabilities like "0.4, 0.3"
            prob_parts = [p.strip() for p in probs.split(',')]
            if len(prob_parts) >= 2:
                pos_prob = int(float(prob_parts[0]) * 100)
                neg_prob = int(float(prob_parts[1]) * 100)
                transformed_code = f"int {var} = kinda_binary_custom({pos_prob}, {neg_prob});"
            else:
                transformed_code = f"int {var} = kinda_binary();"
        else:  # Default probabilities
            var = groups[0]
            used_helpers.add("kinda_binary_default")
            transformed_code = f"int {var} = kinda_binary();"

    elif key == "sorta_print":
        expr = groups[0]
        used_helpers.add("sorta_print")
        # Parse the expression to handle format strings
        if ',' in expr:
            # Split on comma and format properly
            parts = [p.strip() for p in expr.split(',')]
            if len(parts) >= 2:
                # Assume first part is string literal, rest are variables
                fmt_str = parts[0]
                vars_str = ', '.join(parts[1:])
                # Convert string literal to format string by adding %d for integers
                if fmt_str.startswith('"') and fmt_str.endswith('"'):
                    fmt_content = fmt_str[1:-1]  # Remove quotes
                    fmt_content = fmt_content + " %d"  # Add format specifier
                    transformed_code = f'sorta_print("{fmt_content}", {vars_str});'
                else:
                    transformed_code = f"sorta_print({expr});"
            else:
                transformed_code = f"sorta_print({expr});"
        else:
            transformed_code = f"sorta_print({expr});"

    elif key == "sometimes":
        used_helpers.add("sometimes")
        cond = groups[0].strip() if groups and groups[0] else ""
        if cond:
            transformed_code = f"if (sometimes({cond})) {{"
        else:
            transformed_code = f"if (sometimes_random()) {{"

    elif key == "maybe":
        used_helpers.add("maybe")
        cond = groups[0].strip() if groups and groups[0] else ""
        if cond:
            transformed_code = f"if (maybe({cond})) {{"
        else:
            transformed_code = f"if (maybe_random()) {{"

    elif key == "fuzzy_reassign":
        var, val = groups
        used_helpers.add("fuzzy_assign")
        transformed_code = f"{var} = fuzzy_assign({val});"

    else:
        transformed_code = stripped  # fallback

    return [original_line.replace(stripped, transformed_code)]


def transform_file(path: Path, target_language="c") -> str:
    """Transform a .knda file to C code."""
    lines = path.read_text().splitlines()
    output_lines = []

    # Add includes at the top
    header_lines = [
        '#include <stdio.h>',
        '#include <stdlib.h>', 
        '#include "fuzzy.h"',
        '',
        'int main() {'
    ]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("sometimes") or stripped.startswith("maybe"):
            output_lines.extend(transform_line(line))
            i += 1
            # Process block with proper nesting support
            i = _process_conditional_block(lines, i, output_lines, "    ")
        else:
            output_lines.extend(transform_line(line))
            i += 1

    # Add proper indentation for main function body
    indented_lines = []
    for line in output_lines:
        if line.strip():
            indented_lines.append("    " + line)
        else:
            indented_lines.append("")
            
    # Add return statement and close main
    footer_lines = [
        "    return 0;",
        "}"
    ]

    return "\n".join(header_lines + indented_lines + footer_lines)


def transform(input_path: Path, out_dir: Path) -> List[Path]:
    """
    Public API to transform a .knda file or directory to C code.
    Returns list of output paths.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    output_paths = []

    # Copy fuzzy.h header to output directory
    fuzzy_header_src = Path(__file__).parent / "runtime" / "fuzzy.h"
    fuzzy_header_dst = out_dir / "fuzzy.h"
    if fuzzy_header_src.exists():
        fuzzy_header_dst.write_text(fuzzy_header_src.read_text())

    if input_path.is_dir():
        for file in input_path.glob("**/*.knda"):
            if file.name.endswith(".c.knda"):
                output_code = transform_file(file)
                relative_path = file.relative_to(input_path)
                new_name = file.name.replace(".c.knda", ".c")
                output_file_path = out_dir / relative_path.with_name(new_name)
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                output_file_path.write_text(output_code)
                output_paths.append(output_file_path)
    else:
        output_code = transform_file(input_path)
        if input_path.name.endswith(".c.knda"):
            new_name = input_path.name.replace(".c.knda", ".c")
        else:
            new_name = input_path.stem + ".c"
        output_file_path = out_dir / new_name
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        output_file_path.write_text(output_code)
        output_paths.append(output_file_path)

    return output_paths


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Transform kinda-lang files to C")
    parser.add_argument("input", help="Path to .knda file or directory")
    parser.add_argument("--out", default="build", help="Output directory")

    args = parser.parse_args()
    input_path = Path(args.input)
    out_dir = Path(args.out)

    try:
        output_paths = transform(input_path, out_dir)
        for output_path in output_paths:
            print(f"✅ Transformed: {input_path} → {output_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
