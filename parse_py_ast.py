import ast
import json

INPUT_FILE = "test.py"
OUTPUT_AST = "test.ast.json"


def ast_to_dict(node):
    if isinstance(node, ast.AST):
        return {
            "_type": node.__class__.__name__,
            **{k: ast_to_dict(v) for k, v in ast.iter_fields(node)},
            **({"lineno": node.lineno} if hasattr(node, "lineno") else {})
        }
    elif isinstance(node, list):
        return [ast_to_dict(x) for x in node]
    else:
        return node


with open(INPUT_FILE, "r") as f:
    code = f.read()

tree = ast.parse(code, filename=INPUT_FILE)

ast_json = ast_to_dict(tree)

with open(OUTPUT_AST, "w") as f:
    json.dump(ast_json, f, indent=2)

print(f"AST written to {OUTPUT_AST}")
