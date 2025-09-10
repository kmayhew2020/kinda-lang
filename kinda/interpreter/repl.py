import importlib.util
import sys

from kinda.langs.python import transformer as transformer
from kinda.grammar.python import matchers
from kinda.grammar.python.constructs import KindaPythonConstructs as constructs
from kinda.langs.python import runtime_gen
from kinda.langs.python.transformer import transform_line
from pathlib import Path

LANG_DISPATCH = {
    "python": {
        "transformer": transformer,
        "match_line": matchers.match_python_construct,
        "constructs": constructs,
    },
    # Future: "c": {...}
}


def load_fuzzy_runtime(runtime_path: Path):
    spec = importlib.util.spec_from_file_location("fuzzy", runtime_path)
    fuzzy = importlib.util.module_from_spec(spec)
    sys.modules["fuzzy"] = fuzzy
    spec.loader.exec_module(fuzzy)
    return fuzzy


def run_interpreter(filepath, lang="python"):
    # Clean execution - no debug spam
    input_path = Path(filepath)

    # === Transform code ===
    code = transformer.transform_file(input_path)

    # === Prepare runtime ===
    runtime_path = Path("kinda/langs/python/runtime")
    runtime_gen.generate_runtime(runtime_path)
    helper_imports = runtime_gen.generate_runtime_helpers(
        transformer.used_helpers,
        runtime_path,
        constructs,
    )

    fuzzy = load_fuzzy_runtime(runtime_path / "fuzzy.py")

    # Ensure fuzzy module has env attribute
    if not hasattr(fuzzy, "env"):
        fuzzy.env = {}

    exec(helper_imports, {}, fuzzy.env)

    try:
        exec(code, fuzzy.env, fuzzy.env)
    except Exception as e:
        print(f"💥 Well, that went sideways: {e}")
        print(f"[shrug] Your code was... creative. Maybe too creative.")
