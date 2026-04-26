import json
import asyncio
import subprocess
from pathlib import Path
from core.model_router import ModelRouter
from adapters import ollama

BASE_DIR = Path(__file__).parent.parent
HARDWARE_PROFILE = BASE_DIR / "config" / "hardware_profile.json"

class MOAFactory:
    def __init__(self):
        self.router = ModelRouter()
        
    async def analyze_and_upgrade(self):
        """
        Aplica la lógica de CanIRun.ai para optimizar la flota de modelos.
        """
        if not HARDWARE_PROFILE.exists():
            self.router._load_or_detect_hardware()

        profile = json.loads(HARDWARE_PROFILE.read_text())
        
        # Enriquecer perfil con ancho de banda si es posible (RTX 3060 default = 360)
        profile["bandwidth_gbs"] = 360 if profile["mode"] == "GPU" else 50
        
        prompt = f"""
        EVALUAR_HARDWARE (CANIRUN_MODE):
        VRAM_TOTAL: {profile['vram_gb']}GB
        BANDWIDTH: {profile['bandwidth_gbs']}GB/s
        INSTALADOS: {self.router.available_models}
        
        TAREA: Aplica la fórmula VRAM = (B * 0.55) + 0.5 y recomienda cambios.
        """
        
        response = ollama.call(prompt, skill="moa_factory", stream=False)
        return response

    async def self_heal(self):
        """Genera perfiles .md automáticamente para modelos instalados sin configuración."""
        profiles_dir = BASE_DIR / "agents" / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)
        
        for model in self.router.available_models:
            profile_name = model.replace(":", "_").replace("-", "_").split(".")[0]
            profile_path = profiles_dir / f"{profile_name}.md"
            
            if not profile_path.exists():
                print(f"✨ Generando perfil automático para: {model}")
                content = f"""---
name: {profile_name}
model: {model}
task_type: chat
temperature: 0.1
---
ROLE: MOA_AUTO_AGENT
CONTEXT: GENERATED_PROFILE
DIRECTIVE: High-Density, technical-only response for machine-to-machine.
"""
                profile_path.write_text(content)
        return True
