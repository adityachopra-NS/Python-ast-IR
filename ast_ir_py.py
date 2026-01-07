import json
import os

# ENTRY


def ast_to_ir(ast):
    """
    Convert Python AST JSON OR JS Esprima AST JSON into common IR
    """
    root_type = ast.get("type") or ast.get("_type")

    if root_type in ("Program", "Module"):
        return {
            "type": "Program",
            "functions": extract_functions(ast)
        }

    raise ValueError("Unsupported AST root type")


# FUNCTION & METHOD EXTRACTION


def extract_functions(ast):
    functions = []

    for node in ast.get("body", []):
        ntype = node.get("type") or node.get("_type")

        # ---------- Top-level functions ----------
        if ntype in ("FunctionDeclaration", "FunctionDef"):
            functions.append(build_function_ir(node))

        # ---------- Classes (Python + JS) ----------
        if ntype in ("ClassDef", "ClassDeclaration"):
            for member in node.get("body", []):
                mtype = member.get("type") or member.get("_type")
                if mtype in ("FunctionDef", "MethodDefinition"):
                    functions.append(build_function_ir(member))

    return functions


# FUNCTION IR


def build_function_ir(node):
    return {
        "name": (
            node.get("id", {}).get("name") or
            node.get("name") or
            "<anonymous>"
        ),
        "body": extract_block(
            node.get("body") if isinstance(node.get("body"), dict)
            else node.get("body", [])
        )
    }



# BLOCK HANDLING


def extract_block(node):
    statements = []

    body = node.get("body") if isinstance(node, dict) else node

    for stmt in body:
        ir_stmt = convert_statement(stmt)
        if ir_stmt:
            statements.append(ir_stmt)

    return {
        "type": "Block",
        "statements": statements
    }



# STATEMENT CONVERSION (SEMANTIC)


def convert_statement(node):
    ntype = node.get("type") or node.get("_type")

    # ---------- RETURN ----------
    if ntype in ("ReturnStatement", "Return"):
        return {
            "type": "Return",
            "line": extract_line(node)
        }

    # ---------- ASSIGN ----------
    if ntype in ("VariableDeclaration", "Assign"):
        return {
            "type": "Assign",
            "line": extract_line(node)
        }

    # ---------- IF ----------
    if ntype in ("IfStatement", "If"):
        return {
            "type": "If",
            "then": extract_block(
                node.get("consequent") or node.get("body")
            ),
            "else": extract_block(node.get("alternate"))
                    if node.get("alternate") else None
        }

    # ---------- LOOPS ----------
    if ntype in ("ForStatement", "WhileStatement", "For", "While"):
        return {
            "type": "Loop",
            "body": extract_block(node.get("body"))
        }

    # ---------- SWITCH (JS) ----------
    if ntype == "SwitchStatement":
        return {
            "type": "Switch",
            "cases": [
                extract_block(case.get("consequent", []))
                for case in node.get("cases", [])
            ]
        }

    # ---------- EXPRESSIONS ----------
    if ntype.endswith("Statement") or ntype == "Expr":
        return {
            "type": "Expr",
            "line": extract_line(node)
        }

    return None



# LINE EXTRACTION


def extract_line(node):
    if "loc" in node:
        return node["loc"]["start"]["line"]
    return node.get("lineno")



# FILE DRIVER


def convert_ast_file_to_ir(ast_json_path, ir_out_path):
    with open(ast_json_path, "r") as f:
        ast = json.load(f)

    ir = ast_to_ir(ast)

    with open(ir_out_path, "w") as f:
        json.dump(ir, f, indent=2)

    print(f"IR written → {ir_out_path}")



# CLI


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python ast_to_ir.py <input.ast.json> <output.ir.json>")
        sys.exit(1)

    convert_ast_file_to_ir(sys.argv[1], sys.argv[2])
