import json
import networkx as nx
import sys


def build_cfg(ir):
    cfg = nx.DiGraph()

    for func in ir["functions"]:
        fname = func["name"]
        stmts = func["body"]["statements"]

        prev_node = None

        for i, stmt in enumerate(stmts):
            node_id = f"{fname}:{i}"
            cfg.add_node(node_id, stmt=stmt)

            if prev_node is not None:
                cfg.add_edge(prev_node, node_id)

            # Return terminates control flow
            if stmt["type"] == "Return":
                prev_node = None
                continue

            # If creates branches
            if stmt["type"] == "If":
                then_id = f"{node_id}:then"
                cfg.add_node(then_id)
                cfg.add_edge(node_id, then_id)

                if stmt["alternate"]:
                    else_id = f"{node_id}:else"
                    cfg.add_node(else_id)
                    cfg.add_edge(node_id, else_id)

            prev_node = node_id

    return cfg


def find_dead_nodes(cfg):
    entry_nodes = [n for n in cfg.nodes if ":" in n and n.endswith(":0")]
    reachable = set()

    for entry in entry_nodes:
        reachable |= nx.descendants(cfg, entry)
        reachable.add(entry)

    dead = set(cfg.nodes) - reachable
    return dead


def main(ir_path):
    with open(ir_path) as f:
        ir = json.load(f)

    cfg = build_cfg(ir)
    dead = find_dead_nodes(cfg)

    print("\nCFG NODES:")
    for n in cfg.nodes:
        print(" ", n)

    print("\nCFG EDGES:")
    for e in cfg.edges:
        print(" ", e)

    print("\nDEAD CODE NODES:")
    for d in dead:
        print(" ", d)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ir_to_cfg.py <input.ir.json>")
        sys.exit(1)

    main(sys.argv[1])
