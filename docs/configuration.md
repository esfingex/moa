# MOA: CONFIGURATION GUIDE

## 1. HARDWARE PROFILE
Ubicado en `config/hardware_profile.json`.
Este archivo define los límites de VRAM y el modo de operación (GPU/CPU).
- `vram_gb`: Cantidad de memoria detectable.
- `great_threshold`: Límite para ejecución de alta velocidad (>40t/s).

## 2. MODEL ROUTER
El archivo `core/model_router.py` utiliza el perfil de hardware para asignar tareas.
- `code` -> Prioriza modelos con cuantización Q4_K_M que quepan en el `great_threshold`.
- `reasoning` -> Puede usar modelos más pesados si la VRAM lo permite.

## 3. AGENT PROFILES
Los perfiles en `agents/profiles/` son archivos Markdown con frontmatter YAML.
Cualquier cambio en el `model:` del frontmatter forzará al router a ignorar su lógica automática y usar el modelo especificado.

## 4. OLLAMA API
MOA espera que Ollama esté corriendo en `http://localhost:11434`.
Para cambiar esto, edita la variable `OLLAMA_URL` en `core/model_router.py`.
