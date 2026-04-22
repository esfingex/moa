"""
Model Router — Solaria Agent Hub
==================================
Detecta los modelos disponibles en Ollama y selecciona
automáticamente el mejor para cada tipo de tarea.

Optimizado para hardware con 12 GB VRAM (detectado via CanIRun.ai):
  - RUNS GREAT:  hasta ~7 GB  (~55+ tok/s)
  - RUNS WELL:   hasta ~11 GB (~22-55 tok/s)
  - AVOID:       12+ GB (saturan VRAM, se van a RAM = muy lento)

Categorías de tarea:
  code       → Corrección/generación de código Python, JS, etc.
  html       → Plantillas HTML, CSS, Alpine.js
  analysis   → Análisis de archivos, búsqueda de patrones
  reasoning  → Razonamiento complejo, planificación
  chat       → Conversación general
  embedding  → RAG, búsqueda semántica (usa nomic-embed-text)
"""
import json
import urllib.request
from pathlib import Path

OLLAMA_URL = "http://localhost:11434"
CACHE_FILE = Path(__file__).parent.parent / "logs" / "model_cache.json"

# ============================================================
# MAPA DE CAPACIDADES
# Orden: mejor → peor para cada tarea.
# Prioriza modelos que corren GREAT en 12 GB VRAM.
# ============================================================
MODEL_CAPABILITY_MAP: dict[str, list[str]] = {
    "code": [
        # RUNS GREAT en 12 GB VRAM — especializados en código
        "qwen2.5-coder",       # 7B ~4.7GB — El MEJOR open-source para código actualmente
        "deepseek-coder:6.7",  # 6.7B ~3.8GB — Muy bueno en Python/FastAPI
        "deepseek-coder",      # cualquier variante
        "codegemma",           # 7B ~5GB — Google, muy preciso
        "starcoder2",          # 7B ~4.4GB — Bueno en completación
        # RUNS WELL — modelos generales con buen código
        "phi4",                # 14B ~7.7GB — Phi-4, razonamiento + código
        "qwen3.5",             # 9B ~5.1GB — Ya instalado, bueno en código
        "llama3.1",            # 8B ~4.6GB — Ya instalado, fallback sólido
        "llama3",
        "mistral",
        "phi3.5",
        "phi3",
    ],
    "html": [
        "qwen2.5-coder",       # Entiende bien HTML/CSS/JS
        "deepseek-coder",
        "codegemma",
        "qwen3.5",
        "llama3.1",
        "llama3",
        "phi3.5",
        "mistral",
    ],
    "analysis": [
        # Para análisis de código y proyectos: priorizar contexto largo
        "qwen3.5",             # 9B — Muy bueno en comprensión y análisis
        "llama3.1",            # 8B — 128K contexto, ideal para leer archivos grandes
        "phi4",                # 14B — DECENT pero excelente razonamiento
        "llama3",
        "mistral",
        "qwen2.5-coder",       # También analiza bien código
        "phi3.5",
    ],
    "reasoning": [
        # phi4-mini-reasoning está optimizado para razonamiento lógico
        "phi4-mini-reasoning", # Ya instalado — optimizado para razonamiento
        "phi4",                # 14B — DECENT en tu hardware
        "qwen3.5",             # Buen razonamiento multi-step
        "llama3.1",
        "mistral",
        "phi3.5",
    ],
    "chat": [
        "llama3.1",            # ~55 tok/s — rápido y conversacional
        "qwen3.5",             # ~49 tok/s
        "phi3.5",              # ~X tok/s — muy ligero
        "phi4-mini-reasoning",
        "mistral",
        "llama3",
    ],
    "embedding": [
        # Para RAG: usar siempre el modelo de embeddings
        "nomic-embed-text",    # Ya instalado — 274MB, perfecto para RAG
        "mxbai-embed",
        "all-minilm",
        "snowflake-arctic",
    ],
}

