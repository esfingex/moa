"""
MOA DIAGNOSTIC TOOL v1.1
========================
Este script audita la salud del entorno MOA para asegurar la operabilidad 
de los agentes y la conexión con el backend de Ollama.

Diseñado para ser parseado por IAs: Output estructurado y verboso.
"""

import sys
import json
from pathlib import Path

def check_env():
    """
    Realiza una auditoría de 4 puntos: Python, FileSystem, Ollama y Deps.
    Retorna un reporte que puede ser consumido por otros agentes MOA.
    """
    report = {
        "status": "INIT",
        "checks": {}
    }
    
    print("🧬 MOA SYSTEM AUDIT STARTING...")
    
    # 1. Python Check
    report["checks"]["python"] = sys.version.split()[0]
    
    # 2. FileSystem Integrity
    required_dirs = ["core", "adapters", "agents/profiles", "cli", "config", "logs"]
    report["checks"]["filesystem"] = {d: Path(d).exists() for d in required_dirs}

    # 3. Ollama Connectivity
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as r:
            report["checks"]["ollama"] = "ONLINE"
    except Exception:
        report["checks"]["ollama"] = "OFFLINE"

    # 4. Dependency Validation
    try:
        import aiohttp
        report["checks"]["dependencies"] = {"aiohttp": "OK"}
    except ImportError:
        report["checks"]["dependencies"] = {"aiohttp": "MISSING"}

    # Final Decision
    all_ok = all([
        report["checks"]["ollama"] == "ONLINE",
        all(report["checks"]["filesystem"].values())
    ])
    report["status"] = "APPROVED" if all_ok else "REJECTED"
    
    print(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    check_env()
