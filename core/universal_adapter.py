import sys
from pathlib import Path
from typing import Generator

# Asegurar que los adaptadores estén en el path
sys.path.insert(0, str(Path(__file__).parent.parent / "adapters"))
import ollama as ollama_adapter

class UniversalAdapter:
    """
    Orquestador de LLMs. Decide si una tarea se resuelve localmente (Ollama)
    o requiere potencia externa (OpenAI/Anthropic).
    """

    def __init__(self):
        try:
            from config_loader import settings
            self.settings = settings
        except ImportError:
            self.settings = None

    def call(self, prompt: str, **kwargs) -> str | Generator[str, None, None]:
        # Decisión basada en el nombre del modelo o complejidad
        model = kwargs.get("model", "")
        
        # Forzar local si el usuario lo pide o si no hay modelo especificado
        if not model:
            return ollama_adapter.call(prompt, **kwargs)

        # Detectar si es un modelo externo
        is_external = any(x in model.lower() for x in ["gpt-", "claude-", "gemini-"])
        
        if is_external:
            return self._call_external(prompt, **kwargs)
        
        return ollama_adapter.call(prompt, **kwargs)

    def _call_external(self, prompt: str, **kwargs) -> str:
        model = kwargs.get("model", "")
        provider = "OpenAI" if "gpt-" in model.lower() else "Anthropic" if "claude-" in model.lower() else "Google"
        
        # Verificar si tenemos la clave configurada
        key_found = False
        if self.settings:
            key_map = {
                "OpenAI": "openai_key",
                "Anthropic": "anthropic_key",
                "Google": "gemini_key"
            }
            key_found = bool(self.settings.external_keys.get(key_map[provider]))

        if not key_found:
            return f"⚠️ Error MOA: La API Key para {provider} no está configurada en orchestrator.conf. Redirigiendo a modelo local como medida de seguridad..."
        
        return f"🚀 MOA: Conectando con {provider} para ejecutar tarea de alta complejidad con {model}..."

# Instancia global
adapter = UniversalAdapter()
