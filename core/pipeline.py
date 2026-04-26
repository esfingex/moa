import sys
import asyncio
from pathlib import Path
import time
import re

# Asegurar que el path incluya la raíz del proyecto para imports absolutos
BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.model_router import ModelRouter
from core.config_loader import settings
from adapters import ollama

# Rutas actualizadas
AGENTS_DIR = BASE_DIR / "agents" / "profiles"
SOLARIA_CONTEXT_FILE = str(AGENTS_DIR / "context" / "solaria_base.md")
PROJECT_CORE_DIR = BASE_DIR / "project_core"
LOGS_DIR = BASE_DIR / "logs"

PIPELINES: dict[str, list[dict]] = {
    "solaria_module_specialists": [
        {"skill": "qwen25_coder", "label": "📐 MOA Arquitecto", "task": "Genera el modelo Python (models/[name].py). REGLAS: 1. Heredar de 'app.core.database.Base'. 2. Usar campos de 'app.core.database.fields'. Sigue el patrón Solaria.", "use_prev": False},
        {"skill": "qwen25_coder", "label": "🖼️ MOA Visualizador", "task": "Genera el JSON de vistas en 'config/views/[name]_views.json'. Incluye tree, form y search (HTMX).", "use_prev": True},
        {"skill": "phi4_tester", "label": "🛡️ MOA Auditor", "task": "Audita el código y JSON contra las reglas del lote. Si el código cumple con los CAMPOS EXACTOS y NO tiene One2many, DA TU APROBACIÓN.", "use_prev": True},
        {"skill": "llama31_writer", "label": "📝 MOA Escritor", "task": "Genera el '__manifest__.py' y 'menu.json'.", "use_prev": True},
    ],
    "thinker": [
        {"skill": "phi4_tester", "label": "🧠 MOA Pensador", "task": "Analiza la consulta y proporciona un razonamiento profundo.", "use_prev": False},
    ],
}

class PipelineRunner:
    def __init__(self):
        self.router = ModelRouter()
        LOGS_DIR.mkdir(exist_ok=True)

    async def run_step(self, step, full_task, context, all_rag, log_path, verbose=True):
        skill = step["skill"]
        label = step["label"]
        
        # Búsqueda de contexto extendido en el registro de agentes
        agent_registry_dir = AGENTS_DIR / "registry" / skill
        if agent_registry_dir.exists():
            for reg_file in agent_registry_dir.glob("*.md"):
                if str(reg_file) not in all_rag:
                    all_rag.append(str(reg_file))

        max_retries = 2
        current_try = 0
        full_response = []

        while current_try <= max_retries:
            generator = ollama.call(
                prompt=full_task,
                context=context,
                skill=skill,
                rag_files=all_rag,
                stream=True
            )
            
            full_response = []
            with log_path.open("a") as f:
                f.write(f"\n[MOA Agente: {label} - Intento {current_try+1}]\n")
                for chunk in generator:
                    if isinstance(chunk, str):
                        f.write(chunk)
                        full_response.append(chunk)
                        if verbose: print(chunk, end="", flush=True)
            
            full_text = "".join(full_response)
            clean_text = re.sub(r'<think>.*?</think>', '', full_text, flags=re.DOTALL).lower()
            
            prohibited = ["odoo", "django", "xml", "urlpatterns", "serializer"]
            violations = [p for p in prohibited if p in clean_text]
            
            if violations and current_try < max_retries:
                error_msg = f"⚠️ ALERTA MOA: Has usado elementos prohibidos: {violations}. Reintenta en formato Solaria Puro."
                context = f"{context}\n\n## ERROR ANTERIOR:\n{error_msg}"
                current_try += 1
                continue
            else:
                break
        
        return "".join(full_response)

    async def run(self, pipeline_name: str, rag_files: list[str] = None, task: str = ""):
        if pipeline_name not in PIPELINES:
            raise ValueError(f"Pipeline '{pipeline_name}' no existe en MOA.")

        all_rag = list(rag_files or [])
        if any(x in str(all_rag) + task for x in ["solaria", "electoral", "papernews"]):
            if SOLARIA_CONTEXT_FILE not in all_rag:
                all_rag.insert(0, SOLARIA_CONTEXT_FILE)
            
            # Inyectar código real del núcleo de Solaria para Ground Truth
            core_files = [
                PROJECT_CORE_DIR / "app" / "core" / "database" / "fields.py",
                PROJECT_CORE_DIR / "app" / "core" / "database" / "registry.py"
            ]
            for cf in core_files:
                if cf.exists() and str(cf) not in all_rag:
                    all_rag.append(str(cf))

        prev_output = ""
        log_path = LOGS_DIR / f"moa_pipeline_{int(time.time())}.log"

        print(f"🚀 Iniciando Pipeline MOA: {pipeline_name}\n")

        for step in PIPELINES[pipeline_name]:
            label = step["label"]
            print(f"[{label}] en ejecución...")
            
            context = f"## Resultado anterior:\n{prev_output}" if step.get("use_prev") and prev_output else ""
            full_task = f"TAREA PRINCIPAL:\n{task}\n\nTAREA ESPECÍFICA AGENTE:\n{step['task']}"
            
            output = await self.run_step(step, full_task, context, all_rag, log_path)
            prev_output = output

        print("\n✅ Pipeline MOA completado.")
        return prev_output
