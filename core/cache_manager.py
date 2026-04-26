import json
import os
from pathlib import Path
from datetime import datetime, timedelta

class CacheManager:
    """
    Gestiona el almacenamiento temporal de datos para MOA.
    Optimiza el rendimiento evitando re-ejecución de tareas idénticas.
    """
    
    def __init__(self, cache_dir: str = "cache"):
        self.base_path = Path(os.getcwd()) / cache_dir
        self.base_path.mkdir(exist_ok=True)

    def set(self, key: str, data: dict, expiry_hours: int = 24):
        """Guarda datos en el cache con una fecha de expiración."""
        file_path = self.base_path / f"{key}.json"
        payload = {
            "timestamp": datetime.now().isoformat(),
            "expiry": (datetime.now() + timedelta(hours=expiry_hours)).isoformat(),
            "data": data
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def get(self, key: str) -> dict | None:
        """Recupera datos del cache si no han expirado."""
        file_path = self.base_path / f"{key}.json"
        if not file_path.exists():
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
            
            # Verificar expiración
            expiry = datetime.fromisoformat(payload["expiry"])
            if datetime.now() > expiry:
                return None
                
            return payload["data"]
        except Exception:
            return None

    def clear(self, key: str | None = None):
        """Limpia el cache completo o una entrada específica."""
        if key:
            file_path = self.base_path / f"{key}.json"
            if file_path.exists():
                file_path.unlink()
        else:
            for f in self.base_path.glob("*.json"):
                f.unlink()

# Instancia global
cache = CacheManager()
