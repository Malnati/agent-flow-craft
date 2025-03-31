#!/usr/bin/env python3
"""
Script para executar operações do ContextManager diretamente.
Permite listar, obter, criar, atualizar ou excluir contextos armazenados.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from core.core.logger import get_logger, log_execution

# Adicionar o diretório base ao path para permitir importações
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Importar o gerenciador de contexto
from apps.agent_manager.agents import ContextManager

# Configurar logger
logger = get_logger(__name__)

# Mascaramento básico de dados sensíveis para logs
try:
    from core.core.utils import mask_sensitive_data, get_env_status
    has_utils = True
except ImportError:
    has_utils = False
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
            return mask_str
        return data

@log_execution
def parse_arguments():
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos da linha de comando
    """
    parser = argparse.ArgumentParser(
        description="Executa operações do ContextManager",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "operation",
        choices=["listar", "obter", "criar", "atualizar", "excluir", "limpar"],
        help="""Operação a ser executada:
        - listar: Lista contextos (opções: --limit, --type)
        - obter: Obtém um contexto (requer: --context_id)
        - criar: Cria um contexto (requer: --data_file, opções: --type)
        - atualizar: Atualiza um contexto (requer: --context_id, --data_file, opções: --merge)
        - excluir: Exclui um contexto (requer: --context_id)
        - limpar: Remove contextos antigos (opções: --days)"""
    )
    
    parser.add_argument(
        "--context_id",
        help="ID do contexto para operações que exigem identificação específica"
    )
    
    parser.add_argument(
        "--data_file",
        help="Arquivo JSON com dados para criar ou atualizar contexto"
    )
    
    parser.add_argument(
        "--type",
        help="Tipo de contexto para filtrar (listar) ou definir (criar)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limite de contextos a listar (padrão: 10)"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Dias para considerar contextos antigos na operação 'limpar' (padrão: 7)"
    )
    
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Mesclar dados ao atualizar (ao invés de substituir completamente)"
    )
    
    parser.add_argument(
        "--output",
        help="Arquivo de saída para o resultado (opcional)"
    )
    
    parser.add_argument(
        "--context_dir",
        default="agent_context",
        help="Diretório para armazenar/acessar arquivos de contexto (padrão: agent_context)"
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
        
        # Verificar e criar diretório de contexto se necessário
        context_dir = Path(args.context_dir)
        if not context_dir.exists():
            context_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório de contexto criado: {context_dir}")
        
        # Inicializar gerenciador de contexto com diretório personalizado
        manager = ContextManager(base_dir=str(context_dir))
        
        # Executar operação solicitada
        result = None
        
        if args.operation == "listar":
            # Operação: listar contextos
            logger.info(f"Listando contextos (limite: {args.limit}, tipo: {args.type})")
            contexts = manager.list_contexts(context_type=args.type, limit=args.limit)
            
            # Exibir resultado
            print(f"\n📋 Contextos encontrados: {len(contexts)}")
            for i, ctx in enumerate(contexts):
                print(f"- ID: {ctx.get('id')}")
                print(f"  Tipo: {ctx.get('type')}")
                print(f"  Criado em: {ctx.get('created_at')}")
                if ctx.get('updated_at'):
                    print(f"  Atualizado em: {ctx.get('updated_at')}")
                print()
                
            result = contexts
            
        elif args.operation == "obter":
            # Operação: obter contexto específico
            if not args.context_id:
                logger.error("ID de contexto não fornecido para operação 'obter'")
                print("❌ Erro: É necessário fornecer --context_id para obter um contexto específico")
                return 1
                
            logger.info(f"Obtendo contexto: {args.context_id}")
            context = manager.get_context(args.context_id)
            
            if not context:
                logger.warning(f"Contexto não encontrado: {args.context_id}")
                print(f"⚠️ Contexto não encontrado: {args.context_id}")
                return 1
                
            # Exibir resultado
            print(f"\n📄 Contexto: {args.context_id}")
            print(json.dumps(context, indent=2, ensure_ascii=False))
            result = context
            
        elif args.operation == "criar":
            # Operação: criar novo contexto
            if not args.data_file:
                logger.error("Arquivo de dados não fornecido para operação 'criar'")
                print("❌ Erro: É necessário fornecer --data_file para criar um contexto")
                return 1
                
            if not os.path.isfile(args.data_file):
                logger.error(f"Arquivo de dados não encontrado: {args.data_file}")
                print(f"❌ Erro: Arquivo não encontrado: {args.data_file}")
                return 1
                
            logger.info(f"Criando contexto a partir de: {args.data_file}")
            
            # Ler arquivo de dados
            with open(args.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Criar contexto
            context_type = args.type or "default"
            context_id = manager.create_context(data, context_type=context_type)
            
            # Exibir resultado
            print(f"\n✅ Contexto criado com sucesso!")
            print(f"📝 ID: {context_id}")
            print(f"📝 Tipo: {context_type}")
            
            result = {"id": context_id, "type": context_type}
            
        elif args.operation == "atualizar":
            # Operação: atualizar contexto existente
            if not args.context_id or not args.data_file:
                logger.error("ID de contexto ou arquivo de dados não fornecido para operação 'atualizar'")
                print("❌ Erro: É necessário fornecer --context_id e --data_file para atualizar um contexto")
                return 1
                
            if not os.path.isfile(args.data_file):
                logger.error(f"Arquivo de dados não encontrado: {args.data_file}")
                print(f"❌ Erro: Arquivo não encontrado: {args.data_file}")
                return 1
                
            logger.info(f"Atualizando contexto {args.context_id} a partir de: {args.data_file}")
            
            # Ler arquivo de dados
            with open(args.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Atualizar contexto
            merge = args.merge
            success = manager.update_context(args.context_id, data, merge=merge)
            
            if not success:
                logger.warning(f"Falha ao atualizar contexto: {args.context_id}")
                print(f"❌ Erro: Não foi possível atualizar o contexto {args.context_id}")
                return 1
                
            # Exibir resultado
            print(f"\n✅ Contexto atualizado com sucesso!")
            print(f"📝 ID: {args.context_id}")
            print(f"📝 Modo: {'Mesclado' if merge else 'Substituído'}")
            
            result = {"id": args.context_id, "updated": True, "merge": merge}
            
        elif args.operation == "excluir":
            # Operação: excluir contexto
            if not args.context_id:
                logger.error("ID de contexto não fornecido para operação 'excluir'")
                print("❌ Erro: É necessário fornecer --context_id para excluir um contexto")
                return 1
                
            logger.info(f"Excluindo contexto: {args.context_id}")
            
            # Excluir contexto
            success = manager.delete_context(args.context_id)
            
            if not success:
                logger.warning(f"Falha ao excluir contexto: {args.context_id}")
                print(f"❌ Erro: Não foi possível excluir o contexto {args.context_id}")
                return 1
                
            # Exibir resultado
            print(f"\n✅ Contexto excluído com sucesso!")
            print(f"📝 ID: {args.context_id}")
            
            result = {"id": args.context_id, "deleted": True}
            
        elif args.operation == "limpar":
            # Operação: limpar contextos antigos
            days = args.days
            logger.info(f"Limpando contextos mais antigos que {days} dias")
            
            # Limpar contextos
            removed = manager.clean_old_contexts(days=days)
            
            # Exibir resultado
            print(f"\n🧹 Limpeza concluída!")
            print(f"📝 Contextos removidos: {removed}")
            
            result = {"removed_count": removed, "days": days}
        
        # Salvar resultado se solicitado
        if args.output and result:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado salvo em: {args.output}")
        
        # Retorno bem-sucedido
        return 0
        
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