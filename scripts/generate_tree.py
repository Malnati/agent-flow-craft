from rich.console import Console
from rich.tree import Tree
import os

def build_tree(directory: str, tree: Tree):
    for entry in sorted(os.listdir(directory)):
        path = os.path.join(directory, entry)
        if os.path.isdir(path) and entry not in [".git", "__pycache__", "node_modules", ".github"]:
            branch = tree.add(f"📁 {entry}")
            build_tree(path, branch)
        elif os.path.isfile(path):
            tree.add(f"📄 {entry}")

def main():
    console = Console(record=True)
    root_tree = Tree("📦 [bold blue]agent-flow-craft[/bold blue]")
    build_tree(".", root_tree)

    output_file = "TREE.md"
    with open(output_file, "w") as f:
        f.write("# 📂 Estrutura do Projeto\n\n")
        f.write("```\n")
        f.write(console.export_text(root_tree))
        f.write("\n```\n")

    print(f"TREE.md atualizado com sucesso.")

if __name__ == "__main__":
    main()
