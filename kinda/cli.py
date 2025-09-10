# kinda/cli.py

import argparse
import os
import sys
from pathlib import Path
from typing import Union, Optional

# Optional chardet import for encoding detection
try:
    import chardet

    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

# Import personality system
from kinda.personality import PersonalityContext, PERSONALITY_PROFILES


def safe_print(text: str) -> None:
    """Print text with Windows-safe encoding fallbacks"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback for Windows: replace problematic emojis with ASCII
        fallback = (
            text.replace("✨", "*")  # sparkle -> asterisk
            .replace("🎲", "*")  # die -> asterisk
            .replace("[shrug]", "?")  # shrug -> question mark
            .replace("📚", "*")  # book -> asterisk
            .replace("📝", "*")  # memo -> asterisk
            .replace("🎯", "*")  # target -> asterisk
            .replace("[?]", "?")  # thinking -> question mark
            .replace("[shrug]‍♂️", "?")  # shrug man -> question mark
            .replace("🙄", "~")  # eye roll -> tilde
            .replace("🎮", "*")  # game controller -> asterisk
            .replace("🎉", "!")  # party -> exclamation
            .replace("😅", "~")  # sweat smile -> tilde
            .replace("🙃", "~")  # upside down -> tilde
            .replace("🔮", "*")  # crystal ball -> asterisk
            .replace("🌪️", "~")  # tornado -> tilde
            .replace("🤨", "?")  # raised eyebrow -> question mark
            .replace("💥", "!")  # explosion -> exclamation mark
            .replace("✅", "+")  # check mark -> plus sign
        )
        try:
            print(fallback)
        except UnicodeEncodeError:
            # Final fallback: encode with errors='replace' to handle any remaining Unicode issues
            print(fallback.encode("ascii", errors="replace").decode("ascii"))


def safe_read_file(file_path: Path) -> str:
    """Safely read a file with encoding detection and error handling"""
    try:
        # First try reading as binary to detect encoding
        with open(file_path, "rb") as f:
            raw_data = f.read()

        if not raw_data:
            safe_print(f"⚠️  '{file_path}' appears to be empty")
            return ""

        # Try encoding detection if chardet is available
        encoding = "utf-8"  # default
        if HAS_CHARDET:
            detected = chardet.detect(raw_data)
            encoding = detected.get("encoding", "utf-8")
            confidence = detected.get("confidence", 0)

            if confidence < 0.7:
                safe_print(
                    f"⚠️  Encoding detection uncertain for '{file_path}' (confidence: {confidence:.1%})"
                )
                safe_print(f"[info] Trying {encoding} encoding, but results may be wonky")

        # Try to decode with detected/default encoding
        try:
            content = raw_data.decode(encoding)
        except UnicodeDecodeError:
            # Fall back to UTF-8 with error replacement
            if encoding != "utf-8":
                safe_print(f"[?] Encoding {encoding} failed, falling back to UTF-8...")
            content = raw_data.decode("utf-8", errors="replace")

        return content

    except PermissionError:
        safe_print(f"🚫 Permission denied reading '{file_path}'")
        safe_print("[tip] Check if the file is readable or if you need different permissions")
        raise
    except OSError as e:
        safe_print(f"💥 Error reading '{file_path}': {e}")
        safe_print("[tip] File might be corrupted, in use by another program, or on a bad disk")
        raise


def validate_knda_file(file_path: Path) -> bool:
    """Validate that a .knda file can be processed"""
    try:
        # Check if it's a directory
        if file_path.is_dir():
            # For directories, validation passes - let the transformer handle it
            return True

        # For files, do content validation
        content = safe_read_file(file_path)

        # Check if file is suspiciously large
        if len(content) > 1_000_000:  # 1MB limit
            safe_print(f"😰 '{file_path}' is pretty huge ({len(content):,} chars)")
            safe_print("[tip] Large files might cause performance issues")
            safe_print("[shrug] Proceeding anyway, but don't blame me if things get slow...")

        # Check for obviously non-text content
        if "\x00" in content:
            safe_print(f"🤨 '{file_path}' contains binary data - that's not gonna work")
            safe_print("[tip] Make sure you're pointing to a text file with kinda code")
            return False

        return True

    except Exception:
        return False


def show_examples():
    """Show example kinda programs with attitude"""
    safe_print("🎲 Here are some kinda programs to get you started:")
    print()

    examples = [
        # Basic examples
        ("Hello World", "examples/python/hello.py.knda", "The classic, but fuzzy"),
        ("Chaos Greeter", "examples/python/unified_syntax.py.knda", "Variables that kinda work"),
        # Individual construct examples
        (
            "Kinda Int Demo",
            "examples/python/individual/kinda_int_example.py.knda",
            "Fuzzy integers with ±1 variance",
        ),
        (
            "Sorta Print Demo",
            "examples/python/individual/sorta_print_example.py.knda",
            "Probabilistic output (80% chance)",
        ),
        (
            "Sometimes Demo",
            "examples/python/individual/sometimes_example.py.knda",
            "50% conditional execution",
        ),
        (
            "Ish Demo",
            "examples/python/individual/ish_example.py.knda",
            "Fuzzy values and comparisons",
        ),
        (
            "Welp Fallbacks",
            "examples/python/individual/welp_example.py.knda",
            "Graceful fallbacks for risky operations",
        ),
        ("Maybe Math", "examples/python/maybe_example.py.knda", "60% conditional execution"),
        (
            "Binary Logic",
            "examples/python/kinda_binary_example.py.knda",
            "Ternary logic: yes/no/maybe",
        ),
        # Comprehensive examples
        (
            "Fuzzy Calculator",
            "examples/python/comprehensive/fuzzy_calculator.py.knda",
            "All constructs in realistic calculator",
        ),
        (
            "Chaos Arena Complete",
            "examples/python/comprehensive/chaos_arena_complete.py.knda",
            "Epic battle with all constructs",
        ),
        (
            "Fuzzy Game Quest",
            "examples/python/comprehensive/fuzzy_game_logic.py.knda",
            "Adventure game with fuzzy decisions",
        ),
        (
            "Advanced Chaos Arena",
            "examples/python/comprehensive/chaos_arena2_complete.py.knda",
            "Multi-agent simulation with ALL constructs",
        ),
    ]

    for title, filename, description in examples:
        safe_print(f"📝 {title}")
        if filename and Path(filename).exists():
            print(f"   Try: kinda run {filename}")
            print(f"   Or:  kinda interpret {filename}")
        elif description:
            print("   Example code:")
            for line in description.split("\n"):
                print(f"   {line}")
        print(f"   {description}")
        print()

    safe_print("[shrug] Pro tip: Run any example with 'interpret' for maximum chaos")


def show_syntax_reference():
    """Show syntax reference with snark"""
    safe_print("📚 Kinda Syntax Reference (your cheat sheet)")
    print()

    constructs = [
        ("~kinda int x = 42", "Fuzzy integer (adds ±1 noise)"),
        ("~kinda int y ~= 10", "Extra fuzzy assignment"),
        ("~kinda binary choice", "Three-state binary (1, -1, or 0)"),
        ("~sorta print(x)", "Maybe prints (80% chance)"),
        ("~sometimes (x > 0) { }", "Random conditional (50% chance)"),
        ("~maybe (x > 0) { }", "Less random conditional (60% chance)"),
        ("x ~= x + 1", "Fuzzy reassignment"),
    ]

    safe_print("✨ Basic Constructs:")
    for syntax, description in constructs:
        print(f"   {syntax:<25} # {description}")

    print()
    safe_print("🎯 Pro Tips:")
    print("   • Everything fuzzy starts with ~")
    print("   • Your code will behave... differently each time")
    print("   • That's the point. Embrace the chaos.")
    print("   • Use 'kinda examples' to see it in action")


def get_transformer(lang: str):
    if lang == "python":
        from kinda.langs.python import transformer

        return transformer
    elif lang == "c":
        # C support is coming in v0.4.0 - currently incomplete
        safe_print("[note] C support is coming in v0.4.0 with full compilation pipeline!")
        safe_print("[info] Currently only Python is supported. Use '--lang python' or omit --lang.")
        safe_print("[link] Follow progress at: https://github.com/kinda-lang/kinda-lang/issues/19")
        return None
    else:
        raise ValueError(f"Unsupported language: {lang}. Currently only 'python' is supported.")


def validate_chaos_level(chaos_level: int) -> int:
    """Validate and return a valid chaos level (1-10)."""
    if chaos_level < 1 or chaos_level > 10:
        available_range = "1-10"
        safe_print(f"[?] Invalid chaos level '{chaos_level}'. Valid range: {available_range}")
        safe_print("[tip] Defaulting to chaos level 5 (medium chaos)")
        return 5
    return chaos_level


def validate_seed(seed: Optional[int]) -> Optional[int]:
    """Validate and sanitize seed value for security."""
    if seed is None:
        return None

    # Basic bounds checking for security
    MAX_SEED = 2**31 - 1  # Max 32-bit signed integer
    MIN_SEED = -(2**31)  # Min 32-bit signed integer

    if seed > MAX_SEED or seed < MIN_SEED:
        safe_print(f"[?] Seed value {seed} is outside safe range ({MIN_SEED} to {MAX_SEED})")
        safe_print("[tip] Using bounded seed value for security")
        return max(MIN_SEED, min(MAX_SEED, seed))

    return seed


def setup_personality(mood: str, chaos_level: int = 5, seed: Optional[int] = None) -> None:
    """Initialize personality system with specified mood, chaos level, and seed."""
    if mood and mood.lower() not in PERSONALITY_PROFILES:
        available_moods = ", ".join(PERSONALITY_PROFILES.keys())
        safe_print(f"[?] Unknown mood '{mood}'. Available moods: {available_moods}")
        safe_print("[tip] Defaulting to 'playful' mood")
        mood = "playful"

    # Validate chaos level
    chaos_level = validate_chaos_level(chaos_level)

    # Handle seed resolution: CLI arg > environment variable > None
    resolved_seed = seed
    if resolved_seed is None:
        env_seed = os.environ.get("KINDA_SEED")
        if env_seed is not None:
            # Security: Sanitize environment variable input
            env_seed = env_seed.strip()

            # Security: Check for suspicious patterns that might indicate injection attempts
            if any(
                char in env_seed for char in ["$", "`", ";", "|", "&", "<", ">", "(", ")", "{", "}"]
            ):
                safe_print(
                    f"[!] KINDA_SEED contains suspicious characters - ignoring for security reasons"
                )
                safe_print("[tip] KINDA_SEED must contain only digits and optional minus sign")
            else:
                try:
                    # Additional security: Limit length to prevent potential DoS
                    if len(env_seed) > 20:  # Reasonable limit for integer string
                        safe_print(
                            f"[!] KINDA_SEED value too long ({len(env_seed)} chars) - ignoring for security"
                        )
                        safe_print("[tip] KINDA_SEED must be a reasonable-length integer")
                    else:
                        resolved_seed = int(env_seed)
                except ValueError:
                    safe_print(
                        f"[?] Invalid KINDA_SEED value '{env_seed}' - ignoring environment variable"
                    )
                    safe_print("[tip] KINDA_SEED must be an integer")

    # Validate and sanitize seed for security
    resolved_seed = validate_seed(resolved_seed)

    PersonalityContext.set_mood(mood or "playful")
    PersonalityContext.set_chaos_level(chaos_level)
    PersonalityContext.set_seed(resolved_seed)

    if mood:
        safe_print(f"🎭 Setting kinda mood to '{mood}'")
    safe_print(f"🎲 Setting chaos level to {chaos_level} (1=minimal, 10=maximum chaos)")
    if resolved_seed is not None:
        seed_source = "CLI" if seed is not None else "environment"
        safe_print(f"🌱 Using random seed {resolved_seed} for reproducible chaos ({seed_source})")


def detect_language(path: Path, forced: Union[str, None]) -> str:
    """
    Detect target language from file extension or --lang override.
    Currently only Python is fully supported.
    """
    if forced:
        if forced.lower() == "c":
            # Reject C explicitly with helpful message
            safe_print("[note] C transpiler is planned for v0.4.0 but not ready yet!")
            safe_print("[info] Currently only Python is supported.")
            safe_print("[tip] Tip: Remove '--lang c' to use Python (default)")
            safe_print(
                "[link] Track C support progress: https://github.com/kinda-lang/kinda-lang/issues/19"
            )
            raise ValueError("C language not yet supported")
        return forced.lower()

    name = str(path)
    if name.endswith(".py.knda") or name.endswith(".py"):
        return "python"
    elif name.endswith(".c.knda") or name.endswith(".c"):
        # C files not supported yet - reject with helpful message
        safe_print("[note] C files detected but C transpiler isn't ready yet!")
        safe_print("[info] C support is planned for v0.4.0 with full compilation pipeline")
        safe_print("[tip] For now, please use .py.knda files with Python syntax")
        safe_print("[link] Track C support: https://github.com/kinda-lang/kinda-lang/issues/19")
        raise ValueError("C files not yet supported - use .py.knda instead")

    # Default to python - it's our only complete implementation
    return "python"


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="kinda", description="A programming language for people who aren't totally sure"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_transform = sub.add_parser(
        "transform", help="Turn your kinda code into actual code (how responsible of you)"
    )
    p_transform.add_argument("input", help="Your .knda file (yes, it needs the extension)")
    p_transform.add_argument(
        "--out", default="build", help="Where to dump the results (default: build)"
    )
    p_transform.add_argument(
        "--lang", default=None, help="Target language (currently: 'python' only)"
    )
    p_transform.add_argument(
        "--mood", default=None, help="Personality/chaos level: reliable, cautious, playful, chaotic"
    )
    p_transform.add_argument(
        "--chaos-level",
        type=int,
        choices=range(1, 11),
        default=5,
        help="Control randomness intensity (1=minimal, 10=maximum chaos)",
    )
    p_transform.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible chaos (overrides KINDA_SEED environment variable)",
    )

    p_run = sub.add_parser("run", help="Transform then execute (living dangerously, I see)")
    p_run.add_argument("input", help="The .knda file you want to run")
    p_run.add_argument("--lang", default=None, help="Target language (currently: 'python' only)")
    p_run.add_argument(
        "--mood", default=None, help="Personality/chaos level: reliable, cautious, playful, chaotic"
    )
    p_run.add_argument(
        "--chaos-level",
        type=int,
        choices=range(1, 11),
        default=5,
        help="Control randomness intensity (1=minimal, 10=maximum chaos)",
    )
    p_run.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible chaos (overrides KINDA_SEED environment variable)",
    )

    p_interpret = sub.add_parser(
        "interpret", help="Run directly in fuzzy runtime (maximum chaos mode)"
    )
    p_interpret.add_argument("input", help="Your questionable life choices in .knda form")
    p_interpret.add_argument(
        "--lang", default=None, help="Target language (currently: 'python' only)"
    )
    p_interpret.add_argument(
        "--mood", default=None, help="Personality/chaos level: reliable, cautious, playful, chaotic"
    )
    p_interpret.add_argument(
        "--chaos-level",
        type=int,
        choices=range(1, 11),
        default=5,
        help="Control randomness intensity (1=minimal, 10=maximum chaos)",
    )
    p_interpret.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible chaos (overrides KINDA_SEED environment variable)",
    )

    p_examples = sub.add_parser("examples", help="Show example kinda programs (for inspiration)")

    p_syntax = sub.add_parser("syntax", help="Quick syntax reference (because you'll forget)")

    # Record/replay commands for debugging
    p_record = sub.add_parser("record", help="Record execution for debugging and replay")
    record_sub = p_record.add_subparsers(dest="record_command", required=True)

    p_record_run = record_sub.add_parser("run", help="Record program execution to session file")
    p_record_run.add_argument("input", help="The .knda file to run and record")
    p_record_run.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output session file path (default: <input>.session.json)",
    )
    p_record_run.add_argument(
        "--lang", default=None, help="Target language (currently: 'python' only)"
    )
    p_record_run.add_argument(
        "--mood", default=None, help="Personality/chaos level: reliable, cautious, playful, chaotic"
    )
    p_record_run.add_argument(
        "--chaos-level",
        type=int,
        choices=range(1, 11),
        default=5,
        help="Control randomness intensity (1=minimal, 10=maximum chaos)",
    )
    p_record_run.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible chaos (overrides KINDA_SEED environment variable)",
    )

    # Replay command for exact execution reproduction
    p_replay = sub.add_parser("replay", help="Replay recorded sessions for debugging")
    p_replay.add_argument("session", help="The session.json file to replay")
    p_replay.add_argument("program", help="The .knda file to replay (must match recorded session)")
    p_replay.add_argument("--lang", default=None, help="Target language (currently: 'python' only)")
    p_replay.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed replay progress and validation info",
    )

    # Analyze command for session inspection and debugging
    p_analyze = sub.add_parser("analyze", help="Analyze recorded sessions for debugging insights")
    p_analyze.add_argument("session", help="The session.json file to analyze")
    p_analyze.add_argument(
        "--format",
        "-f",
        choices=["summary", "detailed", "constructs", "timeline", "json"],
        default="summary",
        help="Analysis output format",
    )
    p_analyze.add_argument("--construct", "-c", help="Focus analysis on specific construct type")
    p_analyze.add_argument("--export", "-e", help="Export analysis to file (format: csv, json)")

    args = parser.parse_args(argv)

    if args.command == "transform":
        # Setup personality for transform
        setup_personality(
            getattr(args, "mood", None),
            getattr(args, "chaos_level", 5),
            getattr(args, "seed", None),
        )

        input_path = Path(args.input)
        if not input_path.exists():
            safe_print(f"[?] '{args.input}' doesn't exist. Are you sure you typed that right?")
            safe_print("[tip] Tip: Check your file path and make sure the .knda file exists")
            # Suggest similar files if possible
            parent = input_path.parent
            if parent.exists():
                similar_files = list(parent.glob("*.knda"))
                if similar_files:
                    safe_print("📂 Found these .knda files in the same directory:")
                    for f in similar_files[:3]:  # Show max 3 suggestions
                        safe_print(f"   • {f.name}")
            return 1
        # Validate file before processing
        if not validate_knda_file(input_path):
            safe_print("💥 File validation failed - cannot process this file")
            return 1

        out_dir = Path(args.out)
        try:
            lang = detect_language(input_path, args.lang)
        except ValueError as e:
            # Language not supported (like C)
            return 1

        try:
            transformer = get_transformer(lang)
        except ValueError as e:
            # Unsupported language
            safe_print(f"[shrug] Sorry, I don't speak {lang} yet. Try Python maybe?")
            return 1

        if transformer is None:
            safe_print(f"[shrug] Sorry, I don't speak {lang} yet. Try Python maybe?")
            return 1

        try:
            output_paths = transformer.transform(input_path, out_dir=out_dir)
            for path in output_paths:
                print(f"* Transformed your chaos into: {path}")
            print(f"* Generated {len(output_paths)} file(s). Hope they work!")
            return 0
        except Exception as e:
            # Handle parsing errors gracefully
            if "KindaParseError" in str(type(e)):
                safe_print(str(e).strip())
                safe_print("[tip] Fix the syntax error above and try again")
            else:
                safe_print(f"💥 Transform failed: {e}")

                # Provide snarky but helpful suggestions based on error type
                error_str = str(e).lower()
                if "encoding" in error_str or "unicode" in error_str:
                    safe_print(
                        "[?] Your file has encoding issues. Fancy characters causing trouble?"
                    )
                    safe_print("   • Save as UTF-8 (like a civilized person)")
                    safe_print("   • Those emojis might be breaking things 😅")
                elif "permission" in error_str or "access" in error_str:
                    safe_print("[shrug] Permission denied. The file system doesn't trust you:")
                    safe_print(
                        "   • Close the file if it's open elsewhere (multitasking gone wrong)"
                    )
                    safe_print("   • Check file permissions (maybe you don't own it?)")
                elif "no such file" in error_str or "not found" in error_str:
                    safe_print("[?] File not found. Did you type that path correctly?")
                    safe_print("   • Double-check the path (typos are embarrassing)")
                    safe_print("   • Make sure it ends with .knda (kinda important)")
                else:
                    safe_print("[shrug] Transform failed for mysterious reasons. Try:")
                    safe_print("   • Fix any obvious syntax errors in your .knda file")
                    safe_print("   • Remember: ~ before kinda constructs (seriously)")
                    safe_print("   • Start with something simple first")
            return 1

    if args.command == "run":
        # Setup personality for run
        setup_personality(
            getattr(args, "mood", None),
            getattr(args, "chaos_level", 5),
            getattr(args, "seed", None),
        )

        input_path = Path(args.input)
        if not input_path.exists():
            safe_print(f"[shrug]‍♂️ Can't find '{args.input}'. Did you make that up?")
            safe_print("[tip] Double-check your file path - it should end with .knda")
            # Suggest similar files
            parent = input_path.parent
            if parent.exists():
                similar_files = list(parent.glob("*.knda"))
                if similar_files:
                    safe_print("📂 Found these runnable .knda files nearby:")
                    for f in similar_files[:3]:  # Show max 3 suggestions
                        safe_print(f"   • {f.name}")
            return 1
        # Validate file before processing
        if not validate_knda_file(input_path):
            safe_print("💥 File validation failed - cannot run this file")
            return 1

        try:
            lang = detect_language(input_path, args.lang)
        except ValueError as e:
            # Language not supported (like C)
            return 1
        transformer = get_transformer(lang)
        if transformer is None:
            safe_print(f"🙄 Can't run {lang} files yet. Python works though.")
            return 1

        try:
            out_dir = Path(".kinda-build")
            out_paths = transformer.transform(input_path, out_dir=out_dir)
            if lang == "python":
                import runpy

                safe_print("🎮 Running your questionable code...")
                # Execute the transformed file
                try:
                    runpy.run_path(str(out_paths[0]), run_name="__main__")
                    safe_print("🎉 Well, that didn't crash. Success?")
                except Exception as e:
                    safe_print(f"💥 Runtime error: {e}")
                    safe_print("[?] Your code transformed fine but crashed during execution")

                    # Provide snarky but helpful suggestions based on error type
                    error_str = str(e).lower()
                    if "invalid syntax" in error_str:
                        safe_print(
                            "[shrug] Well, that's syntactically questionable. Common kinda fails:"
                        )
                        safe_print(
                            "   • Forgot the ~ tilde? maybe should be ~maybe (kinda important)"
                        )
                        safe_print("   • Mixing Python in .knda? That's... ambitious")
                        safe_print("   • Missing semicolons? Some constructs are picky like that")
                    elif "name" in error_str and "not defined" in error_str:
                        safe_print("[?] That variable doesn't exist. Awkward. Try:")
                        safe_print(
                            "   • ~kinda int x = 42 to declare fuzzy variables (the ~ matters)"
                        )
                        safe_print(
                            "   • Double-check your spelling (typos happen to the best of us)"
                        )
                    elif "module" in error_str and "not found" in error_str:
                        safe_print("[?] Python can't find that module. Oops:")
                        safe_print(
                            "   • Don't import kinda stuff in regular Python (that won't work)"
                        )
                        safe_print("   • Make sure all your dependencies are installed")
                    else:
                        safe_print("[shrug] Something's broken. The usual suspects:")
                        safe_print("   • Missing ~ before kinda constructs (very important)")
                        safe_print("   • General syntax weirdness")
                    return 1
                return 0
            safe_print(f"😅 I can transform {lang} but can't run it. Try 'transform' instead?")
            return 1
        except Exception as e:
            # Handle parsing errors gracefully
            if "KindaParseError" in str(type(e)):
                safe_print(str(e).strip())
                safe_print("[tip] Fix the syntax error above and try again")
            else:
                safe_print(f"💥 Transform failed: {e}")
                safe_print("[tip] Check your .knda file for syntax issues")
            return 1

    if args.command == "interpret":
        # Setup personality for interpret
        setup_personality(
            getattr(args, "mood", None),
            getattr(args, "chaos_level", 5),
            getattr(args, "seed", None),
        )

        input_path = Path(args.input)
        if not input_path.exists():
            safe_print(f"🙃 '{args.input}' is nowhere to be found. Try again?")
            safe_print("[tip] Make sure your .knda file exists and the path is correct")
            # Suggest similar files
            parent = input_path.parent
            if parent.exists():
                similar_files = list(parent.glob("*.knda"))
                if similar_files:
                    safe_print("📂 These .knda files are available for interpretation:")
                    for f in similar_files[:3]:  # Show max 3 suggestions
                        safe_print(f"   • {f.name}")
            return 1
        # Validate file before processing
        if not validate_knda_file(input_path):
            safe_print("💥 File validation failed - cannot interpret this file")
            return 1

        try:
            lang = detect_language(input_path, args.lang)
        except ValueError as e:
            # Language not supported (like C)
            return 1
        if lang == "python":
            from kinda.interpreter.repl import run_interpreter

            safe_print("🔮 Entering the chaos dimension...")
            run_interpreter(str(input_path), lang)
            safe_print("🌪️ Chaos complete. Reality may have shifted slightly.")
            return 0
        safe_print(f"🤨 Interpret mode only works with Python. What are you even trying to do?")
        return 1

    if args.command == "record":
        if args.record_command == "run":
            # Setup personality for record run
            setup_personality(
                getattr(args, "mood", None),
                getattr(args, "chaos_level", 5),
                getattr(args, "seed", None),
            )

            input_path = Path(args.input)
            if not input_path.exists():
                safe_print(f"[?] Can't find '{args.input}' to record. Did you spell that right?")
                safe_print("[tip] Make sure your .knda file exists and the path is correct")
                return 1

            # Validate file before processing
            if not validate_knda_file(input_path):
                safe_print("💥 File validation failed - cannot record this file")
                return 1

            # Determine output file path
            if args.output:
                output_path = Path(args.output)
            else:
                output_path = input_path.parent / f"{input_path.stem}.session.json"

            try:
                lang = detect_language(input_path, args.lang)
            except ValueError as e:
                # Language not supported (like C)
                return 1

            transformer = get_transformer(lang)
            if transformer is None:
                safe_print(f"🙄 Can't record {lang} files yet. Python works though.")
                return 1

            if lang == "python":
                from kinda.record_replay import start_recording, stop_recording
                import runpy

                try:
                    # Start recording
                    safe_print("🎥 Starting recording session...")
                    command_args = sys.argv[1:]  # Store original command for session
                    session_id = start_recording(str(input_path), command_args, output_path)
                    safe_print(f"📼 Session ID: {session_id}")

                    # Transform and execute the program
                    out_dir = Path(".kinda-build")
                    out_paths = transformer.transform(input_path, out_dir=out_dir)

                    safe_print("🎮 Running and recording your questionable code...")

                    try:
                        # Execute the transformed file while recording
                        runpy.run_path(str(out_paths[0]), run_name="__main__")
                        safe_print("🎉 Execution complete! Recording captured.")

                    except Exception as e:
                        safe_print(f"💥 Runtime error during recording: {e}")
                        safe_print("[info] Recording captured up to the point of failure")

                    finally:
                        # Always stop recording and save session
                        session = stop_recording()
                        safe_print(f"💾 Session saved to: {output_path}")
                        safe_print(
                            f"📊 Recorded {session.total_calls} RNG calls in {session.duration:.3f}s"
                        )

                        # Show summary of what was recorded
                        if session.construct_usage:
                            safe_print("🎯 Constructs recorded:")
                            for construct, count in sorted(session.construct_usage.items()):
                                safe_print(f"   • {construct}: {count} calls")

                        return 0

                except Exception as e:
                    safe_print(f"💥 Recording failed: {e}")
                    safe_print("[tip] Check that your .knda file is syntactically correct")
                    return 1
            else:
                safe_print(f"😅 Recording is only supported for Python programs currently")
                return 1

    if args.command == "replay":
        # Replay recorded session
        session_path = Path(args.session)
        program_path = Path(args.program)

        if not session_path.exists():
            safe_print(
                f"[?] Can't find session file '{args.session}'. Did you record this session?"
            )
            safe_print("[tip] Use 'kinda record run' to create a session file first")
            return 1

        if not program_path.exists():
            safe_print(f"[?] Can't find program file '{args.program}'. Did you move it?")
            safe_print("[tip] Make sure the .knda file exists and matches the recorded session")
            return 1

        # Validate file before processing
        if not validate_knda_file(program_path):
            safe_print("💥 File validation failed - cannot replay this file")
            return 1

        try:
            lang = detect_language(program_path, args.lang)
        except ValueError as e:
            # Language not supported (like C)
            return 1

        transformer = get_transformer(lang)
        if transformer is None:
            safe_print(f"🙄 Can't replay {lang} files yet. Python works though.")
            return 1

        if lang == "python":
            from kinda.record_replay import ExecutionRecorder, start_replay, stop_replay
            import runpy

            try:
                # Load the recorded session
                safe_print(f"📂 Loading session from: {session_path}")
                session = ExecutionRecorder.load_session(session_path)
                safe_print(f"🎭 Original session: {session.session_id}")
                safe_print(f"📅 Recorded: {session.start_time} ({session.total_calls} RNG calls)")

                # Verify session matches program
                if session.input_file != str(program_path):
                    safe_print(
                        f"⚠️  Session was recorded for '{session.input_file}', replaying '{program_path}'"
                    )
                    safe_print("[info] This may cause replay mismatches if files differ")

                # Start replay engine
                safe_print("🔄 Starting deterministic replay...")
                replay_session_id = start_replay(session)

                # Transform and execute the program
                out_dir = Path(".kinda-build")
                out_paths = transformer.transform(program_path, out_dir=out_dir)

                safe_print("🎮 Replaying your questionable code with recorded decisions...")

                try:
                    # Execute the transformed file with replay active
                    runpy.run_path(str(out_paths[0]), run_name="__main__")
                    safe_print("🎉 Replay complete! Execution was deterministic.")

                except Exception as e:
                    safe_print(f"💥 Runtime error during replay: {e}")
                    safe_print("[info] This may indicate a difference from the original execution")

                finally:
                    # Always stop replay and show statistics
                    replay_stats = stop_replay()
                    safe_print(f"📊 Replay Statistics:")
                    safe_print(f"   • Total calls: {replay_stats['total_calls']}")
                    safe_print(f"   • Calls replayed: {replay_stats['calls_replayed']}")
                    safe_print(f"   • Success rate: {replay_stats['success_rate']:.1f}%")

                    if replay_stats["validation_issues"] > 0:
                        safe_print(
                            f"   ⚠️  {replay_stats['validation_issues']} validation issues detected"
                        )
                        if args.verbose:
                            for i, mismatch in enumerate(
                                replay_stats["mismatches"][:5]
                            ):  # Show first 5
                                safe_print(
                                    f"      {i+1}. {mismatch['reason']} at call {mismatch['call_index']}"
                                )

                    if replay_stats["replay_complete"]:
                        safe_print("✅ Replay completed successfully - all recorded calls matched")
                    else:
                        safe_print("⚠️  Replay incomplete - execution path may have diverged")

                    return 0

            except Exception as e:
                safe_print(f"💥 Replay failed: {e}")
                safe_print(
                    "[tip] Make sure the session file is valid and the program hasn't changed"
                )
                return 1
        else:
            safe_print(f"😅 Replay is only supported for Python programs currently")
            return 1

    if args.command == "analyze":
        # Analyze recorded session
        session_path = Path(args.session)

        if not session_path.exists():
            safe_print(
                f"[?] Can't find session file '{args.session}'. Did you record this session?"
            )
            safe_print("[tip] Use 'kinda record run' to create a session file first")
            return 1

        try:
            from kinda.record_replay import ExecutionRecorder

            # Load the session
            safe_print(f"📂 Loading session from: {session_path}")
            session = ExecutionRecorder.load_session(session_path)

            # Generate analysis based on format
            if args.format == "json":
                # Output raw JSON
                import json

                session_dict = {
                    "session_id": session.session_id,
                    "input_file": session.input_file,
                    "start_time": session.start_time,
                    "duration": session.duration,
                    "total_calls": session.total_calls,
                    "construct_usage": session.construct_usage,
                    "initial_personality": session.initial_personality,
                    "rng_calls": [
                        {
                            "sequence_number": call.sequence_number,
                            "method_name": call.method_name,
                            "args": call.args,
                            "result": call.result,
                            "construct_type": call.construct_type,
                            "decision_impact": call.decision_impact,
                        }
                        for call in session.rng_calls
                    ],
                }
                print(json.dumps(session_dict, indent=2))

            elif args.format == "summary":
                # Show session summary
                safe_print(f"🎭 Session Analysis: {session.session_id}")
                safe_print(f"📁 Program: {session.input_file}")
                safe_print(
                    f"⏱️  Duration: {session.duration:.3f}s ({session.total_calls} RNG calls)"
                )
                safe_print(f"🎲 Initial Personality: {session.initial_personality}")

                if session.construct_usage:
                    safe_print("\n🎯 Construct Usage:")
                    total_calls = sum(session.construct_usage.values())
                    for construct, count in sorted(
                        session.construct_usage.items(), key=lambda x: x[1], reverse=True
                    ):
                        percentage = (count / total_calls * 100) if total_calls > 0 else 0
                        safe_print(f"   • {construct}: {count} calls ({percentage:.1f}%)")

                    # Show most impactful constructs
                    if len(session.construct_usage) > 1:
                        top_construct = max(session.construct_usage.items(), key=lambda x: x[1])
                        safe_print(
                            f"\n💫 Most Active Construct: {top_construct[0]} ({top_construct[1]} calls)"
                        )

            elif args.format == "detailed":
                # Show detailed call-by-call analysis
                safe_print(f"🔍 Detailed Session Analysis: {session.session_id}")
                safe_print(f"📁 Program: {session.input_file}")
                safe_print(f"⏱️  Duration: {session.duration:.3f}s")

                safe_print(f"\n📋 RNG Call Timeline ({session.total_calls} calls):")

                construct_filter = args.construct
                displayed_calls = 0

                for i, call in enumerate(session.rng_calls[:50]):  # Limit to first 50 calls
                    if construct_filter and call.construct_type != construct_filter:
                        continue

                    safe_print(
                        f"   {call.sequence_number:3d}. {call.method_name}({', '.join(map(str, call.args))}) → {call.result}"
                    )
                    if call.construct_type:
                        safe_print(f"        📍 {call.construct_type}: {call.decision_impact}")
                    displayed_calls += 1

                if len(session.rng_calls) > 50:
                    safe_print(f"   ... and {len(session.rng_calls) - 50} more calls")

                if construct_filter:
                    safe_print(f"\n🎯 Showing calls for construct: {construct_filter}")
                    safe_print(f"📊 {displayed_calls} matching calls found")

            elif args.format == "constructs":
                # Focus on construct analysis
                safe_print(f"🎯 Construct Analysis: {session.session_id}")
                safe_print(f"📁 Program: {session.input_file}")

                if not session.construct_usage:
                    safe_print("🤔 No construct usage detected in this session")
                    return 0

                safe_print(f"\n📊 Construct Breakdown ({session.total_calls} total calls):")

                for construct, count in sorted(
                    session.construct_usage.items(), key=lambda x: x[1], reverse=True
                ):
                    percentage = (
                        (count / session.total_calls * 100) if session.total_calls > 0 else 0
                    )
                    safe_print(f"\n🎲 {construct.upper()}: {count} calls ({percentage:.1f}%)")

                    # Find example calls for this construct
                    examples = [
                        call for call in session.rng_calls if call.construct_type == construct
                    ][:3]
                    if examples:
                        safe_print("   Examples:")
                        for example in examples:
                            safe_print(
                                f"     • {example.method_name}({', '.join(map(str, example.args))}) → {example.result}"
                            )
                            if example.decision_impact:
                                safe_print(f"       Impact: {example.decision_impact}")

            elif args.format == "timeline":
                # Show execution timeline
                safe_print(f"📈 Execution Timeline: {session.session_id}")
                safe_print(f"📁 Program: {session.input_file}")

                if not session.rng_calls:
                    safe_print("🤔 No RNG calls recorded in this session")
                    return 0

                # Group calls by construct type over time
                time_buckets = {}
                start_time = session.rng_calls[0].timestamp

                for call in session.rng_calls:
                    elapsed = call.timestamp - start_time
                    bucket = int(elapsed * 10) / 10  # 0.1s buckets
                    construct = call.construct_type or "unknown"

                    if bucket not in time_buckets:
                        time_buckets[bucket] = {}

                    time_buckets[bucket][construct] = time_buckets[bucket].get(construct, 0) + 1

                safe_print("\n⏱️  Timeline (calls per 0.1s interval):")
                for bucket in sorted(time_buckets.keys())[:20]:  # Show first 20 intervals
                    calls = time_buckets[bucket]
                    total = sum(calls.values())
                    construct_list = ", ".join(f"{k}:{v}" for k, v in sorted(calls.items()))
                    safe_print(f"   {bucket:4.1f}s: {total:2d} calls ({construct_list})")

            # Export functionality
            if args.export:
                export_path = Path(args.export)
                export_format = export_path.suffix.lower().lstrip(".")

                if export_format == "csv":
                    import csv

                    with open(export_path, "w", newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(
                            ["sequence", "method", "args", "result", "construct", "impact"]
                        )
                        for call in session.rng_calls:
                            writer.writerow(
                                [
                                    call.sequence_number,
                                    call.method_name,
                                    str(call.args),
                                    call.result,
                                    call.construct_type or "",
                                    call.decision_impact or "",
                                ]
                            )
                    safe_print(f"💾 Analysis exported to: {export_path}")

                elif export_format == "json":
                    import json

                    analysis_data = {
                        "session_metadata": {
                            "session_id": session.session_id,
                            "input_file": session.input_file,
                            "duration": session.duration,
                            "total_calls": session.total_calls,
                        },
                        "construct_usage": session.construct_usage,
                        "rng_calls": [
                            {
                                "sequence": call.sequence_number,
                                "method": call.method_name,
                                "args": call.args,
                                "result": call.result,
                                "construct": call.construct_type,
                                "impact": call.decision_impact,
                                "timestamp": call.timestamp,
                            }
                            for call in session.rng_calls
                        ],
                    }
                    with open(export_path, "w") as jsonfile:
                        json.dump(analysis_data, jsonfile, indent=2)
                    safe_print(f"💾 Analysis exported to: {export_path}")
                else:
                    safe_print(f"❌ Unsupported export format: {export_format}")
                    safe_print("[tip] Use .csv or .json file extensions")
                    return 1

            return 0

        except Exception as e:
            safe_print(f"💥 Analysis failed: {e}")
            safe_print("[tip] Make sure the session file is valid and not corrupted")
            return 1

    if args.command == "examples":
        show_examples()
        return 0

    if args.command == "syntax":
        show_syntax_reference()
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
