import asyncio
import sys
from pathlib import Path

# Configurar path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.model_router import ModelRouter
from core.factory import MOAFactory
from cli.main import print_banner

# Colores
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RESET = "\033[0m"

async def check_ollama_status():
    """Verifica si Ollama está corriendo y es accesible."""
    import urllib.request
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as response:
            return response.status == 200
    except Exception:
        return False

async def run_onboarding():
    print_banner()
    print(f"{CYAN}🌟 Iniciando Protocolo de Onboarding MOA...{RESET}\n")

    # 0. VERIFICACIÓN DE PRE-REQUISITOS
    print(f"🔍 {CYAN}Verificando estado de Ollama...{RESET}")
    if not await check_ollama_status():
        print(f"❌ {YELLOW}Error: Ollama no detectado en http://localhost:11434{RESET}")
        print("Asegúrate de que Ollama esté instalado y corriendo antes de iniciar MOA.")
        return
    print(f"✅ Ollama detectado y listo.\n")

    # 1. DETECCIÓN DE HARDWARE
    router = ModelRouter()
    print(f"🖥️  {router.report()}")

    # 2. CONSULTA ESTRATÉGICA (CanIRun Logic)
    factory = MOAFactory()
    print(f"🧠 {CYAN}Consultando estrategia de modelos óptimos...{RESET}")
    recommendations = await factory.analyze_and_upgrade()
    
    print(f"\n{YELLOW}--- PROPUESTA DE CONFIGURACIÓN MOA ---{RESET}")
    print(recommendations)
    
    confirm = input(f"\n{GREEN}¿Deseas proceder con la instalación y auto-tunning? (s/n): {RESET}")
    if confirm.lower() != 's':
        print("❌ Onboarding cancelado por el usuario.")
        return

    # 3. INICIALIZACIÓN DE MEMORIA (Cavemem)
    print(f"\n🧠 {CYAN}Inicializando memoria episódica (Cavemem)...{RESET}")
    try:
        from adapters import utils
        # Intentar una consulta simple para disparar la creación de la DB
        utils.get_memories("MOA_INIT")
        print("✅ Memoria vinculada con éxito.")
    except Exception as e:
        print(f"⚠️ Nota: Cavemem se inicializará en la primera ejecución real. ({e})")

    # 4. AUTO-PROFILING & HEALING
    print(f"\n✨ {CYAN}Generando perfiles automáticos para modelos nuevos...{RESET}")
    await factory.self_heal()

    # 5. EDUCACIÓN DE IA (Verificar Documentación)

    # 4. MASTER SCULPTING (Forjar el Cerebro)
    print(f"\n🔨 {CYAN}Forjando el Modelo Maestro (moa-master)...{RESET}")
    await factory.auto_build_master()

    print(f"\n{GREEN}🎉 ¡MOA ha sido inicializado con éxito!{RESET}")
    print("Ahora puedes usar 'python3 cli/main.py run' para tus tareas.")

if __name__ == "__main__":
    asyncio.run(run_onboarding())
