# kinda/langs/python/transformer_py.py

from pathlib import Path
from kinda.codegen.python import generate_runtime_helpers, generate_runtime
from kinda.grammar.python.constructs_py import KindaPythonConstructs
from kinda.grammar.python.matchers_py import match_python_construct


used_helpers = set()

def transform_line(line):
    original_line = line
    stripped = line.strip()

    if not stripped:
        return ""

    if stripped.startswith("#"):  # python-style comment
        return original_line

    key, groups = match_python_construct(stripped)
    if not key:
        return original_line  # preserve indentation if no match

    # Apply Kinda transforms
    if key == "kinda_int":
        var, val = groups
        used_helpers.add("kinda_int")
        transformed_code = f"{var} = kinda_int({val})"

    elif key == "sorta_print":
        (expr,) = groups
        used_helpers.add("sorta_print")
        transformed_code = f"sorta_print({expr})"

    elif key == "sometimes":
        used_helpers.add("sometimes")
        cond = groups[0].strip() if groups and groups[0] else ""
        if cond:
            transformed_code = f"if sometimes({cond}):"
        else:
            transformed_code = "if sometimes():"

    else:
        transformed_code = stripped  # fallback, shouldn't hit

    print(f"[debug] Matching line: '{line.strip()}' → key={key}, groups={groups}")
    print(f"[transformer] {stripped}  →  {transformed_code} yeah yeah")  # Debug output

    return original_line.replace(stripped, transformed_code)

def transform_file(path: Path, target_language="python"):
    lines = path.read_text().splitlines()
    output_lines = []

    print(f"[transform_file] Transforming file: {path} {lines}")

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        print(f"[transform_file] Transforming line: {path} {line}")
        if line.startswith("sometimes"):
            transformed = transform_line(line)
            print(f"[transform_file] Transformed line: {path} {transformed}")
            output_lines.append(transformed)
            i += 1

            # Capture all following non-blank, non-construct lines
            while i < len(lines):
                next_line = lines[i]
                stripped = next_line.strip()

                # stop if it's a new top-level construct or blank line
                if not stripped or stripped.startswith("kinda") or stripped.startswith("sometimes"):
                    break

                # indent and transform this line under the fuzzy if block
                output_lines.append("    " + transform_line(stripped))
                i += 1
        else:
            output_lines.append(transform_line(lines[i]))
        i += 1

    header = ""
    if used_helpers:
        helpers = ", ".join(sorted(used_helpers))
        header = f"from kinda.runtime.{target_language}.fuzzy import {helpers}\n\n"

    return header + "\n".join(output_lines)

def transform(input_path: Path, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(input_path)
    output_paths = []

    if input_path.is_file():
        print(f"[transform] Starting transform_file for: {input_path}")
        output_code = transform_file(input_path)

        # Strip the .py.knda or .knda extension properly
        if input_path.name.endswith(".py.knda"):
            base_name = input_path.name[:-len(".py.knda")]
        else:
            base_name = input_path.stem

        output_path = out_dir / (base_name + ".py")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_code)
        output_paths.append(output_path)


    elif input_path.is_dir():
        for file in input_path.glob("**/*.knda"):
            output_code = transform_file(file)
            relative_path = file.relative_to(input_path)
            output_file_path = out_dir / relative_path.with_suffix(".py")
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            output_file_path.write_text(output_code)
            output_paths.append(output_file_path)

    runtime_path = Path(__file__).parent.parent.parent / "runtime" / "python"
    runtime_path.mkdir(parents=True, exist_ok=True)

    generate_runtime_helpers(used_helpers, runtime_path, KindaPythonConstructs)
    generate_runtime(runtime_path)

    return output_paths
