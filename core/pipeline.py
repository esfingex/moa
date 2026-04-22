"""
Pipeline Runner — Solaria Agent Hub
======================================
Orquesta una secuencia de agentes especializados para una tarea compleja.

El Arquitecto (Antigravity) define el pipeline; cada paso se ejecuta
secuencialmente pasando el resultado del anterior como contexto al siguiente.

Pipelines disponibles:
  - code_review:    qwen25_coder → qwen35_analyst → phi4_tester
  - code_write:     qwen35_analyst → qwen25_coder → phi4_tester → llama31_writer
  - doc_only:       llama31_writer
  - fix_and_test:   qwen25_coder → phi4_tester

Uso desde CLI:
  python3 core/pipeline.py --pipeline code_review --file path/to/file.py

Uso desde código:
  runner = PipelineRunner()
  result = runner.run("code_review", rag_files=["my_file.py"], task="Revisa este módulo")
"""
import sys
from pathlib import Path

# Asegurar que core/ esté en el path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "adapters"))

from model_router import ModelRouter

SKILLS_DIR = Path(__file__).parent.parent / "skills"
SOLARIA_CONTEXT_FILE = str(SKILLS_DIR / "context" / "solaria_base.md")


# ============================================================
# DEFINICIÓN DE PIPELINES
# Cada paso: { skill, task_template, use_prev_output }
# ============================================================
PIPELINES: dict[str, list[dict]] = {
    "code_review": [
        {
            "skill": "qwen35_analyst",
            "label": "🔍 Análisis de código",
            "task": "Analiza este código e identifica todos los problemas siguiendo tus reglas.",
            "use_prev": False,
        },
        {
            "skill": "qwen25_coder",
            "label": "⚙️ Corrección",
            "task": "Basándote en el análisis anterior, corrige todos los issues críticos e importantes.",
            "use_prev": True,
        },
        {
            "skill": "phi4_tester",
            "label": "🧪 Tests",
            "task": "Genera tests unitarios para el código corregido.",
            "use_prev": True,
        },
        {
            "skill": "llama31_writer",
            "label": "📝 Documentación",
            "task": "Genera el mensaje de commit y el docstring para los cambios realizados.",
            "use_prev": True,
        },
    ],
    "code_write": [
        {
            "skill": "qwen35_analyst",
            "label": "🔍 Análisis de contexto",
            "task": "Analiza el código existente para entender el patrón que se debe seguir.",
            "use_prev": False,
        },
        {
            "skill": "qwen25_coder",
            "label": "⚙️ Generación de código",
            "task": "Escribe el código nuevo siguiendo el análisis y los patrones detectados.",
            "use_prev": True,
        },
        {
            "skill": "phi4_tester",
            "label": "🧪 Tests",
            "task": "Genera tests unitarios para el código nuevo.",
            "use_prev": True,
        },
    ],
    "fix_and_test": [
        {
            "skill": "qwen25_coder",
            "label": "⚙️ Corrección directa",
            "task": "Corrige el código tal como se indica.",
            "use_prev": False,
        },
        {
            "skill": "phi4_tester",
            "label": "🧪 Tests",
            "task": "Genera tests para validar la corrección.",
            "use_prev": True,
        },
    ],
    "doc_only": [
        {
            "skill": "llama31_writer",
            "label": "📝 Documentación",
            "task": "Genera la documentación completa para el código proporcionado.",
            "use_prev": False,
        },
    ],
}


class PipelineRunner:
    """Ejecuta pipelines de agentes secuencialmente."""

    def __init__(self):
        self.router = ModelRouter()

    def run(
        self,
        pipeline_name: str,
        task: str,
        rag_files: list[str] | None = None,
        verbose: bool = True,
    ) -> dict[str, str]:
        """
        Ejecuta un pipeline completo.

        Args:
            pipeline_name: Nombre del pipeline (ej: "code_review")
            task: Descripción específica de lo que se quiere hacer
            rag_files: Archivos a inyectar como contexto en todos los pasos
            verbose: Si True, imprime el progreso en consola

        Returns:
            Dict con los resultados de cada paso: {"label": "output", ...}
        """
        import ollama as ollama_adapter

        pipeline = PIPELINES.get(pipeline_name)
        if not pipeline:
            available = ", ".join(PIPELINES.keys())
            raise ValueError(f"Pipeline '{pipeline_name}' no existe. Disponibles: {available}")

        # Auto-inject Solaria context if working with project_core
        all_rag = list(rag_files or [])
        if any("project_core" in f or "solaria_modules" in f or "/scw/" in f for f in all_rag):
            if SOLARIA_CONTEXT_FILE not in all_rag:
                all_rag.insert(0, SOLARIA_CONTEXT_FILE)
                if verbose:
                    print("  📌 Contexto Solaria inyectado automáticamente")

        results: dict[str, str] = {}
        prev_output = ""

        if verbose:
            print(f"\n🚀 Pipeline: {pipeline_name} ({len(pipeline)} pasos)\n{'─'*50}")

        for i, step in enumerate(pipeline, 1):
            skill = step["skill"]
            label = step["label"]
            use_prev = step.get("use_prev", False)

            if verbose:
                print(f"\n[{i}/{len(pipeline)}] {label}")
                print(f"  Skill: {skill}")

            # Construir el prompt del paso
            step_task = step["task"]
            if task:
                step_task = f"{task}\n\n{step_task}"

            # El contexto de este paso incluye la salida del paso anterior
            context = f"## Resultado del paso anterior:\n{prev_output}" if use_prev and prev_output else ""

            try:
                output = ollama_adapter.call(
                    prompt=step_task,
                    context=context,
                    skill=skill,
                    rag_files=rag_files,
                )
                prev_output = output
                results[label] = output

                if verbose:
                    preview = output[:200].replace("\n", " ")
                    print(f"  ✅ Completado: {preview}...")

            except Exception as e:
                error_msg = f"Error en paso '{label}': {e}"
                results[label] = error_msg
                prev_output = error_msg
                if verbose:
                    print(f"  ❌ {error_msg}")

        if verbose:
            print(f"\n{'─'*50}\n✅ Pipeline completado: {len(results)} pasos")

        return results


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Solaria Pipeline Runner")
    parser.add_argument("--pipeline", required=True, choices=list(PIPELINES.keys()))
    parser.add_argument("--task", required=True, help="Descripción de la tarea")
    parser.add_argument("--file", nargs="+", default=[], help="Archivos a incluir como contexto")
    parser.add_argument("--output", default=None, help="Guardar resultado en JSON")
    args = parser.parse_args()

    runner = PipelineRunner()
    results = runner.run(
        pipeline_name=args.pipeline,
        task=args.task,
        rag_files=args.file or None,
    )

    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"\n💾 Resultado guardado en: {args.output}")
