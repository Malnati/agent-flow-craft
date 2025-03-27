import os
import tempfile
import shutil

def generate_index():
    """Gera o índice de documentação baseado nos arquivos em docs/pr."""
    pr_dir = os.path.join("docs", "pr")
    readme_path = os.path.join("docs", "README.md")
    
    # Verifica se o diretório existe
    if not os.path.exists(pr_dir):
        os.makedirs(pr_dir)
        print(f"Diretório {pr_dir} criado.")

    # Lista e ordena os arquivos
    pr_files = []
    if os.path.exists(pr_dir):
        pr_files = sorted([f for f in os.listdir(pr_dir) if f.endswith(".md")])

    # Gera as linhas do índice
    index_lines = []
    for file in pr_files:
        name = file.replace("_", " ").replace(".md", "").capitalize()
        index_lines.append(f"- [{name}](pr/{file})")

    # Se não houver arquivos, adiciona uma mensagem
    if not index_lines:
        index_lines.append("- *Nenhum plano de execução disponível no momento.*")

    return "\n".join(index_lines)

def update_readme():
    """Atualiza o README.md com o novo índice."""
    readme_path = os.path.join("docs", "README.md")
    marker = "<!-- A lista abaixo será gerada automaticamente -->"
    
    try:
        # Lê o conteúdo atual
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Divide no marcador
        if marker in content:
            pre_content = content.split(marker)[0]
            
            # Gera o novo conteúdo
            new_content = (
                f"{pre_content}\n"
                f"{marker}\n"
                f"{generate_index()}\n"
            )

            # Escreve o novo conteúdo
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print("docs/README.md atualizado com sucesso.")
            return True
        else:
            print(f"Marcador '{marker}' não encontrado em {readme_path}")
            return False
    except Exception as e:
        print(f"Erro ao atualizar README: {str(e)}")
        return False

def test_update_docs():
    """Função de teste para verificar a geração de índice em ambiente controlado."""
    print("Iniciando teste de atualização de documentos...")
    
    # Criar ambiente de teste
    temp_dir = tempfile.mkdtemp()
    print(f"Diretório temporário criado: {temp_dir}")
    
    try:
        # Criar estrutura de diretórios
        test_docs_dir = os.path.join(temp_dir, "docs")
        test_pr_dir = os.path.join(test_docs_dir, "pr")
        os.makedirs(test_pr_dir)
        
        # Criar arquivo README de teste
        test_readme_path = os.path.join(test_docs_dir, "README.md")
        with open(test_readme_path, "w", encoding="utf-8") as f:
            f.write("# Test README\n\n### Planos de execução:\n<!-- A lista abaixo será gerada automaticamente -->\n")
        
        # Criar alguns arquivos de teste em pr/
        test_files = ["01_teste_feature.md", "02_outra_feature.md"]
        for file in test_files:
            with open(os.path.join(test_pr_dir, file), "w", encoding="utf-8") as f:
                f.write(f"# Plano de teste {file}\n\nConteúdo de teste.")
        
        # Substitui temporariamente os diretórios reais por diretórios de teste
        real_docs_dir = "docs"
        original_docs_exists = os.path.exists(real_docs_dir)
        
        if original_docs_exists:
            os.rename(real_docs_dir, f"{real_docs_dir}_backup")
        
        os.symlink(test_docs_dir, real_docs_dir)
        
        # Executa atualização
        result = update_readme()
        
        # Verifica se o arquivo foi atualizado
        if result:
            with open(test_readme_path, "r", encoding="utf-8") as f:
                updated_content = f.read()
                
            print("\nConteúdo do README atualizado:")
            print("="*40)
            print(updated_content)
            print("="*40)
            
            # Verifica se os nomes dos arquivos aparecem no conteúdo
            all_files_included = all(file.replace(".md", "") in updated_content for file in test_files)
            if all_files_included:
                print("\n✅ Teste PASSOU: Todos os arquivos foram incluídos no índice!")
            else:
                print("\n❌ Teste FALHOU: Nem todos os arquivos foram incluídos no índice.")
        else:
            print("\n❌ Teste FALHOU: Atualização do README retornou False.")
    
    finally:
        # Restaura diretórios originais
        if os.path.islink(real_docs_dir):
            os.unlink(real_docs_dir)
        
        if original_docs_exists:
            os.rename(f"{real_docs_dir}_backup", real_docs_dir)
        
        # Limpa o diretório temporário
        shutil.rmtree(temp_dir)
        print(f"Diretório temporário removido: {temp_dir}")
        print("Teste concluído.")

if __name__ == "__main__":
    test_update_docs()  # Executa o teste
    # Para produção, comente a linha acima e descomente a linha abaixo:
    # update_readme()