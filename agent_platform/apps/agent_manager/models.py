from django.db import models
from django.conf import settings
import json
import os

class Agent(models.Model):
    """Modelo para armazenar informações sobre um agente"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=50, choices=[
        ('feature_creation', 'Criação de Features'),
        ('plan_validator', 'Validador de Planos'),
        ('autogen', 'AutoGen Multi-agente'),
    ])
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_session_dir(self):
        """Retorna o diretório de sessão para este agente"""
        session_dir = os.path.join(settings.AGENT_SESSION_BASE_PATH, f"agent_{self.id}")
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
        return session_dir
    
    def save_session(self, session_data):
        """Salva os dados da sessão para o agente"""
        session_dir = self.get_session_dir()
        session_file = os.path.join(session_dir, "session.json")
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        return session_file
    
    def load_session(self):
        """Carrega os dados da sessão para o agente"""
        session_dir = self.get_session_dir()
        session_file = os.path.join(session_dir, "session.json")
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                return json.load(f)
        return {} 