from rich.console import Console
from rich.tree import Tree
import os
import argparse

def build_tree(directory: str, tree: Tree):
    for entry in sorted(os.listdir(directory)):
        path = os.path.join(directory, entry)
        if os.path.isdir(path) and entry not in [".git", "__pycache__", "node_modules", ".github"]:
            branch = tree.add(f"📁 {entry}")
            build_tree(path, branch)
        elif os.path.isfile(path):
            tree.add(f"📄 {entry}")

def main():
    parser = argparse.ArgumentParser(description="Gera árvore de diretórios do projeto")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="TREE.md",
        help="Caminho do arquivo de saída (default: TREE.md)"
    )
    args = parser.parse_args()

    console = Console(record=True)
    root_tree = Tree("📦 [bold blue]agent-flow-craft[/bold blue]")
    build_tree(".", root_tree)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, "w") as f:
        f.write("# 📂 Estrutura do Projeto\n\n")
        f.write("```\n")
        f.write(console.export_text(root_tree))
        f.write("\n```\n")

    print(f"Arquivo {args.output} atualizado com sucesso.")

if __name__ == "__main__":
    main()
