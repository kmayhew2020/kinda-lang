import re
import random
import sys

# ───────────────────────────────────────────────
# 🧠 Environment
# ───────────────────────────────────────────────
env = {}

def evaluate(expr):
    try:
        return eval(expr, {}, env)
    except:
        return None

def assign(var, expr):
    value = evaluate(expr)
    if value is not None:
        if isinstance(value, (int, float)):
            value += random.choice([-1, 0, 1])
        env[var] = value
        print(f"[assign] {var} ~= {value}")
    else:
        print(f"[assign] {var} skipped (evaluation failed)")

# ───────────────────────────────────────────────
# 🧱 Core Features
# ───────────────────────────────────────────────

def handle_declaration(line):
    """kinda int x = 5;"""
    match = re.match(r'kinda int (\w+)\s*=\s*(.+);', line)
    if match:
        assign(*match.groups())

def handle_assignment(line):
    """x ~= 5;"""
    match = re.match(r'(\w+)\s*~=\s*(.+);', line)
    if match:
        assign(*match.groups())

def handle_sorta_print(line):
    """sorta print(...)"""
    match = re.match(r'sorta print\((.+)\);', line)
    if match and random.random() < 0.8:
        try:
            print(f"[print] {eval(match.group(1), {}, env)}")
        except:
            print(f"[print] Failed to evaluate: {match.group(1)}")

def handle_sometimes_block(lines, i):
    """sometimes (cond) { ... }"""
    cond_match = re.match(r'sometimes\s*\((.+)\)\s*{', lines[i].strip())
    if cond_match:
        condition = cond_match.group(1)
        block = []
        i += 1
        while i < len(lines) and not lines[i].strip().startswith("}"):
            block.append(lines[i])
            i += 1
        if random.random() < 0.7:
            if evaluate(condition):
                for bline in block:
                    process_line(bline.strip())
            else:
                print("[sometimes] condition false")
        else:
            print("[sometimes] skipped randomly")
    return i  # new line index

# ───────────────────────────────────────────────
# 🚧 Not Yet Implemented
# ───────────────────────────────────────────────

# TODO: def handle_maybe_block(...)
# TODO: def handle_meh_noop(...)
# TODO: def handle_returnish(...)
# TODO: def handle_whileish(...)
# TODO: def handle_orMaybe(...)
# TODO: def handle_personality(...)
# TODO: def handle_comments(...)
# TODO: def handle_believeStrongly(...)
# TODO: def handle_memory_allocators(...)
# TODO: def handle_time_calls(...)
# TODO: def transpile_to_c(...)
# TODO: def handle_pragma_directives(...)
# TODO: def cli_mood_flag(...)

# ───────────────────────────────────────────────
# 🧵 Line Dispatcher
# ───────────────────────────────────────────────

def process_line(line):
    line = line.strip()

    if not line or line.startswith("//"):
        return  # ignore blank lines and comments

    if line.startswith("kinda int"):
        match = re.match(r'kinda int (\w+)\s*=\s*(.+);', line)
        if match:
            var, expr = match.groups()
            assign(var, expr)

    elif line.startswith("sorta print"):
        match = re.match(r'sorta print\((.+)\);', line)
        if match and random.random() < 0.8:  # 80% chance to print
            args = match.group(1)
            try:
                output = eval(args, {}, env)
                print(f"[print] {output}")
            except:
                print(f"[print] Failed to evaluate: {args}")

    elif "~=" in line:
        match = re.match(r'(\w+)\s*~=\s*(.+);', line)
        if match:
            var, expr = match.groups()
            assign(var, expr)

    else:
        print(f"[warn] Unrecognized line: {line}")


def run_kinda_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("sometimes"):
            i = handle_sometimes_block(lines, i)
        else:
            process_line(line)
        i += 1

# ───────────────────────────────────────────────
# 🚀 CLI Entry
# ───────────────────────────────────────────────

if __name__ == "__main__":
    # Check for --test flag
    test_mode = False
    if "--test" in sys.argv:
        test_mode = True
        random.seed(42)  # ✅ Make randomness deterministic
        sys.argv.remove("--test")  # Clean the arg list

    if len(sys.argv) != 2:
        print("Usage: python interpreter.py [--test] <filename.knda>")
    else:
        run_kinda_file(sys.argv[1])
