# MOA INSTALLATION GUIDE

## 1. REQUISITOS PREVIOS
- **Python**: 3.10+ (Recomendado 3.12).
- **Ollama**: Instalado y corriendo en el puerto 11434.
- **VRAM**: Mínimo 8GB para una experiencia fluida (Optimizado para 12GB+).

## 2. PASOS DE INSTALACIÓN
1. **Clonar repositorio**:
   ```bash
   git clone [url-moa]
   cd agents_orchestrator
   ```
2. **Entorno Virtual**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Inicialización**:
   ```bash
   python3 moa_onboarding.py
   ```

## 3. VERIFICACIÓN
Ejecuta el auditor de salud para confirmar que todo está en orden:
```bash
python3 scripts/check_moa.py
```

## 4. COMANDOS CLAVE
- `python3 cli/main.py status`: Ver perfil de hardware.
- `python3 cli/main.py upgrade`: Optimizar modelos según VRAM.
- `python3 cli/main.py run --pipeline thinker --task "..."`: Ejecutar pipeline inteligente.
