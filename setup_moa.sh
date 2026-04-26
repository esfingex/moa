#!/bin/bash

# MOA: Multimodal Agent Orchestrator - Setup Script
# Este script prepara el entorno para que MOA tome el control.

set -e

echo "🚀 Iniciando instalación de MOA..."

# 1. Verificar dependencias del sistema
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado."
    exit 1
fi

if ! command -v ollama &> /dev/null; then
    echo "⚠️ Advertencia: Ollama no está instalado. Instálalo desde https://ollama.com"
fi

# 2. Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

# 3. Instalar dependencias de Python
echo "📥 Instalando librerías necesarias..."
pip install --upgrade pip
pip install httpx playwright Pillow requests python-dotenv

# 4. Configurar Playwright (para el módulo PaperNews)
echo "🌐 Configurando Playwright..."
playwright install chromium

# 5. Configurar MCP (Caveman/Cavemem)
echo "🧠 Verificando infraestructura MCP..."
if [ -d "$HOME/.cavemem" ]; then
    echo "✅ Memoria Cavemem detectada."
else
    echo "ℹ️ Cavemem no detectado. Se creará al primer uso."
fi

# 6. Permisos del CLI
chmod +x cli/main.py

echo ""
echo "✅ MOA está listo para operar."
echo "Usa 'python3 cli/main.py status' para verificar el estado."
echo "--------------------------------------------------------"
