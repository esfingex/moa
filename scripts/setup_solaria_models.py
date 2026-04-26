import subprocess
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = BASE_DIR / "skills"
SOLARIA_CONTEXT = SKILLS_DIR / "context" / "solaria_base.md"

MODELS = {
    "solaria-coder": {
        "base": "qwen2.5-coder:7b",
        "skill": "qwen25_coder.md"
    },
    "solaria-auditor": {
        "base": "phi4-mini-reasoning:latest",
        "skill": "phi4_tester.md"
    },
    "solaria-writer": {
        "base": "llama3.1:8b",
        "skill": "llama31_writer.md"
    }
}

def create_model(name, base_model, system_content):
    modelfile_content = f"""
FROM {base_model}
SYSTEM \"\"\"{system_content}\"\"\"
PARAMETER temperature 0.1
PARAMETER stop \"<|file_separator|>\"
PARAMETER stop \"```\"
"""
    modelfile_path = BASE_DIR / f"Modelfile_{name}"
    modelfile_path.write_text(modelfile_content, encoding="utf-8")
    
    print(f"🚀 Creando modelo {name} desde {base_model}...")
    try:
        subprocess.run(["ollama", "create", name, "-f", str(modelfile_path)], check=True)
        print(f"✅ Modelo {name} creado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear modelo {name}: {e}")
    finally:
        if modelfile_path.exists():
            modelfile_path.unlink()

def main():
    if not SOLARIA_CONTEXT.exists():
        print(f"Error: No se encuentra {SOLARIA_CONTEXT}")
        return

    solaria_rules = SOLARIA_CONTEXT.read_text(encoding="utf-8")

    for name, config in MODELS.items():
        skill_file = SKILLS_DIR / config["skill"]
        skill_content = ""
        if skill_file.exists():
            # Extraer solo el cuerpo del skill (quitar frontmatter si existe)
            raw_content = skill_file.read_text(encoding="utf-8")
            if raw_content.startswith("---"):
                parts = raw_content.split("---", 2)
                if len(parts) >= 3:
                    skill_content = parts[2].strip()
            else:
                skill_content = raw_content.strip()

        full_system = f"{skill_content}\n\n## ESTÁNDARES SOLARIA (REGLAS DE ORO):\n{solaria_rules}"
        create_model(name, config["base"], full_system)

if __name__ == "__main__":
    main()
