import re
import random

env = {}

def evaluate(expr):
    try:
        return eval(expr, {}, env)
    except:
        return None

def assign(var, expr):
    value = evaluate(expr)
    if value is not None:
        # Fuzzy nudge: add small random noise to int/float
        if isinstance(value, (int, float)):
            value += random.choice([-1, 0, 1])
        env[var] = value
        print(f"[assign] {var} ~= {value}")
    else:
        print(f"[assign] {var} skipped (evaluation failed)")

def process_line(line):
    line = line.strip()

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

def run_kinda_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("sometimes"):
            cond_match = re.match(r'sometimes\s*\((.+)\)\s*{', line)
            if cond_match:
                condition = cond_match.group(1)
                block = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("}"):
                    block.append(lines[i])
                    i += 1

                if random.random() < 0.7:  # 70% chance to run block
                    if evaluate(condition):
                        for bline in block:
                            process_line(bline)
                    else:
                        print("[sometimes] condition false")
                else:
                    print("[sometimes] skipped randomly")
        else:
            process_line(line)

        i += 1

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python interpreter.py <filename.knda>")
    else:
        run_kinda_file(sys.argv[1])
