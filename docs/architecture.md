# MOA: SYSTEM ARCHITECTURE

## 1. ORCHESTRATION LAYER
MOA actúa como un despachador inteligente entre el usuario y los modelos locales. Utiliza el `ModelRouter` para asignar tareas basándose en el hardware disponible (VRAM/Bandwidth).

## 2. AGENT FACTORY (AUTO-PILOT)
- **Auto-Profiling**: MOA genera automáticamente perfiles `.md` para cualquier modelo instalado en Ollama.
- **Hardware-Awareness**: Las decisiones de ejecución se basan en la lógica de `CanIRun.ai`.

## 3. PERSISTENT MEMORY & TOOLS (MCP)
MOA está vinculado nativamente con el ecosistema **MCP** para otorgar superpoderes a los modelos locales:
- **Caveman (FS)**: Permite que los agentes lean, escriban y auditen archivos en el disco de forma autónoma.
- **Cavemem (Memory)**: Implementa una memoria episódica de largo plazo usando SQLite. Cada interacción se indexa y se recupera automáticamente para dar contexto histórico a los agentes.

## 4. MODEL SCULPTING (MODULAR BRAINS)
El comando `build-model` permite inyectar el "Ground Truth" de Solaria en cualquier modelo base, transformándolo en un experto (Ej: `solaria-master`, `solaria-rutificador`).

## 5. M2M COMMUNICATION
Todos los agentes operan en modo **High-Density**, eliminando capas de conversación humana para maximizar la velocidad y precisión en el intercambio de datos entre IAs.