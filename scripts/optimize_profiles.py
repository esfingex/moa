import sys
import os
from pathlib import Path

# Configurar path raíz
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from adapters import ollama

PROFILES_DIR = BASE_DIR / "agents" / "profiles"

def optimize_profile(file_path):
    print(f"🧬 Optimizando perfil: {file_path.name}...")
    
    content = file_path.read_text(encoding="utf-8")
    
    # Prompt de optimización IA-IA
    prompt = f"""
    Eres el MODELO MAESTRO. Optimiza este perfil de agente de MOA para comunicación MACHINE-TO-MACHINE (IA-IA).
    
    REGLAS:
    1. Mantén el FRONTMATTER YAML exactamente igual (entre --- y ---).
    2. Elimina saludos, cortesías y prosa innecesaria.
    3. Usa directivas densas (ej: ROLE:, OBJECTIVE:, CONSTRAINTS:, OUTPUT_FORMAT:).
    4. Maximiza la precisión técnica sobre la legibilidad humana.
    
    CONTENIDO ORIGINAL:
    {content}
    """
    
    optimized_content = ollama.call(prompt, model="solaria-master", stream=False)
    
    if optimized_content:
        file_path.write_text(optimized_content, encoding="utf-8")
        print(f"✅ Perfil {file_path.name} optimizado.")

if __name__ == "__main__":
    for profile in PROFILES_DIR.glob("*.md"):
        if profile.name == "caveman.md": continue # Mantener las reglas del sistema
        optimize_profile(profile)
