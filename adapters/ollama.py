"""
Adapter: Ollama (Local AI)
===========================
Conecta con Ollama para inferencia 100% local y privada.
Ideal para: análisis de código, búsquedas en el proyecto, refactoring sin enviar datos a la nube.
"""
import json
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"


def call(prompt: str, context: str = "", model: str = DEFAULT_MODEL) -> str:
    """Envía un prompt a Ollama y retorna la respuesta completa."""
    payload = {
        "model": model,
        "prompt": f"{context}\n\n{prompt}" if context else prompt,
        "stream": False,
    }

    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read())
            return data.get("response", "").strip()
    except Exception as e:
        return f"Error al conectar con Ollama: {e}"


if __name__ == "__main__":
    # Test rápido
    reply = call("Explica en una línea qué hace Python.", model=DEFAULT_MODEL)
    print(f"Ollama dice: {reply}")
