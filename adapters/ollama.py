"""
Adapter: Ollama (Local AI) con Skills
========================================
Conecta con Ollama. Si se especifica un skill, lo carga como system prompt
+ few-shot examples para guiar al modelo con contexto y ejemplos específicos.

Ideal para: análisis de código, búsquedas en el proyecto, refactoring sin enviar datos a la nube.
"""
import json
import urllib.request
from pathlib import Path
from typing import TYPE_CHECKING

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"
SKILLS_DIR = Path(__file__).parent.parent / "skills"


def _get_router():
    """Lazy import del router para evitar dependencias circulares."""
    from pathlib import Path
    import sys
    core_dir = str(Path(__file__).parent.parent / "core")
    if core_dir not in sys.path:
        sys.path.insert(0, core_dir)
    from model_router import ModelRouter
    return ModelRouter()


def load_skill(skill_name: str) -> tuple[str, str, str, float]:
    """
    Carga un skill desde skills/{skill_name}.md
    Retorna: (system_prompt, model, task_type, temperature)
    """
    skill_file = SKILLS_DIR / f"{skill_name}.md"
    if not skill_file.exists():
        return "", DEFAULT_MODEL, "chat", 0.7

    content = skill_file.read_text(encoding="utf-8")
    model = DEFAULT_MODEL
    temperature = 0.7
    task_type = "chat"
    system_prompt = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            body = parts[2].strip()
            for line in frontmatter.split("\n"):
                if line.startswith("model:"):
                    model = line.split(":", 1)[1].strip()
                elif line.startswith("temperature:"):
                    try:
                        temperature = float(line.split(":", 1)[1].strip())
                    except ValueError:
                        pass
                elif line.startswith("task_type:"):
                    task_type = line.split(":", 1)[1].strip()
            system_prompt = body

    return system_prompt, model, task_type, temperature


def call(
    prompt: str,
    context: str = "",
    model: str | None = None,
    skill: str | None = None,
    rag_files: list[str] | None = None,
) -> str:
    """
    Envía un prompt a Ollama con soporte de Skills y RAG.

    Args:
        prompt: La pregunta o tarea principal.
        context: Contexto adicional (texto libre).
        model: Modelo de Ollama a usar (sobrescribe el del skill).
        skill: Nombre del skill a cargar (sin extensión .md).
        rag_files: Lista de rutas de archivos a inyectar como contexto RAG.
    """
    system_prompt = ""
    skill_model = model or DEFAULT_MODEL
    temperature = 0.7
    task_type = "chat"

    # 1. Cargar skill si se especifica
    if skill:
        system_prompt, skill_model, task_type, temperature = load_skill(skill)

    # 2. Auto-seleccionar el mejor modelo disponible según la tarea
    if not model:
        try:
            router = _get_router()
            best = router.best_for(task_type)
            model = best or skill_model
        except Exception:
            model = skill_model

    # 2. RAG: inyectar contenido de archivos relevantes
    rag_context = ""
    if rag_files:
        rag_parts = []
        for fpath in rag_files:
            p = Path(fpath)
            if p.exists():
                content = p.read_text(encoding="utf-8")
                # Limitar a 3000 chars por archivo para no saturar el contexto
                if len(content) > 3000:
                    content = content[:3000] + "\n... [truncado]"
                rag_parts.append(f"### Archivo: {p.name}\n```\n{content}\n```")
        if rag_parts:
            rag_context = "\n\n## CONTEXTO DEL PROYECTO\n" + "\n\n".join(rag_parts)

    # 3. Construir prompt final
    full_prompt_parts = []
    if system_prompt:
        full_prompt_parts.append(system_prompt)
    if rag_context:
        full_prompt_parts.append(rag_context)
    if context:
        full_prompt_parts.append(f"\n## CONTEXTO ADICIONAL\n{context}")
    full_prompt_parts.append(f"\n## TAREA\n{prompt}")

    full_prompt = "\n\n".join(full_prompt_parts)

    payload = {
        "model": model or DEFAULT_MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }

    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read())
            return data.get("response", "").strip()
    except Exception as e:
        return f"Error al conectar con Ollama: {e}"


if __name__ == "__main__":
    # Test con skill de Python async
    reply = call(
        prompt="Corrige el siguiente código:\n\nasync def save(model):\n    file, key = find_view_file(model)\n    return file",
        skill="python_async_expert",
    )
    print(f"Ollama con skill dice:\n{reply}")
