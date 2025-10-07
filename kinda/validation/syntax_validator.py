#!/usr/bin/env python3
"""Syntax validation module for Kinda-Lang files."""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class SyntaxValidator:
    """Validate syntax of .knda files."""

    def __init__(self, strict: bool = True):
        self.strict = strict
        self.errors: List[str] = []

    def validate_file(self, file_path: Path) -> bool:
        """Validate syntax of a single file."""
        try:
            # Use kinda transform to validate syntax
            result = subprocess.run(
                ["python", "-m", "kinda.cli", "transform", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                self.errors.append(f"{file_path}: {result.stderr}")
                return False

            return True

        except subprocess.TimeoutExpired:
            self.errors.append(f"{file_path}: Syntax validation timeout")
            return False
        except Exception as e:
            self.errors.append(f"{file_path}: {e}")
            return False

    def validate_directory(self, directory: Path) -> Dict[str, bool]:
        """Validate all .knda files in directory."""
        results = {}

        for knda_file in directory.rglob("*.knda"):
            results[str(knda_file)] = self.validate_file(knda_file)

        return results


def main():
    """CLI interface for syntax validator."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate Kinda-Lang syntax")
    parser.add_argument("paths", nargs="*", help="Files or directories to validate")
    parser.add_argument("--strict", action="store_true", help="Strict validation mode")

    args = parser.parse_args()

    validator = SyntaxValidator(strict=args.strict)

    # Default to current directory if no paths provided
    paths = args.paths or ["."]

    success_count = 0
    total_count = 0

    for path_str in paths:
        path = Path(path_str)

        if path.is_file() and path.suffix == ".knda":
            total_count += 1
            if validator.validate_file(path):
                success_count += 1
                print(f"✅ {path}")
            else:
                print(f"❌ {path}")

        elif path.is_dir():
            results = validator.validate_directory(path)
            for file_path, success in results.items():
                total_count += 1
                if success:
                    success_count += 1
                    print(f"✅ {file_path}")
                else:
                    print(f"❌ {file_path}")

    if validator.errors:
        print("\n🚨 Syntax Errors:")
        for error in validator.errors:
            print(f"   {error}")

    print(f"\n📊 Results: {success_count}/{total_count} files passed syntax validation")

    # Exit with error code if any failures
    sys.exit(0 if success_count == total_count else 1)


if __name__ == "__main__":
    main()
