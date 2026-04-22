"""
Tool: fix_awaits
=================
Busca y corrige automáticamente llamadas a funciones async sin su 'await' correspondiente.

Recibe por stdin un JSON con:
  - target_file: ruta al archivo Python a reparar
  - functions: lista de nombres de funciones async (default: ["find_view_file", "find_security_file"])

Uso desde Dispatcher:
  dispatcher.run_tool("fix_awaits", target_file="path/to/file.py")

Uso desde CLI:
  echo '{"target_file": "path/to/file.py"}' | python3 fix_awaits.py
"""
import json
import re
import sys
from pathlib import Path


def fix_awaits(target_file: str, functions: list[str] | None = None) -> dict:
    if functions is None:
        functions = ["find_view_file", "find_security_file"]

    path = Path(target_file)
    if not path.exists():
        return {"status": "error", "message": f"Archivo no encontrado: {target_file}"}

    content = path.read_text(encoding="utf-8")
    original = content
    fixed_count = 0

    for fn in functions:
        # Regex: busca la función precedida por whitespace/asignacion, sin await delante
        # Excluye definiciones (async def fn_name) y ya-awaited
        pattern = rf'(?<!\bawait\s)(?<!\bawait  )(\b)(?<!def )({re.escape(fn)}\()'
        
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            # Saltar definiciones de función
            if re.search(rf'async def {re.escape(fn)}', line):
                new_lines.append(line)
                continue
            # Si tiene la llamada sin await
            if fn + "(" in line and "await " + fn not in line:
                line = line.replace(fn + "(", "await " + fn + "(")
                fixed_count += 1
            new_lines.append(line)
        content = "\n".join(new_lines)

    if content != original:
        path.write_text(content, encoding="utf-8")
        return {"status": "success", "fixed": fixed_count, "file": str(path)}
    else:
        return {"status": "ok", "fixed": 0, "message": "No se encontraron llamadas sin await"}


if __name__ == "__main__":
    try:
        args = json.loads(sys.stdin.read() or "{}")
    except Exception:
        args = {}

    target = args.get("target_file", "")
    fns = args.get("functions", None)

    if not target:
        print(json.dumps({"status": "error", "message": "Se requiere 'target_file' en el JSON de entrada"}))
        sys.exit(1)

    result = fix_awaits(target, fns)
    print(json.dumps(result, ensure_ascii=False))
