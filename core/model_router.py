import json
import subprocess
import urllib.request
from pathlib import Path

OLLAMA_URL = "http://localhost:11434"
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
CACHE_DIR = BASE_DIR / "cache"
HARDWARE_PROFILE = CACHE_DIR / "hardware_profile.json"

from core.cache_manager import cache

class ModelRouter:
    def __init__(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        try:
            from core.config_loader import settings
            self.settings = settings
        except ImportError:
            self.settings = None
        self.profile = self._load_or_detect_hardware()
        self.available_models = self._get_ollama_models()

    def _load_or_detect_hardware(self):
        """Detecta el hardware o carga el perfil existente."""
        if HARDWARE_PROFILE.exists():
            return json.loads(HARDWARE_PROFILE.read_text())
        
        print("🔍 MOA: Detectando hardware por primera vez...")
        vram_gb = 0
        ram_gb = 0
        
        # 1. Detección de RAM (Linux fallback)
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemTotal' in line:
                        ram_gb = int(line.split()[1]) // (1024 * 1024)
                        break
        except Exception:
            ram_gb = 8 # Fallback genérico

        # 2. Detección de NVIDIA VRAM
        try:
            res = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"], stderr=subprocess.DEVNULL)
            vram_gb = int(res.decode().strip()) // 1024
        except Exception:
            pass

        profile = {
            "vram_gb": vram_gb,
            "ram_gb": ram_gb,
            "mode": "GPU" if vram_gb > 0 else "CPU",
            "great_threshold": (vram_gb or ram_gb) * 0.6,
            "max_threshold": (vram_gb or ram_gb) * 0.9
        }
        HARDWARE_PROFILE.write_text(json.dumps(profile, indent=2))
        return profile

    def _get_ollama_models(self):
        """Obtiene la lista de modelos instalados en Ollama."""
        try:
            with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags") as response:
                data = json.loads(response.read())
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    def best_for(self, task_type: str) -> str | None:
        """Selecciona el mejor modelo disponible según el perfil de hardware y configuración."""
        # Mapa de preferencia cargado desde configuración
        if self.settings and hasattr(self.settings, 'capability_map'):
            capability_map = self.settings.capability_map
        else:
            capability_map = {
                "code": ["qwen2.5-coder:7b", "solaria-master"],
                "reasoning": ["phi4", "solaria-master"],
                "chat": ["llama3.1:8b", "solaria-master"]
            }
        
        candidates = capability_map.get(task_type, ["llama3.1:8b"])
        
        # Filtrar por los que realmente están instalados
        installed_candidates = [c for c in candidates if any(c in m for m in self.available_models)]
        
        if installed_candidates:
            return installed_candidates[0]
        
        return self.available_models[0] if self.available_models else None

    def report(self):
        return f"""
{'-'*40}
🚀 MOA HARDWARE PROFILE:
Mode: {self.profile['mode']}
VRAM: {self.profile['vram_gb']} GB
RAM: {self.profile['ram_gb']} GB
Models Installed: {len(self.available_models)}
{'-'*40}
"""

if __name__ == "__main__":
    router = ModelRouter()
    print(router.report())
