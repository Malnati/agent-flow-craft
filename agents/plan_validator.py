import json
import os
import yaml
from openai import OpenAI

class PlanValidator:
    """Classe responsável por validar planos de execução usando modelos de IA mais econômicos"""
    
    def __init__(self, logger):
        self.logger = logger
        self.model_name = "gpt-3.5-turbo"  # Modelo mais econômico
        self.requirements_file = os.path.join("config", "plan_requirements.yaml")
        self.requirements = self._load_requirements()
    
    def _load_requirements(self):
        try:
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            # Se não conseguir carregar, usa um dicionário vazio
            return {}
    
    def validate(self, plan_content, openai_token=None):
        """
        Valida se o plano de execução atende a todos os requisitos usando um modelo de IA
        
        Args:
            plan_content (str): Conteúdo do plano de execução
            openai_token (str): Token da API da OpenAI
            
        Returns:
            dict: Resultado da validação com status e itens ausentes
        """
        self.logger.info("Iniciando validação do plano com arquivo YAML de requisitos")
        
        if not openai_token:
            openai_token = os.environ.get("OPENAI_API_KEY")
            if not openai_token:
                self.logger.error("Token da OpenAI não fornecido")
                return {"is_valid": False, "missing_items": ["Token da OpenAI ausente"]}
        
        try:
            client = OpenAI(api_key=openai_token)
            prompt = self._create_validation_prompt(plan_content)
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Você é um validador de planos de execução."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=1000
            )
            
            validation_result = json.loads(response.choices[0].message.content)
            is_valid = validation_result.get("is_valid", False)
            status = "válido" if is_valid else "inválido"
            self.logger.info(f"Validação concluída: plano {status}")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Erro durante validação: {str(e)}")
            return {
                "is_valid": False,
                "missing_items": [f"Erro durante validação: {str(e)}"]
            }
    
    def _create_validation_prompt(self, plan_content):
        """Cria o prompt para validação do plano"""
        # Extrair requisitos do YAML para o prompt
        req_items = []
        
        if self.requirements and "requisitos_entregaveis" in self.requirements:
            for req in self.requirements["requisitos_entregaveis"]:
                for key, desc in req.items():
                    if key != "obrigatorio":
                        req_items.append(f"- {key}: {desc}")
        else:
            # Fallback caso não tenha carregado o YAML
            req_items = [
                "- nome: Nome claro do entregável",
                "- descricao: Descrição detalhada",
                "- dependencias: Lista de dependências",
                "- exemplo_uso: Exemplo prático",
                "- criterios_aceitacao: Critérios mensuráveis",
                "- resolucao_problemas: Problemas e soluções",
                "- passos_implementacao: Passos detalhados"
            ]
        
        # Construir o prompt de validação
        prompt = "# Validação de Plano de Execução\n\n"
        prompt += "## Plano a ser validado:\n"
        prompt += plan_content + "\n\n"
        prompt += "## Requisitos obrigatórios:\n"
        prompt += "1. O plano deve conter uma lista clara de entregáveis\n"
        prompt += "2. Para cada entregável, o plano deve incluir:\n"
        prompt += "\n".join(req_items) + "\n\n"
        prompt += "## Instruções:\n"
        prompt += "Verifique se o plano atende a todos os requisitos. Retorne sua análise no formato JSON:\n"
        prompt += '{\n'
        prompt += '  "is_valid": true/false,\n'
        prompt += '  "missing_items": ["item1", "item2", ...],\n'
        prompt += '  "entregaveis_encontrados": ["nome1", "nome2", ...],\n'
        prompt += '  "detalhes_por_entregavel": [\n'
        prompt += '    {\n'
        prompt += '      "nome": "nome do entregável",\n'
        prompt += '      "itens_ausentes": ["item1", "item2", ...]\n'
        prompt += '    }\n'
        prompt += '  ]\n'
        prompt += '}'
        
        return prompt
    
    def _extract_deliverables(self, plan_content):
        """
        Ext
</rewritten_file> 