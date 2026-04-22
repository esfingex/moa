# 🤖 Solaria Agent Hub (SAH)

**Orquestador multimodal de agentes IA** diseñado para reducir el costo de tokens y acelerar el desarrollo delegando tareas a la IA más especializada para cada caso.

> Arquitecto: **Antigravity** (Google Gemini) — coordina y decide qué agente usa.
> Especialistas: **Modelos Ollama locales** — ejecutan tareas específicas sin enviar datos a la nube.

---

## 🏗️ Arquitectura

```
agents_orchestrator/
├── core/
│   ├── dispatcher.py      # Ejecutor de herramientas individuales
│   ├── pipeline.py        # Orquestador de pipelines secuenciales
│   └── model_router.py    # Selector automático de modelo por tarea
├── adapters/
│   └── ollama.py          # Conector Ollama (Skills + RAG integrado)
├── skills/                # Instrucciones específicas por modelo
│   ├── qwen25_coder.md    # Escritura/edición de código
│   ├── phi4_tester.md     # Tests unitarios y validación lógica
│   ├── qwen35_analyst.md  # Análisis de arquitectura y código
│   └── llama31_writer.md  # Documentación y commits
├── toolbox/               # Scripts locales sin consumo de tokens
│   └── fix_awaits.py      # Corrige await faltantes en código async
├── logs/                  # Historial de ejecuciones
│   └── model_cache.json   # Caché de modelos instalados
└── project_core/          # Symlink → /workspace/scw (Solaria)
```

---

## 🧠 Modelos Instalados y Roles

| Modelo | Tarea Principal | Velocidad | VRAM |
|--------|----------------|-----------|------|
| `qwen2.5-coder:7b` | ⚙️ Escritura de código | ~50 tok/s | 4.7 GB |
| `deepseek-coder:6.7b` | ⚙️ Código Python/SQL | ~55 tok/s | 3.8 GB |
| `qwen3.5:9b` | 🔍 Análisis de arquitectura | ~49 tok/s | 5.1 GB |
| `phi4-mini-reasoning` | 🧠 Tests y validación lógica | ~33 tok/s | 3.2 GB |
| `llama3.1:8b` | 📝 Docs, commits, chat | ~55 tok/s | 4.6 GB |
| `nomic-embed-text` | 📐 RAG y búsqueda semántica | N/A | 0.3 GB |

**Hardware**: 12 GB VRAM — modelos >12 GB en la lista negra del router.

---

## 🔌 Skills System

Cada modelo tiene un archivo `.md` en `skills/` con:
- **Frontmatter YAML**: modelo, temperatura, tipo de tarea
- **System Prompt**: rol e identidad del agente
- **Reglas estrictas**: qué puede y no puede hacer
- **Formato de respuesta**: template exacto de salida

```yaml
---
name: qwen25_coder
model: qwen2.5-coder:7b
task_type: code
temperature: 0.05
---
```

---

## 🚀 Pipelines Disponibles

| Pipeline | Pasos | Cuándo usarlo |
|----------|-------|---------------|
| `code_review` | Análisis → Corrección → Tests → Docs | Revisar código existente |
| `code_write` | Análisis contexto → Código → Tests | Escribir código nuevo |
| `fix_and_test` | Corrección → Tests | Fix rápido con validación |
| `doc_only` | Documentación | Solo docs/commits |

### Ejemplo de uso

```bash
# Revisar un archivo completo
python3 core/pipeline.py \
  --pipeline code_review \
  --task "Revisar el controlador de permisos de campo" \
  --file project_core/solaria_modules/solaria_studio/controllers/studio_controller.py \
  --output results/review_studio_controller.json

# Corregir y testear
python3 core/pipeline.py \
  --pipeline fix_and_test \
  --task "Corregir los awaits faltantes en las funciones async" \
  --file project_core/solaria_modules/solaria_studio/controllers/studio_controller.py
```

---

## 🔧 Toolbox (Sin consumo de tokens)

Scripts locales que el Dispatcher puede ejecutar sin consultar a ninguna IA:

```bash
# Corregir awaits faltantes en un archivo Python
echo '{"target_file": "project_core/path/to/file.py"}' | python3 toolbox/fix_awaits.py

# Vía Dispatcher
python3 core/dispatcher.py \
  --task fix_awaits \
  --args '{"target_file": "project_core/path/to/file.py"}'
```

---

## 🗺️ Roadmap

- [x] Model Router con hardware awareness (12 GB VRAM)
- [x] Skills por modelo (qwen2.5-coder, phi4, qwen3.5, llama3.1)
- [x] Pipeline Runner secuencial
- [x] RAG automático (inyección de archivos como contexto)
- [ ] Adapter OpenAI/Anthropic para tareas que requieran más capacidad
- [ ] Tool `inject_html` para modificar templates sin errores de línea
- [ ] Tool `audit_imports` para detectar imports faltantes
- [ ] CLI interactivo con selección de pipeline
- [ ] Integración con git: auto-commit tras pipeline exitoso
