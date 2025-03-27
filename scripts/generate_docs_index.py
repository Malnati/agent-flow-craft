import os
import tempfile
import shutil
import argparse

def generate_index():
    """Gera o índice de documentação baseado nos arquivos em docs/pr."""
    pr_dir = os.path.join("docs", "pr")
    
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

def update_readme(output_path=None):
    """
    Atualiza o README.md com o novo índice.
    
    Args:
        output_path (str): Caminho para o arquivo de saída. 
                          Se não especificado, usa docs/README.md
    """
    if output_path is None:
        output_path = os.path.join("docs", "README.md")
    
    marker = "<!-- A lista abaixo será gerada automaticamente -->"
    
    try:
        # Verifica se o diretório de saída existe
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Diretório {output_dir} criado.")
        
        # Lê o conteúdo atual se o arquivo existir
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            # Se o arquivo não existir, cria um conteúdo padrão
            content = "# Documentação\n\n### Planos de execução:\n" + marker + "\n"
            print(f"Arquivo {output_path} não encontrado. Criando novo arquivo.")

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
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print(f"Arquivo {output_path} atualizado com sucesso.")
            return True
        else:
            print(f"Marcador '{marker}' não encontrado em {output_path}")
            return False
    except Exception as e:
        print(f"Erro ao atualizar documento: {str(e)}")
        return False

def test_update_docs(output_path=None):
    """
    Função de teste para verificar a geração de índice em ambiente controlado.
    
    Args:
        output_path (str): Caminho para o arquivo de saída de teste
    """
    print("Iniciando teste de atualização de documentos...")
    
    # Criar ambiente de teste
    temp_dir = tempfile.mkdtemp()
    print(f"Diretório temporário criado: {temp_dir}")
    
    try:
        # Criar estrutura de diretórios
        test_docs_dir = os.path.join(temp_dir, "docs")
        test_pr_dir = os.path.join(test_docs_dir, "pr")
        os.makedirs(test_pr_dir)
        
        # Definir caminho de teste
        if output_path:
            test_output_path = os.path.join(temp_dir, output_path)
            test_output_dir = os.path.dirname(test_output_path)
            if not os.path.exists(test_output_dir):
                os.makedirs(test_output_dir)
        else:
            test_output_path = os.path.join(test_docs_dir, "README.md")
        
        # Criar arquivo README de teste
        with open(test_output_path, "w", encoding="utf-8") as f:
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
        result = update_readme(output_path)
        
        # Verifica se o arquivo foi atualizado
        if result:
            with open(test_output_path, "r", encoding="utf-8") as f:
                updated_content = f.read()
                
            print("\nConteúdo do arquivo atualizado:")
            print("="*40)
            print(updated_content)
            print("="*40)
            
            # Verifica se os nomes dos arquivos aparecem no conteúdo
            all_files_included = all(file.replace(".md", "") in updated_content for file in test_files)
            if all_files_included:
                print(f"\n✅ Teste PASSOU: Todos os arquivos foram incluídos no índice em {output_path}!")
            else:
                print(f"\n❌ Teste FALHOU: Nem todos os arquivos foram incluídos no índice em {output_path}.")
        else:
            print(f"\n❌ Teste FALHOU: Atualização do arquivo {output_path} retornou False.")
    
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

def main():
    """Função principal que processa os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(description="Atualiza o índice de documentação.")
    parser.add_argument(
        "--output", "-o", 
        type=str, 
        default=os.path.join("docs", "README.md"),
        help="Caminho para o arquivo de saída (default: docs/README.md)"
    )
    parser.add_argument(
        "--test", "-t", 
        action="store_true", 
        help="Executa o teste em vez da atualização real"
    )
    
    args = parser.parse_args()
    
    if args.test:
        test_update_docs(args.output)
    else:
        update_readme(args.output)

if __name__ == "__main__":
    main()