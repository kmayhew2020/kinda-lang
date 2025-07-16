from pathlib import Path
from kinda.grammar.python.constructs_py import KindaPythonConstructs as KindaConstructs

def generate_runtime_helpers(used_keys, output_path: Path, constructs):
    code = []

    for key in sorted(used_keys):
        construct = constructs.get(key)
        if construct and "body" in construct:
            code.append(construct["body"])  # ✅ grab the actual string

    runtime_path = output_path / "fuzzy.py"
    runtime_path.write_text("\n\n".join(code) + "\n")

    return runtime_path


def generate_runtime(output_dir: Path):
    # Create directory structure
    output_dir.mkdir(parents=True, exist_ok=True)

    # Ensure __init__.py files exist for module recognition
    init_files = [
        Path("kinda/__init__.py"),
        Path("kinda/runtime/__init__.py"),
        output_dir / "__init__.py",
    ]
    for f in init_files:
        f.touch()

    # Build runtime code
    lines = [
        "# Auto-generated fuzzy runtime for Python\n",
        "import random\n",
        "\n"
    ]

    for key, meta in KindaConstructs.items():
        runtime_code = meta.get("runtime", {}).get("python")
        if runtime_code:
            lines.append(runtime_code + "\n")
        elif "body" in meta:
            lines.append(meta["body"] + "\n")
        elif meta["type"] == "print":
            lines.append(
                "def sorta_print(*args):\n"
                "    if random.random() < 0.8:\n"
                "        print(*args)\n\n"
            )
        elif meta["type"] == "conditional":
            lines.append(
                "def sometimes(cond):\n"
                "    return cond and random.random() < 0.5\n\n"
            )

    # Write to fuzzy.py
    runtime_file = output_dir / "fuzzy.py"
    runtime_file.write_text("".join(lines))

    print(f"✅ Wrote runtime to {runtime_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="kinda/runtime/python",
        help="Output directory for generated runtime",
    )
    args = parser.parse_args()
    generate_runtime(Path(args.out))