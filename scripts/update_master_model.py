import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = BASE_DIR / "skills"
SOLARIA_CONTEXT = SKILLS_DIR / "context" / "solaria_base.md"
CONTACTS_MODEL = BASE_DIR / "project_core" / "app/modules/contacts/models/contacts.py"
CAMPAIGNS_MODEL = BASE_DIR / "project_core" / "app/modules/campaigns/models/campaign.py"
DEV_MANUAL = BASE_DIR / "project_core" / "docs" / "src" / "developer-guide" / "module-development.rst"

def update_master_model_silent():
    # Verificar archivos
    for f in [SOLARIA_CONTEXT, CONTACTS_MODEL, CAMPAIGNS_MODEL, DEV_MANUAL]:
        if not f.exists():
            print(f"❌ Error: No se encuentra {f}")
            return

    solaria_rules = SOLARIA_CONTEXT.read_text(encoding="utf-8")
    contacts_code = CONTACTS_MODEL.read_text(encoding="utf-8")
    campaigns_code = CAMPAIGNS_MODEL.read_text(encoding="utf-8")
    manual_content = DEV_MANUAL.read_text(encoding="utf-8")

    system_content = f"""
Eres el MODELO MAESTRO de Solaria. Estás diseñado para comunicarte con otros AGENTES IA.
PROHIBIDO EXPLICAR, SALUDAR O DAR RESÚMENES. Responde ÚNICAMENTE con el código o datos solicitados.
PROHIBIDO EL USO DE ODOO O DJANGO.

## 1. MANUAL DE DESARROLLO (TEORÍA):
{manual_content.replace('"""', "'''")}

## 2. PILARES DE CÓDIGO (EJEMPLOS MAESTROS):

### MODELO CONTACTOS (Compute, Validations, RUT):
```python
{contacts_code.replace('"""', "'''")}
```

### MODELO CAMPAÑAS (Relationships, Selections):
```python
{campaigns_code.replace('"""', "'''")}
```

## 3. REGLAS DE ORO:
{solaria_rules}
"""

    modelfile_content = f"""
FROM qwen2.5-coder:7b
SYSTEM \"\"\"{system_content}\"\"\"
PARAMETER temperature 0.0
PARAMETER stop \"<|file_separator|>\"
PARAMETER stop \"```\"
"""
    modelfile_path = BASE_DIR / "Modelfile_Master_Silent"
    modelfile_path.write_text(modelfile_content, encoding="utf-8")
    
    print("🚀 Forjando solaria-master (Modo Silencio IA-IA)...")
    try:
        subprocess.run(["ollama", "create", "solaria-master", "-f", str(modelfile_path)], check=True)
        print("✅ Modelo solaria-master (Silent) listo.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
    finally:
        if modelfile_path.exists():
            modelfile_path.unlink()

if __name__ == "__main__":
    update_master_model_silent()