# Modelos a EVITAR en este hardware (>12 GB, se van a RAM)
AVOID_ON_12GB = [
    "mistral-small-3.1",  # 12.8 GB — 107% VRAM
    "gemma3:27b",         # 14.3 GB — 119% VRAM
    "qwen2.5-coder:32b",  # 16.9 GB — 141% VRAM
    "qwen3:32b",          # 16.9 GB — 141% VRAM
    "deepseek-r1:32b",    # 16.9 GB — 141% VRAM
    "llama3.3:70b",       # 36.4 GB — TOO HEAVY
    "llama4",             # 56+ GB — TOO HEAVY
]


class ModelRouter:
    """
    Detecta los modelos disponibles en Ollama y elige
    el mejor para cada tipo de tarea según el hardware real.
    """

    def __init__(self, refresh: bool = False):
        self._installed: list[str] = []
        self._load_installed(refresh)

    def _load_installed(self, refresh: bool = False):
        """Carga la lista de modelos desde Ollama (con caché de 1h)."""
        if CACHE_FILE.exists() and not refresh:
            try:
                import time
                data = json.loads(CACHE_FILE.read_text())
                age = time.time() - data.get("timestamp", 0)
                if age < 3600 and data.get("models"):  # caché de 1 hora
                    self._installed = data["models"]
                    return
            except Exception:
                pass

        self._installed = self._fetch_from_ollama()
        CACHE_FILE.parent.mkdir(exist_ok=True)
        import time
        CACHE_FILE.write_text(json.dumps({
            "models": self._installed,
            "timestamp": time.time()
        }, indent=2))

    def _fetch_from_ollama(self) -> list[str]:
        """Consulta la API de Ollama para obtener modelos instalados."""
        try:
            req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            print(f"⚠️  No se pudo conectar con Ollama: {e}")
            return []

    def installed(self) -> list[str]:
        """Retorna la lista de modelos instalados."""
        return self._installed

    def best_for(self, task_type: str) -> str | None:
        """
        Retorna el mejor modelo instalado para el tipo de tarea dado.
        Evita automáticamente modelos que saturan el hardware.
        """
        priority_list = MODEL_CAPABILITY_MAP.get(task_type, MODEL_CAPABILITY_MAP["chat"])

        for preferred in priority_list:
            for installed in self._installed:
                # Saltar modelos que sobrepasan el hardware
                if any(avoid in installed.lower() for avoid in AVOID_ON_12GB):
                    continue
                # Comparación flexible por nombre base
                if preferred.lower() in installed.lower():
                    return installed

        # Fallback: primer modelo instalado que no sea de embeddings
        for m in self._installed:
            if "embed" not in m.lower():
                return m
        return None

    def report(self) -> str:
        """Genera un reporte legible de los modelos disponibles y sus roles."""
        if not self._installed:
            return "❌ Ollama no disponible o sin modelos instalados."

        lines = [f"🤖 Modelos en Ollama ({len(self._installed)}) — Hardware: 12 GB VRAM\n"]

        for task, icon in [
            ("code", "⚙️ "), ("html", "🎨"), ("analysis", "🔍"),
            ("reasoning", "🧠"), ("chat", "💬"), ("embedding", "📐"),
        ]:
            best = self.best_for(task)
            lines.append(f"  {icon} {task:12s} → {best or 'Sin modelo disponible'}")

        lines.append(f"\n📦 Instalados: {', '.join(self._installed)}")
        return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Solaria Model Router")
    parser.add_argument("--refresh", action="store_true", help="Re-detectar modelos")
    parser.add_argument("--task", default=None, help="Ver el mejor modelo para una tarea")
    args = parser.parse_args()

    router = ModelRouter(refresh=args.refresh)

    if args.task:
        best = router.best_for(args.task)
        print(f"✅ Mejor modelo para '{args.task}': {best or 'No disponible'}")
    else:
        print(router.report())
