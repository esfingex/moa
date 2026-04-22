"""
Solaria Agent Hub — Core Dispatcher
====================================
Recibe una tarea, elige el adapter adecuado y ejecuta.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

TOOLBOX_DIR = Path(__file__).parent.parent / "toolbox"
ADAPTERS_DIR = Path(__file__).parent.parent / "adapters"
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


class Dispatcher:
    """Punto de entrada central del orquestador."""

    def __init__(self, adapter: str = "ollama"):
        self.adapter = adapter
        self._load_adapter()

    def _load_adapter(self):
        adapter_path = ADAPTERS_DIR / f"{self.adapter}.py"
        if not adapter_path.exists():
            print(f"⚠️  Adapter '{self.adapter}' no encontrado. Usando modo local.")
            self.ai_call = None
        else:
            import importlib.util
            spec = importlib.util.spec_from_file_location(self.adapter, adapter_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.ai_call = getattr(mod, "call", None)

    def run_tool(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """Ejecuta un script del toolbox localmente sin gastar tokens de IA."""
        tool_path = TOOLBOX_DIR / f"{tool_name}.py"
        if not tool_path.exists():
            return {"status": "error", "message": f"Tool '{tool_name}' no encontrado en toolbox/"}

        # Pasamos kwargs como JSON por stdin
        result = subprocess.run(
            ["python3", str(tool_path)],
            input=json.dumps(kwargs),
            capture_output=True, text=True, timeout=30
        )

        output = result.stdout.strip()
        error = result.stderr.strip()
        
        # Log
        log_entry = {"tool": tool_name, "kwargs": kwargs, "output": output, "error": error}
        log_file = LOGS_DIR / f"{tool_name}.log"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        if result.returncode != 0:
            return {"status": "error", "message": error}
        return {"status": "success", "output": output}

    def ask(self, prompt: str, context: str = "") -> str:
        """Consulta a la IA del adapter configurado."""
        if not self.ai_call:
            return "Adapter no disponible. Usa run_tool() para ejecutar scripts locales."
        return self.ai_call(prompt, context)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Solaria Agent Hub Dispatcher")
    parser.add_argument("--task", required=True, help="Nombre del tool a ejecutar")
    parser.add_argument("--adapter", default="ollama", help="Adapter de IA a usar")
    parser.add_argument("--args", default="{}", help="JSON con argumentos para el tool")
    args = parser.parse_args()

    d = Dispatcher(adapter=args.adapter)
    result = d.run_tool(args.task, **json.loads(args.args))
    print(json.dumps(result, indent=2, ensure_ascii=False))
