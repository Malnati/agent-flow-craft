import asyncio
import json
import uuid
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
from core.core.logger import get_logger, log_execution

@dataclass
class AgentConfig:
    name: str
    command: str
    env: Dict[str, str]
    working_dir: Optional[Path] = None
    timeout: int = 30
    buffer_size: int = 4096

class LocalAgentRunner:
    def __init__(self, config: AgentConfig):
        self.logger = get_logger(__name__)
        self.logger.info(f"INÍCIO - LocalAgentRunner.__init__ | Agent: {config.name}")
        
        try:
            self.config = config
            self.process = None
            self.reader = None
            self.writer = None
            self.last_heartbeat = 0
            
            # Não podemos chamar diretamente o método async, então apenas registramos a configuração
            # O setup real será feito na primeira chamada a um método
            self.initialized = False
            self.logger.info(f"SUCESSO - Agente {config.name} configurado (inicialização pendente)")
        except Exception as e:
            self.logger.error(f"FALHA - LocalAgentRunner.__init__ | Erro: {str(e)}", exc_info=True)
            raise

    async def ensure_initialized(self):
        """Garante que o processo está inicializado"""
        if not self.initialized:
            await self._setup_process()
            self.initialized = True

    @log_execution
    async def _setup_process(self):
        """Inicializa o processo do agente"""
        try:
            self.process = subprocess.Popen(
                self.config.command.split(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=self.config.env,
                cwd=self.config.working_dir,
                bufsize=self.config.buffer_size
            )
            
            # Configurar streams assíncronos
            loop = asyncio.get_event_loop()
            self.reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(self.reader)
            
            # Criar transport para stdout
            transport, _ = await loop.connect_read_pipe(
                lambda: protocol,
                self.process.stdout
            )
            
            # Criar writer para stdin
            self.writer = asyncio.StreamWriter(
                transport,
                protocol,
                self.reader,
                loop
            )
            
            # Iniciar heartbeat
            asyncio.create_task(self._heartbeat_loop())
            
            self.logger.info(f"SUCESSO - Agente {self.config.name} inicializado")
            
        except Exception as e:
            self.logger.error(f"FALHA - _setup_process | Erro: {str(e)}", exc_info=True)
            raise

    @log_execution
    async def send_command(self, command: str, payload: dict) -> dict:
        """Envia comando para o agente e aguarda resposta"""
        try:
            # Garantir que o processo está inicializado
            await self.ensure_initialized()
            
            message = {
                "message_id": str(uuid.uuid4()),
                "command": command,
                "payload": payload
            }
            
            self.logger.debug(f"Enviando comando: {command} | ID: {message['message_id']}")
            
            # Enviar mensagem
            envelope = json.dumps(message) + "\n"
            self.writer.write(envelope.encode())
            await self.writer.drain()
            
            # Aguardar resposta com timeout
            response = await asyncio.wait_for(
                self.reader.readuntil(b'\n'),
                timeout=self.config.timeout
            )
            
            result = json.loads(response.decode())
            self.logger.debug(f"Resposta recebida: {result['message_id']}")
            
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"TIMEOUT - Comando {command} excedeu {self.config.timeout}s")
            await self._handle_timeout()
            raise
        except Exception as e:
            self.logger.error(f"FALHA - send_command | Erro: {str(e)}", exc_info=True)
            raise

    async def _heartbeat_loop(self):
        """Envia heartbeats periódicos para o agente"""
        while True:
            try:
                await self.send_command("heartbeat", {})
                self.last_heartbeat = time.time()
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.error(f"FALHA - Heartbeat | Erro: {str(e)}")
                await self._handle_failure()

    @log_execution
    async def _handle_failure(self):
        """Trata falhas do agente com circuit breaker"""
        try:
            self.logger.warning(f"Reiniciando agente {self.config.name}")
            await self.stop()
            await asyncio.sleep(1)
            await self._setup_process()
        except Exception as e:
            self.logger.error(f"FALHA - _handle_failure | Erro: {str(e)}", exc_info=True)
            raise

    @log_execution
    async def stop(self):
        """Para o agente de forma limpa"""
        try:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()
            
            if self.process:
                self.process.terminate()
                await asyncio.sleep(0.5)
                if self.process.poll() is None:
                    self.process.kill()
                    
            self.logger.info(f"Agente {self.config.name} finalizado")
        except Exception as e:
            self.logger.error(f"FALHA - stop | Erro: {str(e)}", exc_info=True)
            raise
            
    async def _handle_timeout(self):
        """Gerencia timeouts de comunicação"""
        self.logger.warning(f"Timeout detectado para o agente {self.config.name}")
        # Pode implementar estratégias de retry ou circuit breaking aqui 