import json
import os
import yaml
from openai import OpenAI

class PlanValidator:
    def __init__(self, logger):
        self.logger = logger
        self.model_name = "gpt-3.5-turbo"
        self.requirements_file = os.path.join("config", "plan_requirements.yaml")
        self.requirements = self._load_requirements()
    
    def _load_requirements(self):
        try:
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            return {}
    
    def validate(self, plan_content, openai_token=None):
        self.logger.info("Iniciando validacao do plano")
        
        if not openai_token:
            openai_token = os.environ.get("OPENAI_API_KEY")
            if not openai_token:
                return {"is_valid": False, "missing_items": ["Token da OpenAI ausente"]}
        
        try:
            client = OpenAI(api_key=openai_token)
            prompt = self._create_validation_prompt(plan_content)
            
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
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Erro durante validacao: {str(e)}")
            return {
                "is_valid": False,
                "missing_items": [f"Erro durante validacao: {str(e)}"]
            }
    
    def _create_validation_prompt(self, plan_content):
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
