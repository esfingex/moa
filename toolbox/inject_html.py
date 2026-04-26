import sys
import json
from pathlib import Path

def inject_html(file_path: str, marker: str, content: str):
    """
    Inyecta contenido HTML en un archivo buscando un marcador específico.
    Formato del marcador: <!-- MOA_INJECT:marker_name -->
    """
    p = Path(file_path)
    if not p.exists():
        return {"error": f"Archivo {file_path} no encontrado"}

    html = p.read_text(encoding="utf-8")
    search_str = f"<!-- MOA_INJECT:{marker} -->"
    
    if search_str not in html:
        return {"error": f"Marcador '{search_str}' no encontrado en el archivo"}

    # Reemplazar el marcador manteniendo el marcador para futuras inyecciones si se desea,
    # o simplemente insertar después de él.
    new_html = html.replace(search_str, f"{search_str}\n{content}")
    
    p.write_text(new_html, encoding="utf-8")
    return {"status": "success", "file": file_path, "marker": marker}

if __name__ == "__main__":
    # Lee argumentos desde STDIN como JSON (estándar de MOA Toolbox)
    try:
        data = json.load(sys.stdin)
        result = inject_html(
            data.get("target_file"),
            data.get("marker"),
            data.get("content")
        )
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
