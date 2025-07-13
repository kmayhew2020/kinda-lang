import ast
import astor  # requires `pip install astor`
import sys
from pathlib import Path

# ───────────────────────────────────────────────
# 🧠 Transformer Core
# ───────────────────────────────────────────────

class KindaTransformer(ast.NodeTransformer):
    def visit_Assign(self, node):
        # Leave assignments alone for now
        return node

    def visit_Print(self, node):
        # Python 2 print stmt — not used
        return node

    def visit_Call(self, node):
        # Replace print(...) with sorta_print(...)
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            node.func.id = 'sorta_print'
        return self.generic_visit(node)

# ───────────────────────────────────────────────
# 🔄 Code Transformer
# ───────────────────────────────────────────────

def transform_file(input_path):
    input_code = Path(input_path).read_text()
    parsed_ast = ast.parse(input_code)

    transformer = KindaTransformer()
    transformed_ast = transformer.visit(parsed_ast)
    ast.fix_missing_locations(transformed_ast)

    transformed_code = astor.to_source(transformed_ast)

    # Inject the Kinda import if used
    if 'sorta_print' in transformed_code:
        header = 'from kinda.runtime.fuzzy import sorta_print\n\n'
    else:
        header = ''

    return header + transformed_code

# ───────────────────────────────────────────────
# 🚀 CLI Entry
# ───────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transformer.py <your_script.py>")
        sys.exit(1)

    input_path = sys.argv[1]
    output = transform_file(input_path)

    print("🔁 Transformed Code:\n")
    print(output)
