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
    parser = argparse.ArgumentParser(
        prog="kinda", 
        description="🤷 A programming language for people who aren't totally sure"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_transform = sub.add_parser(
        "transform", help="Turn your kinda code into actual code (how responsible of you)"
    )
    p_transform.add_argument("input", help="Your .knda file (yes, it needs the extension)")
    p_transform.add_argument(
        "--out", default="build", help="Where to dump the results (default: build)"
    )
    p_transform.add_argument("--lang", default=None, help="Force a language if you're feeling decisive")

    p_run = sub.add_parser("run", help="Transform then execute (living dangerously, I see)")
    p_run.add_argument("input", help="The .knda file you want to run")
    p_run.add_argument("--lang", default=None, help="Override language detection (sure, why not)")

    p_interpret = sub.add_parser("interpret", help="Run directly in fuzzy runtime (maximum chaos mode)")
    p_interpret.add_argument("input", help="Your questionable life choices in .knda form")
    p_interpret.add_argument("--lang", default=None, help="Force language (you know what you did)")

    args = parser.parse_args(argv)

    if args.command == "transform":
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"🤔 '{args.input}' doesn't exist. Are you sure you typed that right?")
            return 1
        out_dir = Path(args.out)
        lang = detect_language(input_path, args.lang)
        transformer = get_transformer(lang)
        if transformer is None:
            print(f"🤷 Sorry, I don't speak {lang} yet. Try Python maybe?")
            return 0
        output_paths = transformer.transform(input_path, out_dir=out_dir)
        for path in output_paths:
            print(f"✨ Transformed your chaos into: {path}")
        print(f"🎲 Generated {len(output_paths)} file(s). Hope they work!")
        return 0

    if args.command == "run":
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"🤷‍♂️ Can't find '{args.input}'. Did you make that up?")
            return 1
        lang = detect_language(input_path, args.lang)
        transformer = get_transformer(lang)
        if transformer is None:
            print(f"🙄 Can't run {lang} files yet. Python works though.")
            return 1
        out_dir = Path(".kinda-build")
        out_paths = transformer.transform(input_path, out_dir=out_dir)
        if lang == "python":
            import runpy
            print("🎮 Running your questionable code...")
            # Execute the transformed file
            runpy.run_path(str(out_paths[0]), run_name="__main__")
            print("🎉 Well, that didn't crash. Success?")
            return 0
        print(f"😅 I can transform {lang} but can't run it. Try 'transform' instead?")
        return 1

    if args.command == "interpret":
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"🙃 '{args.input}' is nowhere to be found. Try again?")
            return 1
        lang = detect_language(input_path, args.lang)
        if lang == "python":
            from kinda.interpreter.repl import run_interpreter
            print("🔮 Entering the chaos dimension...")
            run_interpreter(str(input_path), lang)
            print("🌪️ Chaos complete. Reality may have shifted slightly.")
            return 0
        print(f"🤨 Interpret mode only works with Python. What are you even trying to do?")
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())