from pathlib import Path
from typing import Dict, Any, Set
from kinda.grammar.python.constructs import KindaPythonConstructs as KindaConstructs


def generate_runtime_helpers(
    used_keys: Set[str], output_path: Path, constructs: Dict[str, Any]
) -> str:
    """
    Dynamically appends helpers to fuzzy.py based on what was actually used during transformation.
    """
    code = []

    for key in sorted(used_keys):
        construct = constructs.get(key)
        if construct and isinstance(construct, dict) and "body" in construct:
            code.append(construct["body"])

    if code:
        runtime_path = output_path / "fuzzy.py"
        with runtime_path.open("a") as f:
            f.write("\n\n" + "\n\n".join(code) + "\n")

    return "\n\n".join(code) + "\n"


def generate_runtime(output_dir: Path) -> None:
    """
    Auto-generates the core fuzzy.py file using all known construct definitions.
    Typically writes to: kinda/langs/python/runtime/
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Ensure __init__.py files exist
    init_files = [
        Path("kinda/__init__.py"),
        Path("kinda/langs/__init__.py"),
        Path("kinda/langs/python/__init__.py"),
        output_dir / "__init__.py",
    ]
    for f in init_files:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.touch()

    # Core runtime header
    lines = [
        "# Auto-generated fuzzy runtime for Python\n",
        "# Uses centralized seeded RNG from PersonalityContext for reproducibility\n",
        "env = {}\n\n",
    ]

    # Add default runtime implementations
    already_added = set()

    for key in sorted(KindaConstructs.keys()):
        meta = KindaConstructs[key]

        if not isinstance(meta, dict):
            continue

        runtime_info = meta.get("runtime")
        if isinstance(runtime_info, dict):
            runtime_code = runtime_info.get("python")
            if runtime_code and isinstance(runtime_code, str):
                lines.append(runtime_code.strip() + "\n\n")
                lines.append(f'env["{key}"] = {key}\n\n')
                already_added.add(key)
        elif "body" in meta:
            body = meta["body"]
            if isinstance(body, str):
                body_stripped = body.strip()
                lines.append(body_stripped + "\n\n")
                if "def " in body_stripped:
                    func_name = body_stripped.split("def ")[1].split("(")[0].strip()
                    lines.append(f'env["{func_name}"] = {func_name}\n\n')
                    already_added.add(key)
                else:
                    print(f"⚠️ No 'def' found in body for key: {key}, skipping env assignment")

    # Add built-ins if not already defined
    if "sorta_print" not in already_added:
        lines.append(
            "def sorta_print(*args):\n"
            "    from kinda.personality import chaos_random\n"
            "    if chaos_random() < 0.8:\n"
            "        print('[print]', *args)\n"
            "    else:\n"
            "        print('[shrug]', *args)\n"
        )
        lines.append("env['sorta_print'] = sorta_print\n\n")
    if "sometimes" not in already_added:
        lines.append(
            "def sometimes():\n"
            "    from kinda.personality import chaos_random\n"
            "    return chaos_random() < 0.5\n"
        )
        lines.append("env['sometimes'] = sometimes\n\n")

    # Write full runtime file
    runtime_file = output_dir / "fuzzy.py"
    # Generate runtime silently - no debug spam
    runtime_file.write_text("".join(lines), encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="kinda/langs/python/runtime",
        help="Output directory for generated runtime",
    )
    args = parser.parse_args()
    generate_runtime(Path(args.out))
