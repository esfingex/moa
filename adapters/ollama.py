import json
import urllib.request
from pathlib import Path
from typing import Generator

# Importación relativa al núcleo de MOA
try:
    from core.config_loader import settings
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.config_loader import settings

# Rutas actualizadas a la nueva jerarquía MOA
BASE_DIR = Path(__file__).parent.parent
AGENTS_DIR = BASE_DIR / "agents" / "profiles"
CAVEMAN_SKILL = AGENTS_DIR / "caveman.md"

def _get_router():
    from core.model_router import ModelRouter
    return ModelRouter()

def create_model(name: str, base: str, system_prompt: str) -> bool:
    """
    Crea un nuevo modelo en Ollama inyectando un Modelfile dinámico.
    Útil para el 'Model Sculpting' de MOA.
    """
    url = settings.ollama_url.replace("/generate", "/create")
    modelfile = f'FROM {base}\nSYSTEM """{system_prompt}"""'
    
    payload = {
        "name": name,
        "modelfile": modelfile,
        "stream": False
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=600) as response:
            return response.status == 200
    except Exception as e:
        print(f"Error MOA Factory: {e}")
        return False

def load_skill(skill_name: str) -> tuple[str, str, str, float]:
    skill_file = AGENTS_DIR / f"{skill_name}.md"
    if not skill_file.exists():
        return "", "qwen2.5-coder:7b", "chat", 0.0

    content = skill_file.read_text(encoding="utf-8")
    model = "qwen2.5-coder:7b"
    temperature = 0.0
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
                    except ValueError: pass
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
    stream: bool | None = None
) -> str | Generator[str, None, None]:
    system_prompt = ""
    skill_model = model or "qwen2.5-coder:7b"
    temperature = 0.0
    task_type = "chat"
    
    if skill:
        system_prompt, skill_model, task_type, temperature = load_skill(skill)

    if settings.use_caveman and CAVEMAN_SKILL.exists():
        caveman_rules = CAVEMAN_SKILL.read_text(encoding="utf-8")
        system_prompt = f"{system_prompt}\n\n{caveman_rules}"

    if not model:
        try:
            router = _get_router()
            model = router.best_for(task_type) or skill_model
        except Exception:
            model = skill_model

    rag_context = ""
    if rag_files:
        rag_parts = []
        for fpath in rag_files:
            p = Path(fpath)
            if p.exists():
                content = p.read_text(encoding="utf-8")
                if len(content) > 3000: content = content[:3000] + "\n..."
                rag_parts.append(f"### Archivo: {p.name}\n```\n{content}\n```")
        rag_context = "\n\n## CONTEXTO PROYECTO\n" + "\n\n".join(rag_parts)
    
    # Soporte para memoria MCP (cavemem)
    mem_context = ""
    if settings.use_cavemem:
        from adapters.utils import get_cavemem_context
        mem_context = get_cavemem_context(prompt, skill=skill)

    full_prompt = f"{system_prompt}\n\n{rag_context}\n\n{mem_context}\n\n{context}\n\n## TAREA\n{prompt}"
    should_stream = stream if stream is not None else settings.streaming
    
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": should_stream,
        "options": {"temperature": temperature},
    }

    try:
        req = urllib.request.Request(
            settings.ollama_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        
        if not should_stream:
            with urllib.request.urlopen(req, timeout=300) as response:
                data = json.loads(response.read())
                return data.get("response", "").strip()
        else:
            def generate():
                with urllib.request.urlopen(req, timeout=300) as response:
                    for line in response:
                        if line:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                yield chunk["response"]
                            if chunk.get("done"):
                                break
            return generate()
    except Exception as e:
        return f"Error MOA Ollama: {e}"
