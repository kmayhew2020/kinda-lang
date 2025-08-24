from pathlib import Path
from typing import List
from kinda.langs.python.runtime_gen import generate_runtime_helpers, generate_runtime
from kinda.grammar.python.constructs import KindaPythonConstructs
from kinda.grammar.python.matchers import match_python_construct

used_helpers = set()

def _process_conditional_block(lines: List[str], start_index: int, output_lines: List[str], indent: str) -> int:
    """
    Process a conditional block (~sometimes or ~maybe) with proper nesting support.
    Returns the index after processing the block.
    """
    i = start_index
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Stop at closing brace
        if stripped == "}":
            i += 1  # Skip the closing brace
            break
        
        # Empty lines or comments - pass through with indentation
        if not stripped or stripped.startswith("#"):
            output_lines.append(indent + line)
            i += 1
            continue

        # Handle nested conditional constructs
        if stripped.startswith("~sometimes") or stripped.startswith("~maybe"):
            transformed_nested = transform_line(line)
            output_lines.extend([indent + l for l in transformed_nested])
            i += 1
            # Recursively process nested block with increased indentation
            i = _process_conditional_block(lines, i, output_lines, indent + "    ")
        else:
            # Regular kinda constructs or normal python
            transformed_block = transform_line(line)
            output_lines.extend([indent + l for l in transformed_block])
            i += 1

    return i

def transform_line(line: str) -> List[str]:
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

    elif key == "kinda_binary":
        if len(groups) == 2 and groups[1]:  # Custom probabilities provided
            var, probs = groups
            used_helpers.add("kinda_binary")
            transformed_code = f"{var} = kinda_binary({probs})"
        else:  # Default probabilities
            var = groups[0]
            used_helpers.add("kinda_binary")
            transformed_code = f"{var} = kinda_binary()"

    elif key == "sorta_print":
        (expr,) = groups
        used_helpers.add("sorta_print")
        transformed_code = f"sorta_print({expr})"

    elif key == "sometimes":
        used_helpers.add("sometimes")
        cond = groups[0].strip() if groups and groups[0] else ""
        transformed_code = f"if sometimes({cond}):" if cond else "if sometimes():"

    elif key == "maybe":
        used_helpers.add("maybe")
        cond = groups[0].strip() if groups and groups[0] else ""
        transformed_code = f"if maybe({cond}):" if cond else "if maybe():"

    elif key == "fuzzy_reassign":
        var, val = groups
        used_helpers.add("fuzzy_assign")
        transformed_code = f"{var} = fuzzy_assign('{var}', {val})"

    else:
        transformed_code = stripped  # fallback

    # Debug removed for clean UX

    return [original_line.replace(stripped, transformed_code)]


def transform_file(path: Path, target_language="python") -> str:
    lines = path.read_text().splitlines()
    output_lines = []

    # Clean output - no debug spam

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # Processing silently

        if stripped.startswith("~sometimes") or stripped.startswith("~maybe"):
            output_lines.extend(transform_line(line))
            i += 1

            # Process block with proper nesting support
            i = _process_conditional_block(lines, i, output_lines, "    ")
        else:
            output_lines.extend(transform_line(line))
            i += 1

    header = ""
    if used_helpers:
        helpers = ", ".join(sorted(used_helpers))
        header = f"from kinda.langs.{target_language}.runtime.fuzzy import {helpers}\n\n"

    return header + "\n".join(output_lines)


def transform(input_path: Path, out_dir: Path) -> List[Path]:
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