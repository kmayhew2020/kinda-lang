import os
from pathlib import Path
from kinda.grammar.constructs import KindaConstructs

# Create directory structure
runtime_dir = Path("kinda/runtime/python")
runtime_dir.mkdir(parents=True, exist_ok=True)

# Ensure __init__.py files exist
init_files = [
    Path("kinda/__init__.py"),
    Path("kinda/runtime/__init__.py"),
    Path("kinda/runtime/python/__init__.py"),
]
for f in init_files:
    f.touch()

# Build runtime file
lines = [
    "# Auto-generated fuzzy runtime for Python\n",
    "import random\n",
    "\n"
]

for key, meta in KindaConstructs.items():
    runtime_code = meta.get("runtime", {}).get("python")
    if runtime_code:
        lines.append(runtime_code)
        lines.append("\n")
    else:
        # Optional fallback for known types (for legacy dev/testing)
        if meta["type"] == "print":
            lines.append(
                "def sorta_print(*args):\n"
                "    if random.random() < 0.8:\n"
                "        print(*args)\n\n"
            )
        elif meta["type"] == "conditional":
            lines.append(
                "def sometimes(cond):\n"
                "    return cond and random.random() < 0.5\n\n"
            )

# Write to fuzzy.py
runtime_file = runtime_dir / "fuzzy.py"
runtime_file.write_text("".join(lines))

print(f"✅ Wrote runtime to {runtime_file}")
