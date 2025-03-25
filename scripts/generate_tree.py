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

# Criar o arquivo .github/workflows/auto-tag.yml com o seguinte conteúdo
with open(".github/workflows/auto-tag.yml", "w") as f:
    f.write("""name: Criar tag automática

on:
  push:
    branches:
      - main

jobs:
  tag:
    runs-on: ubuntu-latest
    steps:
      - name: Clonar o repositório
        uses: actions/checkout@v3

      - name: Configurar Git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Obter última tag
        id: get_tag
        run: |
          git fetch --tags
          TAG=$(git describe --tags `git rev-list --tags --max-count=1`)
          echo "ultima_tag=$TAG" >> $GITHUB_OUTPUT

      - name: Criar próxima tag
        id: next_tag
        run: |
          if [ -z "${{ steps.get_tag.outputs.ultima_tag }}" ]; then
            NEXT_TAG="v0.1.0"
          else
            VERSION_PARTS=($(echo "${{ steps.get_tag.outputs.ultima_tag }}" | tr "." " "))
            MAJOR=$(echo ${VERSION_PARTS[0]} | tr -d 'v')
            MINOR=${VERSION_PARTS[1]}
            PATCH=${VERSION_PARTS[2]}
            PATCH=$((PATCH + 1))
            NEXT_TAG="v$MAJOR.$MINOR.$PATCH"
          fi
          echo "next_tag=$NEXT_TAG" >> $GITHUB_OUTPUT

      - name: Criar nova tag no repositório
        run: |
          git tag ${{ steps.next_tag.outputs.next_tag }}
          git push origin ${{ steps.next_tag.outputs.next_tag }}
""")
