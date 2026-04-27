import asyncio
import sys
from pathlib import Path

# Configurar path raíz
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.pipeline import PipelineRunner

# Patrones de Solaria (Simulados como contexto para el ejemplo, pero idealmente pasados como RAG)
SOLARIA_PATTERNS = """
- MODELS: Inherit from 'app.core.database.db.Base'.
- FIELDS: Use 'app.core.database.fields' (Char, Integer, Text, Boolean, Many2one).
- NAMING: Use '_name' and '_description' attributes.
- STRUCTURE: 
  - __manifest__.py
  - models/
  - views/
  - worker/
"""

async def recreate_module(module_name, definition):
    runner = PipelineRunner()
    
    # Definimos los archivos de RAG que contienen el "Ground Truth" de Solaria
    rag_files = [
        str(BASE_DIR / "project_core/app/core/database/fields.py"),
        str(BASE_DIR / "project_core/app/core/database/mixins.py"),
    ]
    
    print(f"\n🏗️  CREANDO MÓDULO: {module_name}")
    print(f"TASK: {definition}")
    
    # Tarea para el Pipeline
    task = f"""
    Crea la estructura de un módulo de Solaria llamado '{module_name}'.
    DEFINICIÓN: {definition}
    REGLAS:
    - Seguir el patrón Solaria Puro.
    - Generar el contenido de __manifest__.py, models/{module_name}.py y worker/scraper.py (si aplica).
    - Usar moa-master como orquestador.
    """
    
    # Ejecutamos un pipeline de arquitectura genérico usando moa-master
    # Nota: Forzamos el uso de moa-master en el skill
    result = await runner.run("software_architect", rag_files=rag_files, task=task)
    
    # En un entorno real, aquí escribiríamos los archivos resultantes al disco
    # Para esta tarea, simularemos la creación de la estructura base
    target_dir = Path("/home/esfingex/workspace/solaria_modules") / module_name
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "models").mkdir(exist_ok=True)
    (target_dir / "worker").mkdir(exist_ok=True)
    
    # Guardamos el resultado del arquitecto como el blueprint del módulo
    (target_dir / "blueprint.md").write_text(result, encoding="utf-8")
    print(f"✅ Blueprint de '{module_name}' generado en {target_dir}")

async def main():
    print("🔥 MOA REGENERATION: Solaria Modules\n")
    
    # 1. PAPERNEWS
    await recreate_module("papernews", "Scraper de noticias con resúmenes automáticos usando LLM local.")
    
    # 2. ELECTORAL ROLL
    await recreate_module("electoral_roll", "Gestión de padrón electoral, validación de RUT y búsqueda de datos de identidad.")

if __name__ == "__main__":
    asyncio.run(main())
