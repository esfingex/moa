import sys
import os
from pathlib import Path

# Añadir el path raíz para imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from adapters import ollama

def generate_moa_doc(title, topic, output_file):
    print(f"📄 Generando doc: {title}...")
    prompt = f"Genera la documentación técnica en Markdown para el proyecto MOA. Título: {title}. Tema: {topic}."
    content = ollama.call(prompt, model="solaria-master", stream=False)
    
    out_path = BASE_DIR / "docs" / output_file
    out_path.write_text(content, encoding="utf-8")
    print(f"✅ Guardado en {output_file}")

if __name__ == "__main__":
    docs = [
        ("Arquitectura MOA", "Diseño multimodal, integración con MCP (caveman/cavemem), jerarquía Core/Adapters/Agents.", "architecture.md"),
        ("Guía de Model Sculpting", "Cómo crear Modelfiles especializados, uso del comando build-model, reducción de latencia y ruido IA-IA.", "model_sculpting.md"),
        ("Manual de Usuario CLI", "Uso de los comandos status, run y build-model con ejemplos.", "getting_started.md")
    ]
    
    for title, topic, file in docs:
        generate_moa_doc(title, topic, file)
