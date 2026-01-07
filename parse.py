import ast
import json

#  Read Python source file
with open("test.py", "r") as f:
    code = f.read()


tree = ast.parse(code, filename="test.py")

#onvert AST → dict (JSON-safe)
def ast_to_dict(node):
    if isinstance(node, ast.AST):
        return {
            "_type": node.__class__.__name__,
            **{k: ast_to_dict(v) for k, v in ast.iter_fields(node)}
        }
    elif isinstance(node, list):
        return [ast_to_dict(x) for x in node]
    else:
        return node

ast_json = ast_to_dict(tree)

# 4️⃣ Save AST to file
with open("test_ast.json", "w") as f:
    json.dump(ast_json, f, indent=2)

# 5️⃣ (Optional) Human-readable dump
with open("test_ast.txt", "w") as f:
    f.write(ast.dump(tree, indent=2, include_attributes=True))

print(" AST written to test_ast.json and test_ast.txt")
