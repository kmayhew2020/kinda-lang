# kinda/cli.py

import argparse
from pathlib import Path
from kinda.run import execute

def get_transformer(lang):
    if lang == "python":
        from kinda.langs.python import transformer_py
        return transformer_py
    elif lang == "c":
        return None  # 🔕 Disable C for now
    else:
        raise ValueError(f"Unsupported language: {lang}")


        
def detect_language(file_path: Path, override: str = None) -> str:
    if override:
        return override.lower()
    name = file_path.name.lower()
    if name.endswith(".py.knda"):
        return "python"
    if name.endswith(".c.knda"):
        return "c"
    raise ValueError("Could not infer language from filename. Use --lang.")


def main():
    parser = argparse.ArgumentParser(
        prog="kinda",
        description="🌀 Kinda Language CLI – inject chaos into your code"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # -------------------------
    # kinda run ...
    # -------------------------
    run_parser = subparsers.add_parser("run", help="Transform and execute a .knda file")
    run_parser.add_argument("input", help="Path to .knda file")
    run_parser.add_argument("--out", default="build", help="Output directory")
    run_parser.add_argument("--test", action="store_true", help="Enable test mode (less chaos)")
    run_parser.add_argument("--chaos-level", type=int, default=5, help="Chaos intensity (0–10)")
    run_parser.add_argument("--lang", default=None, choices=["c", "python"], help="Language flavor of .knda file")

    # -------------------------
    # kinda transform ...
    # -------------------------
    transform_parser = subparsers.add_parser("transform", help="Only transform to .py")
    transform_parser.add_argument("input", help="Path to .knda file or directory")
    transform_parser.add_argument("--out", default="build", help="Output directory")
    transform_parser.add_argument("--lang", default=None, choices=["c", "python"], help="Language flavor of .knda file")

    # -------------------------
    # kinda interpret ...
    # -------------------------
    interp_parser = subparsers.add_parser("interpret", help="Run the interpreter in interactive mode")
    interp_parser.add_argument("input", help="Path to .knda file")

    # Parse arguments
    args = parser.parse_args()

    # Dispatch
    if args.command == "run":
        # (Optional) someday: set config.chaos_level = args.chaos_level
        input_path = Path(args.input)
        lang = detect_language(input_path, args.lang)
        transformer = get_transformer(lang)
        execute(args.input, out_dir=args.out, transformer=transformer)

    elif args.command == "transform":
        input_path = Path(args.input)
        out_dir = Path(args.out)
        lang = detect_language(Path(args.input), args.lang)
        transformer = get_transformer(lang)
        if transformer is None:
            print(f"[skipping] No transformer for language: {lang}")
            return
        output_paths = transformer.transform(input_path, out_dir=out_dir)
        for path in output_paths:
            print(f"✅ Transformed: {path}")

    elif args.command == "interpret":
        from kinda.interpreter import repl  # You'll create this module soon
        repl.run_interpreter(args.input)