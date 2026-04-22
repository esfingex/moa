# 🤖 Solaria Agent Hub (SAH)

Orquestador multimodal de agentes IA diseñado para aliviar el costo de tokens y
acelerar el desarrollo delegando tareas a la IA más apropiada para cada caso.

## 🏗️ Arquitectura

```
agents_orchestrator/
├── core/           # Cerebro: dispatcher y gestor de tareas
├── adapters/       # Conectores: Ollama, OpenAI, Anthropic, Google
├── tasks/          # Cola de tareas pendientes / completadas
├── toolbox/        # Scripts locales de Python/Bash reutilizables
├── logs/           # Historial de ejecuciones
└── project_core/   # Symlink -> /workspace/scw (Solaria)
```

## 🧠 Filosofía "Offload to Local"

En lugar de gastar tokens explicando cambios de código, el Orquestador:
1. Recibe la tarea del Arquitecto (Antigravity)
2. Elige el adapter más eficiente (Ollama para privacidad, GPT-4 para razonamiento)
3. Ejecuta scripts locales del `toolbox/` para modificaciones de archivos
4. Reporta el resultado sin gastar tokens en idas y vueltas

## 🔌 Adapters Disponibles

| Adapter     | Uso Ideal                        |
|-------------|----------------------------------|
| `ollama`    | Análisis privado, búsqueda local |
| `openai`    | Razonamiento complejo            |
| `anthropic` | Código de alta precisión         |
| `google`    | Multimodal, imágenes             |

## 🚀 Quickstart

```bash
python3 core/dispatcher.py --task "fix_awaits" --target "project_core/solaria_modules/..."
```
