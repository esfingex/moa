# 🚀 MOA: Multimodal Agent Orchestrator
**"The Silent Brain for Local LLMs"**

MOA is a high-performance orchestration layer designed to control local AI models (via Ollama) with a focus on hardware optimization, persistent memory (MCP), and machine-to-machine (M2M) communication.

## ✨ Key Features
- **Hardware-Aware Routing**: Automatic model selection based on VRAM and Bandwidth (Logic by CanIRun.ai).
- **M2M High-Density**: Expert agents optimized for zero-prose, technical exchange.
- **Persistent Memory**: Integrated with **Cavemem** (SQLite) and **Caveman** (FS) via MCP.
- **Auto-Onboarding**: Self-configuring system that audits your hardware and suggests the best model fleet.
- **Model Sculpting**: Tooling to create specialized expert models in seconds.

## 🏛️ Project Philosophy: Pure Orchestrator
MOA is designed as a **Pure Orchestrator**. It follows a strict **Separation of Concerns**:
1. **The Engine (MOA)**: Manages hardware detection, model routing, caching, and execution pipelines.
2. **The Workload (Solaria & others)**: All domain-specific logic, scrapers, and business rules must reside **outside** this repository.
3. **The Plugin Pattern**: MOA orchestrates external modules but never embeds their code in its `core/`.

## 🛠️ Installation
```bash
git clone https://github.com/[TU_USUARIO]/moa-orchestrator.git
cd moa-orchestrator
python3 moa_onboarding.py
```

## ⚖️ License
This project is licensed under the **GNU GPLv3**. Feel free to fork, modify, and share, keeping the spirit of Open Source alive.

---
*Built with ❤️ for the Solaria Ecosystem.*
