#!/usr/bin/env python3
"""
Script para executar o ContextManager diretamente.
Gerencia arquivos de contexto para transferência de dados entre agentes.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from agent_platform.core.logger import get_logger, log_execution

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Importar o gerenciador de contexto
from apps.agent_manager.agents import ContextManager

# Configurar logger
logger = get_logger(__name__)

@log_execution
def parse_arguments():
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos da linha de comando
    """
    parser = argparse.ArgumentParser(
        description="Executa o ContextManager para gerenciar arquivos de contexto",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "operation",
        choices=["listar", "obter", "criar", "atualizar", "excluir", "limpar"],
        help="Operação a ser executada no gerenciador de contexto"
    )
    
    parser.add_argument(
        "--context_id",
        help="ID do contexto (necessário para obter, atualizar e excluir)"
    )
    
    parser.add_argument(
        "--data_file",
        help="Arquivo JSON com dados (necessário para criar e atualizar)"
    )
    
    parser.add_argument(
        "--type",
        help="Tipo de contexto (usado para criar e filtrar contextos)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limite de contextos a serem retornados (para listar)"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Número de dias para manter contextos (para limpar)"
    )
    
    parser.add_argument(
        "--no_merge",
        action="store_true",
        help="Não mesclar dados ao atualizar (substitui completamente)"
    )
    
    parser.add_argument(
        "--base_dir",
        default="agent_context",
        help="Diretório base para arquivos de contexto"
    )
    
    parser.add_argument(
        "--output",
        help="Arquivo de saída para o resultado (opcional)"
    )
    
    return parser.parse_args()

def main():
    """
    Função principal de execução do script.
    """
    try:
        # Analisar argumentos
        args = parse_arguments()
        logger.info(f"Operação: {args.operation}")
        
        # Inicializar gerenciador de contexto
        manager = ContextManager(base_dir=args.base_dir)
        
        # Executar operação solicitada
        result = None
        
        if args.operation == "listar":
            logger.info(f"Listando contextos (limite: {args.limit}, tipo: {args.type})")
            result = manager.list_contexts(context_type=args.type, limit=args.limit)
            
            print(f"\n📋 Contextos encontrados: {len(result)}")
            for ctx in result:
                print(f"- ID: {ctx.get('id')}")
                print(f"  Tipo: {ctx.get('type')}")
                print(f"  Criado em: {ctx.get('created_at')}")
                if ctx.get('updated_at') != ctx.get('created_at'):
                    print(f"  Atualizado em: {ctx.get('updated_at')}")
                print()
            
        elif args.operation == "obter":
            if not args.context_id:
                raise ValueError("ID do contexto é obrigatório para a operação 'obter'")
                
            logger.info(f"Obtendo contexto: {args.context_id}")
            result = manager.get_context(args.context_id)
            
            if result:
                print(f"\n📋 Contexto: {args.context_id}")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"\n❌ Contexto não encontrado: {args.context_id}")
                return 1
            
        elif args.operation == "criar":
            if not args.data_file:
                raise ValueError("Arquivo de dados é obrigatório para a operação 'criar'")
                
            # Carregar dados do arquivo
            with open(args.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            logger.info(f"Criando contexto (tipo: {args.type})")
            context_id = manager.create_context(data, context_type=args.type or "default")
            
            if context_id:
                print(f"\n✅ Contexto criado com sucesso!")
                print(f"📋 ID: {context_id}")
                result = {"id": context_id}
            else:
                print("\n❌ Erro ao criar contexto")
                return 1
            
        elif args.operation == "atualizar":
            if not args.context_id:
                raise ValueError("ID do contexto é obrigatório para a operação 'atualizar'")
            if not args.data_file:
                raise ValueError("Arquivo de dados é obrigatório para a operação 'atualizar'")
                
            # Carregar dados do arquivo
            with open(args.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            merge = not args.no_merge
            logger.info(f"Atualizando contexto: {args.context_id} (merge: {merge})")
            success = manager.update_context(args.context_id, data, merge=merge)
            
            if success:
                print(f"\n✅ Contexto atualizado com sucesso!")
                print(f"📋 ID: {args.context_id}")
                result = {"id": args.context_id, "updated": True}
            else:
                print(f"\n❌ Erro ao atualizar contexto: {args.context_id}")
                return 1
            
        elif args.operation == "excluir":
            if not args.context_id:
                raise ValueError("ID do contexto é obrigatório para a operação 'excluir'")
                
            logger.info(f"Excluindo contexto: {args.context_id}")
            success = manager.delete_context(args.context_id)
            
            if success:
                print(f"\n✅ Contexto excluído com sucesso!")
                print(f"📋 ID: {args.context_id}")
                result = {"id": args.context_id, "deleted": True}
            else:
                print(f"\n❌ Erro ao excluir contexto: {args.context_id}")
                return 1
            
        elif args.operation == "limpar":
            logger.info(f"Limpando contextos mais antigos que {args.days} dias")
            removed = manager.clean_old_contexts(days=args.days)
            
            print(f"\n🧹 Limpeza concluída!")
            print(f"📋 Contextos removidos: {removed}")
            result = {"removed_count": removed}
            
        # Salvar resultado se solicitado
        if args.output and result:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado salvo em: {args.output}")
        
        # Retorno bem-sucedido
        return 0
        
    except ValueError as e:
        logger.error(f"Erro de validação: {str(e)}")
        print(f"\n❌ Erro: {str(e)}")
        return 1
        
    except KeyboardInterrupt:
        logger.warning("Processo interrompido pelo usuário")
        print("\n⚠️  Processo interrompido pelo usuário")
        return 130
        
    except Exception as e:
        logger.error(f"Erro ao executar operação: {str(e)}", exc_info=True)
        print(f"\n❌ Erro: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 