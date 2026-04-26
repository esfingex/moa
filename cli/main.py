#!/usr/bin/python3
import sys
import argparse
import asyncio
from pathlib import Path

# Añadir el path raíz para imports de MOA
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.pipeline import PipelineRunner, PIPELINES
from core.model_router import ModelRouter
from adapters import ollama

# Colores ANSI para el estilo MOA
BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
YELLOW = "\033[1;33m"
MAGENTA = "\033[1;35m"
RESET = "\033[0m"

def print_banner():
    banner = f"""
{MAGENTA}╔════════════════════════════════════════════════════════════╗
║             🚀 MOA: MULTIMODAL AGENT ORCHESTRATOR           ║
║                "The Silent Brain of Solaria"               ║
╚════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)

async def build_model_cmd(args):
    """Lógica para forjar nuevos modelos desde el CLI."""
    print(f"{CYAN}⚒️ Forjando modelo: {args.name}...{RESET}")
    
    # Cargar system prompt si es un archivo o texto directo
    system_prompt = args.prompt
    if Path(args.prompt).exists():
        system_prompt = Path(args.prompt).read_text(encoding="utf-8")
    
    success = ollama.create_model(args.name, args.base, system_prompt)
    if success:
        print(f"{GREEN}✅ Modelo '{args.name}' creado con éxito en Ollama.{RESET}")
    else:
        print(f"{YELLOW}❌ Error al crear el modelo.{RESET}")

def main():
    parser = argparse.ArgumentParser(description="MOA CLI - Multimodal Agent Orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: status
    subparsers.add_parser("status", help="Ver estado de modelos y agentes")

    # Comando: run
    run_parser = subparsers.add_parser("run", help="Ejecutar un pipeline de agentes")
    run_parser.add_argument("--pipeline", choices=list(PIPELINES.keys()), required=True)
    run_parser.add_argument("--task", required=True, help="Tarea a realizar")
    run_parser.add_argument("--file", nargs="+", help="Archivos de contexto (RAG)")
    run_parser.add_argument("--write", help="Guardar resultado en archivo")

    # Comando: build-model (Fábrica de Modelos)
    build_parser = subparsers.add_parser("build-model", help="Forjar un nuevo modelo especializado")
    build_parser.add_argument("--name", required=True, help="Nombre del nuevo modelo")
    build_parser.add_argument("--base", default="qwen2.5-coder:7b", help="Modelo base (Ollama)")
    build_parser.add_argument("--prompt", required=True, help="System Prompt o ruta a archivo .md")

    # Comando: upgrade (Auto-Evolución)
    subparsers.add_parser("upgrade", help="Analizar hardware y optimizar flota de modelos")

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        return

    if args.command == "status":
        print_banner()
        router = ModelRouter()
        print(router.report())

    elif args.command == "upgrade":
        print_banner()
        from core.factory import MOAFactory
        factory = MOAFactory()
        print(f"{CYAN}🧠 MOA está analizando su propio hardware...{RESET}")
        recommendations = asyncio.run(factory.analyze_and_upgrade())
        print(f"\n{YELLOW}--- RECOMENDACIONES DE MOA FACTORY ---{RESET}")
        print(recommendations)
        print(f"\n{GREEN}Tip: Usa 'ollama pull [modelo]' para aplicar los cambios.{RESET}")

    elif args.command == "run":
        print_banner()
        runner = PipelineRunner()
        results = asyncio.run(runner.run(args.pipeline, args.file, args.task))
        
        if args.write:
            output_path = Path(args.write)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(results.strip(), encoding="utf-8")
            print(f"\n{GREEN}💾 Resultado guardado en: {args.write}{RESET}")

    elif args.command == "build-model":
        asyncio.run(build_model_cmd(args))

if __name__ == "__main__":
    main()
