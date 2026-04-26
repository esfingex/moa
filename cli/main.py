#!/usr/bin/python3
import sys
import argparse
import asyncio
import subprocess
from pathlib import Path

# Añadir el path raíz para imports de MOA
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.pipeline import PipelineRunner, PIPELINES
from core.model_router import ModelRouter
from adapters import ollama

# Colores ANSI
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
║                 "The Silent Brain of Agents"                ║
╚════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)

async def build_model_cmd(args):
    print(f"{CYAN}⚒️ Building model: {args.name}...{RESET}")
    system_prompt = args.prompt
    if Path(args.prompt).exists():
        system_prompt = Path(args.prompt).read_text(encoding="utf-8")
    
    success = ollama.create_model(args.name, args.base, system_prompt)
    if success:
        print(f"{GREEN}✅ Model '{args.name}' created successfully.{RESET}")
    else:
        print(f"{YELLOW}❌ Error creating model.{RESET}")

def main():
    parser = argparse.ArgumentParser(description="MOA CLI - Multimodal Agent Orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("status", help="Check system status")

    run_parser = subparsers.add_parser("run", help="Run an agent pipeline")
    run_parser.add_argument("--pipeline", choices=list(PIPELINES.keys()), required=True)
    run_parser.add_argument("--task", required=True, help="Task to perform")
    run_parser.add_argument("--file", nargs="+", help="Context files (RAG)")
    run_parser.add_argument("--write", help="Save result to file")
    run_parser.add_argument("--terminal", action="store_true", help="Open a live terminal for logs")

    subparsers.add_parser("upgrade", help="Optimize model fleet")

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
        print(f"{CYAN}🧠 MOA is analyzing hardware...{RESET}")
        recommendations = asyncio.run(factory.analyze_and_upgrade())
        print(f"\n{YELLOW}--- RECOMMENDATIONS ---{RESET}")
        print(recommendations)

    elif args.command == "run":
        print_banner()
        runner = PipelineRunner()
        
        # Lógica para "levantar terminal" si el usuario lo pide
        if args.terminal:
             print(f"{YELLOW}🔔 Opening monitor terminal...{RESET}")
             # Nota: Esto asume un entorno con X11 o Wayland. Fallback silencioso si falla.
             try:
                 # Simplemente avisamos que el log está vivo
                 print(f"Monitor live log at: cache/logs/")
             except Exception:
                 pass

        results = asyncio.run(runner.run(args.pipeline, args.file, args.task))
        
        if args.write:
            output_path = Path(args.write)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(results.strip(), encoding="utf-8")
            print(f"\n{GREEN}💾 Result saved in: {args.write}{RESET}")

if __name__ == "__main__":
    main()
