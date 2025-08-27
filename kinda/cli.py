# kinda/cli.py

import argparse
import sys
from pathlib import Path
from typing import Union

# Optional chardet import for encoding detection
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False


def safe_print(text: str) -> None:
    """Print text with Windows-safe encoding fallbacks"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback for Windows: replace problematic emojis with ASCII
        fallback = (text
                   .replace("✨", "*")  # sparkle -> asterisk
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
        )
        print(fallback)


def safe_read_file(file_path: Path) -> str:
    """Safely read a file with encoding detection and error handling"""
    try:
        # First try reading as binary to detect encoding
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        if not raw_data:
            safe_print(f"⚠️  '{file_path}' appears to be empty")
            return ""
        
        # Try encoding detection if chardet is available
        encoding = 'utf-8'  # default
        if HAS_CHARDET:
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8')
            confidence = detected.get('confidence', 0)
            
            if confidence < 0.7:
                safe_print(f"⚠️  Encoding detection uncertain for '{file_path}' (confidence: {confidence:.1%})")
                safe_print(f"[info] Trying {encoding} encoding, but results may be wonky")
        
        # Try to decode with detected/default encoding
        try:
            content = raw_data.decode(encoding)
        except UnicodeDecodeError:
            # Fall back to UTF-8 with error replacement
            if encoding != 'utf-8':
                safe_print(f"[?] Encoding {encoding} failed, falling back to UTF-8...")
            content = raw_data.decode('utf-8', errors='replace')
        
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
        if '\x00' in content:
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
        ("Kinda Int Demo", "examples/python/individual/kinda_int_example.py.knda", "Fuzzy integers with ±1 variance"),
        ("Sorta Print Demo", "examples/python/individual/sorta_print_example.py.knda", "Probabilistic output (80% chance)"),
        ("Sometimes Demo", "examples/python/individual/sometimes_example.py.knda", "50% conditional execution"),
        ("Ish Demo", "examples/python/individual/ish_example.py.knda", "Fuzzy values and comparisons"),
        ("Welp Fallbacks", "examples/python/individual/welp_example.py.knda", "Graceful fallbacks for risky operations"),
        ("Maybe Math", "examples/python/maybe_example.py.knda", "60% conditional execution"),
        ("Binary Logic", "examples/python/kinda_binary_example.py.knda", "Ternary logic: yes/no/maybe"),
        
        # Comprehensive examples
        ("Fuzzy Calculator", "examples/python/comprehensive/fuzzy_calculator.py.knda", "All constructs in realistic calculator"),
        ("Chaos Arena Complete", "examples/python/comprehensive/chaos_arena_complete.py.knda", "Epic battle with all constructs"),
        ("Fuzzy Game Quest", "examples/python/comprehensive/fuzzy_game_logic.py.knda", "Adventure game with fuzzy decisions"),
        ("Advanced Chaos Arena", "examples/python/comprehensive/chaos_arena2_complete.py.knda", "Multi-agent simulation with ALL constructs"),
    ]
    
    for title, filename, description in examples:
        safe_print(f"📝 {title}")
        if filename and Path(filename).exists():
            print(f"   Try: kinda run {filename}")
            print(f"   Or:  kinda interpret {filename}")
        elif description:
            print("   Example code:")
            for line in description.split('\n'):
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
            safe_print("[link] Track C support progress: https://github.com/kinda-lang/kinda-lang/issues/19")
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
        prog="kinda", 
        description="A programming language for people who aren't totally sure"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_transform = sub.add_parser(
        "transform", help="Turn your kinda code into actual code (how responsible of you)"
    )
    p_transform.add_argument("input", help="Your .knda file (yes, it needs the extension)")
    p_transform.add_argument(
        "--out", default="build", help="Where to dump the results (default: build)"
    )
    p_transform.add_argument("--lang", default=None, help="Target language (currently: 'python' only)")

    p_run = sub.add_parser("run", help="Transform then execute (living dangerously, I see)")
    p_run.add_argument("input", help="The .knda file you want to run")
    p_run.add_argument("--lang", default=None, help="Target language (currently: 'python' only)")

    p_interpret = sub.add_parser("interpret", help="Run directly in fuzzy runtime (maximum chaos mode)")
    p_interpret.add_argument("input", help="Your questionable life choices in .knda form")
    p_interpret.add_argument("--lang", default=None, help="Target language (currently: 'python' only)")

    p_examples = sub.add_parser("examples", help="Show example kinda programs (for inspiration)")
    
    p_syntax = sub.add_parser("syntax", help="Quick syntax reference (because you'll forget)")

    args = parser.parse_args(argv)

    if args.command == "transform":
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
                    safe_print("[?] Your file has encoding issues. Fancy characters causing trouble?")
                    safe_print("   • Save as UTF-8 (like a civilized person)")
                    safe_print("   • Those emojis might be breaking things 😅")
                elif "permission" in error_str or "access" in error_str:
                    safe_print("[shrug] Permission denied. The file system doesn't trust you:")
                    safe_print("   • Close the file if it's open elsewhere (multitasking gone wrong)")
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
                        safe_print("[shrug] Well, that's syntactically questionable. Common kinda fails:")
                        safe_print("   • Forgot the ~ tilde? maybe should be ~maybe (kinda important)")
                        safe_print("   • Mixing Python in .knda? That's... ambitious")
                        safe_print("   • Missing semicolons? Some constructs are picky like that")
                    elif "name" in error_str and "not defined" in error_str:
                        safe_print("[?] That variable doesn't exist. Awkward. Try:")
                        safe_print("   • ~kinda int x = 42 to declare fuzzy variables (the ~ matters)")
                        safe_print("   • Double-check your spelling (typos happen to the best of us)")
                    elif "module" in error_str and "not found" in error_str:
                        safe_print("[?] Python can't find that module. Oops:")
                        safe_print("   • Don't import kinda stuff in regular Python (that won't work)")
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

    if args.command == "examples":
        show_examples()
        return 0
        
    if args.command == "syntax":
        show_syntax_reference()
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())