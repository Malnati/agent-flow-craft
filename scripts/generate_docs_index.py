import os

readme_path = "docs/README.md"

def generate_index():
    pr_files = sorted(os.listdir("docs/pr"))
    index_lines = []
    for file in pr_files:
        if file.endswith(".md"):
            name = file.replace("_", " ").replace(".md", "").capitalize()
            index_lines.append(f"- [{name}](pr/{file})")
    return "\n".join(index_lines)

with open(readme_path, "r") as f:
    content = f.read()

if "<!-- A lista abaixo será gerada automaticamente -->" in content:
    index_block = generate_index()
    updated_content = content.replace(
        "<!-- A lista abaixo será gerada automaticamente -->",
        "<!-- A lista abaixo será gerada automaticamente -->\n" + index_block
    )

    with open(readme_path, "w") as f:
        f.write(updated_content)
    print("docs/README.md atualizado com índice automático.")
else:
    print("Marcador não encontrado no docs/README.md.")