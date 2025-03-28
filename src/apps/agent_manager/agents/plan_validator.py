import json
import os
import yaml
from openai import OpenAI
from agent_platform.core.logger import get_logger, log_execution
import logging

# Tente importar funções de mascaramento de dados sensíveis
try:
    from agent_platform.core.utils import mask_sensitive_data, get_env_status
    has_utils = True
except ImportError:
    has_utils = False
    # Função básica de fallback para mascaramento
    def mask_sensitive_data(data, mask_str='***'):
        if isinstance(data, str) and any(s in data.lower() for s in ['token', 'key', 'secret', 'password']):
            # Mostrar parte do início e fim para debugging
            if len(data) > 10:
                return f"{data[:4]}{'*' * 12}{data[-4:] if len(data) > 8 else ''}"
            return mask_str
        return data

class PlanValidator:
    """Classe responsável por validar planos de execução usando modelos de IA mais econômicos"""
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger(__name__)
        self.logger.info("INÍCIO - PlanValidator.__init__")
        self.model_name = "gpt-3.5-turbo"
        self.requirements_file = "configs/agents/plan_requirements.yaml"
        self.requirements = self._load_requirements()
        self.logger.info("SUCESSO - PlanValidator inicializado")
    
    @log_execution(level=logging.DEBUG)
    def _load_requirements(self):
        """Carrega os requisitos do arquivo YAML"""
        self.logger.info(f"INÍCIO - _load_requirements | Arquivo: {self.requirements_file}")
        
        # Requisitos padrão caso o arquivo não exista
        default_requirements = {
            "requisitos_entregaveis": [
                {
                    "nome": "Nome do entregável",
                    "descricao": "Descrição detalhada do entregável",
                    "dependencias": "Lista de dependências necessárias",
                    "exemplo_uso": "Exemplo prático de uso",
                    "criterios_aceitacao": "Critérios mensuráveis de aceitação",
                    "resolucao_problemas": "Problemas comuns e soluções",
                    "passos_implementacao": "Passos detalhados para implementação",
                    "obrigatorio": True
                }
            ]
        }
        
        try:
            if not os.path.exists(self.requirements_file):
                self.logger.warning(f"ALERTA - _load_requirements | Arquivo não encontrado: {self.requirements_file}. Usando requisitos padrão.")
                return default_requirements
                
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                requirements = yaml.safe_load(f)
                self.logger.debug(f"Requisitos carregados: {len(requirements) if requirements else 0} itens")
                return requirements
        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            self.logger.warning(f"ALERTA - _load_requirements | Erro ao carregar requisitos: {error_msg}. Usando requisitos padrão.")
            return default_requirements
    
    @log_execution
    def validate(self, plan_content, openai_token=None):
        """Valida o plano de execução"""
        self.logger.info("INÍCIO - validate")
        
        try:
            if not openai_token:
                openai_token = os.environ.get("OPENAI_API_KEY")
                if not openai_token:
                    self.logger.error("FALHA - validate | Token OpenAI ausente")
                    return {"is_valid": False, "missing_items": ["Token da OpenAI ausente"]}
            
            # Não registrar o token OpenAI
            if has_utils:
                token_status = get_env_status("OPENAI_API_KEY") 
                self.logger.debug(f"Status do token OpenAI: {token_status}")
            else:
                self.logger.debug("Token OpenAI disponível para API")
            
            client = OpenAI(api_key=openai_token)
            prompt = self._create_validation_prompt(plan_content)
            self.logger.debug(f"Prompt gerado com {len(prompt)} caracteres")
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Voce e um validador de planos de execucao."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=1000
            )
            
            validation_result = json.loads(response.choices[0].message.content)
            is_valid = validation_result.get("is_valid", False)
            status = "válido" if is_valid else "inválido"
            
            self.logger.info(f"SUCESSO - validate | Status: plano {status}")
            if not is_valid:
                missing = validation_result.get("missing_items", [])
                # Mascarar itens ausentes para evitar exposição de dados sensíveis
                safe_missing = [mask_sensitive_data(item) for item in missing]
                self.logger.warning(f"ALERTA - Plano inválido | Itens ausentes: {safe_missing}")
            
            return validation_result
            
        except Exception as e:
            # Mascarar dados sensíveis na mensagem de erro
            error_msg = mask_sensitive_data(str(e))
            self.logger.error(f"FALHA - validate | Erro: {error_msg}", exc_info=True)
            return {
                "is_valid": False,
                "missing_items": [f"Erro durante validação: {error_msg}"]
            }
    
    def _create_validation_prompt(self, plan_content):
        """Cria o prompt para validação do plano"""
        req_items = []
        
        if self.requirements and "requisitos_entregaveis" in self.requirements:
            for req in self.requirements["requisitos_entregaveis"]:
                for key, desc in req.items():
                    if key != "obrigatorio":
                        req_items.append(f"- {key}: {desc}")
        else:
            req_items = [
                "- nome: Nome do entregavel",
                "- descricao: Descricao detalhada",
                "- dependencias: Lista de dependencias",
                "- exemplo_uso: Exemplo pratico",
                "- criterios_aceitacao: Criterios mensuraveis",
                "- resolucao_problemas: Problemas e solucoes",
                "- passos_implementacao: Passos detalhados"
            ]
        
        prompt = (
            "# Validacao de Plano\n\n"
            "## Plano a validar:\n"
            f"{plan_content}\n\n"
            "## Requisitos:\n"
            "1. Lista de entregaveis\n"
            "2. Para cada entregavel:\n"
            f"{chr(10).join(req_items)}\n\n"
            "## Retorne JSON:\n"
            '{\n'
            '  "is_valid": true/false,\n'
            '  "missing_items": ["item1", "item2"],\n'
            '  "entregaveis_encontrados": ["nome1", "nome2"],\n'
            '  "detalhes_por_entregavel": [\n'
            '    {\n'
            '      "nome": "nome do entregavel",\n'
            '      "itens_ausentes": ["item1", "item2"]\n'
            '    }\n'
            '  ]\n'
            '}'
        )
        
        return prompt
    
    def _extract_deliverables(self, plan_content):
        """
        Extrai os entregáveis do plano de execução
        
        Args:
            plan_content (str): Conteúdo do plano de execução
            
        Returns:
            list: Lista de entregáveis encontrados
        """
        # restante do código da função... 