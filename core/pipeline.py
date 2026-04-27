import sys
import asyncio
from pathlib import Path
import time
import re

# Asegurar que el path incluya la raíz del proyecto
BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.model_router import ModelRouter
from core.config_loader import settings
from adapters import ollama

# Rutas Genéricas
AGENTS_DIR = BASE_DIR / "agents" / "profiles"
CACHE_DIR = BASE_DIR / "cache"
LOGS_DIR = CACHE_DIR / "logs"

# Pipelines Estándar (Ejemplos genéricos)
PIPELINES: dict[str, list[dict]] = {
    "software_architect": [
        {"skill": "moa-master", "label": "📐 MOA Master Architect", "task": "Design the system architecture based on requirements.", "use_prev": False},
        {"skill": "qwen25_coder", "label": "💻 MOA Coder", "task": "Implement the design following best practices.", "use_prev": True},
        {"skill": "tester", "label": "🛡️ MOA Tester", "task": "Audit and verify the implementation.", "use_prev": True},
    ],
    "thought_flow": [
        {"skill": "reasoner", "label": "🧠 MOA Thinker", "task": "Deep analysis of the query.", "use_prev": False},
    ],
}

class PipelineRunner:
    def __init__(self):
        self.router = ModelRouter()
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    async def run_step(self, step, full_task, context, all_rag, log_path, verbose=True):
        skill = step["skill"]
        label = step["label"]
        
        # Búsqueda de contexto en el registro de agentes
        agent_registry_dir = AGENTS_DIR / "registry" / skill
        if agent_registry_dir.exists():
            for reg_file in agent_registry_dir.glob("*.md"):
                if str(reg_file) not in all_rag:
                    all_rag.append(str(reg_file))

        max_retries = 2
        current_try = 0
        full_response = []

        while current_try <= max_retries:
            # INDICADOR DE ACTIVIDAD EN TERMINAL
            print(f"\n[EXEC] {label} (Try {current_try+1})...", end="\r", flush=True)
            
            generator = ollama.call(
                prompt=full_task,
                context=context,
                skill=skill,
                rag_files=all_rag,
                stream=True
            )
            
            full_response = []
            with log_path.open("a") as f:
                f.write(f"\n[{label} - {time.ctime()}]\n")
                for chunk in generator:
                    if isinstance(chunk, str):
                        f.write(chunk)
                        full_response.append(chunk)
                        if verbose:
                            # Stream real a la terminal para visibilidad
                            print(chunk, end="", flush=True)
            
            full_text = "".join(full_response)
            if not full_text:
                current_try += 1
                continue
                
            break
        
        return "".join(full_response)

    async def run(self, pipeline_name: str, rag_files: list[str] = None, task: str = ""):
        if pipeline_name not in PIPELINES:
            raise ValueError(f"Pipeline '{pipeline_name}' not found.")

        all_rag = list(rag_files or [])
        log_path = LOGS_DIR / f"pipeline_{int(time.time())}.log"

        print(f"\n🚀 MOA ORCHESTRATOR: Running '{pipeline_name}'")
        print(f"📂 Log: {log_path.relative_to(BASE_DIR)}")
        print("-" * 50)

        prev_output = ""
        for step in PIPELINES[pipeline_name]:
            label = step["label"]
            print(f"\n▶️  STEP: {label}")
            
            context = f"## Previous Output:\n{prev_output}" if step.get("use_prev") and prev_output else ""
            full_task = f"TASK:\n{task}\n\nAGENT INSTRUCTIONS:\n{step['task']}"
            
            output = await self.run_step(step, full_task, context, all_rag, log_path)
            prev_output = output

        print(f"\n\n✅ Pipeline '{pipeline_name}' completed.")
        return prev_output
