import json
import os
import yaml
from openai import OpenAI
from agent_platform.core.logger import get_logger, log_execution
import logging

class PlanValidator:
    """Classe responsável por validar planos de execução usando modelos de IA mais econômicos"""
    
    def __init__(self, logger=None):
        # Usar o logger passado ou criar um novo
        self.logger = logger or get_logger(__name__)
        self.model_name = "gpt-3.5-turbo"  # Modelo mais econômico
        self.requirements_file = "configs/agents/plan_requirements.yaml"
        self.requirements = self._load_requirements()
    
    @log_execution(level=logging.DEBUG)
    def _load_requirements(self):
        try:
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Erro ao carregar requisitos: {str(e)}")
            return {}
    
    @log_execution
    def validate(self, plan_content, openai_token=None):
        """
        Valida se o plano de execução atende a todos os requisitos usando um modelo de IA
        
        Args:
            plan_content (str): Conteúdo do plano de execução
            openai_token (str): Token da API da OpenAI
            
        Returns:
            dict: Resultado da validação com status e itens ausentes
        """
        self.logger.info("Iniciando validacao do plano")
        
        if not openai_token:
            openai_token = os.environ.get("OPENAI_API_KEY")
            if not openai_token:
                self.logger.error("Token da OpenAI nao fornecido")
                return {"is_valid": False, "missing_items": ["Token da OpenAI ausente"]}
        
        try:
            client = OpenAI(api_key=openai_token)
            prompt = self._create_validation_prompt(plan_content)
            
            # Log de debug com conteúdo seguro (sem expor tokens)
            self.logger.debug(f"Enviando prompt com {len(prompt)} caracteres")
            
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
            status = "valido" if is_valid else "invalido"
            self.logger.info(f"Validacao concluida: plano {status}")
            
            # Log detalhado para debugging
            if not is_valid:
                missing = validation_result.get("missing_items", [])
                self.logger.warning(f"Plano inválido. Itens ausentes: {missing}")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Erro durante validacao: {str(e)}", exc_info=True)
            return {
                "is_valid": False,
                "missing_items": [f"Erro durante validacao: {str(e)}"]
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