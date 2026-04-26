# MOA: MULTIMODAL AGENT ORCHESTRATOR - SYSTEM CONTEXT

## 1. PROJECT IDENTITY
MOA is a high-performance orchestration layer for local LLMs, designed to control file systems and persistent memory via MCP (Model Context Protocol).

## 2. CORE PRINCIPLES
- **M2M Communication**: Agents communicate via High-Density (dense, technical, no-prose) prompts.
- **Pure Architecture**: Business logic is decoupled from external frameworks.
- **Hardware-Awareness**: Models are selected based on available VRAM/RAM.
- **Silent Brain**: No-prose, direct-to-code/data outputs.

## 3. DIRECTORY STRUCTURE
- `core/`: Pipeline engine, settings, and model routing.
- `adapters/`: External connectors (Ollama) and MCP utilities.
- `agents/profiles/`: Agent identities and task-specific rules.
- `cli/`: Terminal interface (`moa-cli`).
- `docs/`: Technical documentation and sculpting guides.

## 4. PERSISTENT MEMORY (MCP)
- **Caveman**: File system operations.
- **Cavemem**: Episodic memory in SQLite (Path: `~/.cavemem/data.db`).

## 5. MODEL SCULPTING
MOA creates specialized models in Ollama by injecting "Master Pillars" (Development Manuals + Golden Code Patterns) into a base model's SYSTEM prompt.
