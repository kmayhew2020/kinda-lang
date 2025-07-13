# kinda/cli.py

import argparse
from pathlib import Path
from kinda import transformer
from kinda.run import execute

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

    # -------------------------
    # kinda transform ...
    # -------------------------
    transform_parser = subparsers.add_parser("transform", help="Only transform to .py")
    transform_parser.add_argument("input", help="Path to .knda file or directory")
    transform_parser.add_argument("--out", default="build", help="Output directory")

    # Parse arguments
    args = parser.parse_args()

    # Dispatch
    if args.command == "run":
        # (Optional) someday: set config.chaos_level = args.chaos_level
        execute(args.input, out_dir=args.out)

    elif args.command == "transform":
        input_path = Path(args.input)
        out_dir = Path(args.out)
        output_paths = transformer.transform(input_path, out_dir=out_dir)
        for path in output_paths:
            print(f"✅ Transformed: {path}")