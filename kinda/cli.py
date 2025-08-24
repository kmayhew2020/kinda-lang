# kinda/cli.py

import argparse
import sys
from pathlib import Path


def get_transformer(lang: str):
    if lang == "python":
        from kinda.langs.python import transformer
        return transformer
    elif lang == "c":
        # C path not ready yet
        return None
    else:
        raise ValueError(f"Unsupported language: {lang}")


def detect_language(path: Path, forced: str | None) -> str:
    """Tiny heuristic; lets --lang override."""
    if forced:
        return forced
    name = str(path)
    if name.endswith(".py.knda") or name.endswith(".py"):
        return "python"
    # Default to python for now
    return "python"


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(prog="kinda", description="Kinda CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_transform = sub.add_parser(
        "transform", help="Transform a Kinda file to its host language"
    )
    p_transform.add_argument("input", help="Input file (e.g., foo.py.knda)")
    p_transform.add_argument(
        "--out", default="build", help="Output directory (default: build)"
    )
    p_transform.add_argument("--lang", default=None, help="Force language (e.g., python)")

    p_run = sub.add_parser("run", help="Transform then execute")
    p_run.add_argument("input", help="Input file (e.g., foo.py.knda)")
    p_run.add_argument("--lang", default=None, help="Force language (e.g., python)")

    p_interpret = sub.add_parser("interpret", help="Interpret using in-memory runtime")
    p_interpret.add_argument("input", help="Input file (e.g., foo.py.knda)")
    p_interpret.add_argument("--lang", default=None, help="Force language (e.g., python)")

    args = parser.parse_args(argv)

    if args.command == "transform":
        input_path = Path(args.input)
        out_dir = Path(args.out)
        lang = detect_language(input_path, args.lang)
        transformer = get_transformer(lang)
        if transformer is None:
            print(f"[skipping] No transformer for language: {lang}")
            return 0
        output_paths = transformer.transform(input_path, out_dir=out_dir)
        for path in output_paths:
            print(f"✅ Transformed: {path}")
        return 0

    if args.command == "run":
        input_path = Path(args.input)
        lang = detect_language(input_path, args.lang)
        transformer = get_transformer(lang)
        if transformer is None:
            print(f"[run] Unsupported language: {lang}")
            return 1
        out_dir = Path(".kinda-build")
        out_paths = transformer.transform(input_path, out_dir=out_dir)
        if lang == "python":
            import runpy

            # Naively execute the first produced file
            runpy.run_path(str(out_paths[0]), run_name="__main__")
            return 0
        print(f"[run] Unsupported language runtime: {lang}")
        return 1

    if args.command == "interpret":
        input_path = Path(args.input)
        lang = detect_language(input_path, args.lang)
        if lang == "python":
            from kinda.interpreter.repl import run_interpreter
            run_interpreter(str(input_path), lang)
            return 0
        print(f"[interpret] Unsupported language: {lang}")
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())