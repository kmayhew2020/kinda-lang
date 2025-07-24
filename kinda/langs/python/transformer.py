from pathlib import Path
from kinda.langs.python.runtime_gen import generate_runtime_helpers, generate_runtime
from kinda.grammar.python.constructs import KindaPythonConstructs
from kinda.grammar.python.matchers import match_python_construct

used_helpers = set()

def transform_line(line: str) -> list[str]:
    original_line = line
    stripped = line.strip()

    if not stripped:
        return [""]
    if stripped.startswith("#"):
        return [original_line]

    key, groups = match_python_construct(stripped)
    if not key:
        return [original_line]

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
        transformed_code = f"if sometimes({cond}):" if cond else "if sometimes():"

    else:
        transformed_code = stripped  # fallback

    print(f"[debug] Matching line: '{stripped}' → key={key}, groups={groups}")
    print(f"[transformer] {stripped}  →  {transformed_code} yeah yeah")

    return [original_line.replace(stripped, transformed_code)]


def transform_file(path: Path, target_language="python") -> str:
    lines = path.read_text().splitlines()
    output_lines = []

    print(f"[transform_file] Transforming file: {path}")

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        print(f"[transform_file] Transforming line: {stripped}")

        if stripped.startswith("sometimes"):
            output_lines.extend(transform_line(line))
            i += 1

            # Add indented block under sometimes
            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()

                if not next_stripped or next_stripped.startswith("kinda") or next_stripped.startswith("sometimes"):
                    break

                transformed_block = transform_line(next_line)
                output_lines.extend(["    " + l for l in transformed_block])
                i += 1
        else:
            output_lines.extend(transform_line(line))
            i += 1

    header = ""
    if used_helpers:
        helpers = ", ".join(sorted(used_helpers))
        header = f"from kinda.langs.{target_language}.runtime.fuzzy import {helpers}\n\n"

    return header + "\n".join(output_lines)


def transform(input_path: Path, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(input_path)
    output_paths = []

    if input_path.is_dir():
        for file in input_path.glob("**/*.knda"):
            output_code = transform_file(file)
            relative_path = file.relative_to(input_path)

            if file.name.endswith(".py.knda"):
                new_name = file.name.replace(".py.knda", ".py")
            else:
                new_name = file.stem + ".py"

            output_file_path = out_dir / relative_path.with_name(new_name)
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            output_file_path.write_text(output_code)
            output_paths.append(output_file_path)
    else:
        output_code = transform_file(input_path)
        new_name = input_path.name.replace(".py.knda", ".py")
        output_file_path = out_dir / new_name
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        output_file_path.write_text(output_code)
        output_paths.append(output_file_path)

    # Generate fuzzy runtime
    runtime_path = Path(__file__).parent.parent.parent / "langs" / "python" / "runtime"
    runtime_path.mkdir(parents=True, exist_ok=True)

    generate_runtime_helpers(used_helpers, runtime_path, KindaPythonConstructs)
    generate_runtime(runtime_path)

    return output_paths