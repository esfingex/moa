# MOA: AI WORKSPACE & SCRATCHPAD

## 1. CONCEPTO
MOA utiliza un área de "Scratchpad" para realizar experimentos de código, pruebas de algoritmos y generación de datos temporales sin ensuciar el `core/` del proyecto.

## 2. ESTRUCTURA DE EXPERIMENTACIÓN
- **`scripts/`**: Contiene herramientas de mantenimiento y automatización (Generadores de docs, actualizadores de modelos).
- **`scratch/`**: (Directorio temporal) Espacio donde los agentes pueden escribir archivos de prueba, logs extendidos y prototipos de funciones.

## 3. FLUJO DE PRUEBA DE CAMPO
1. El Agente **Analista** propone una solución.
2. El Agente **Coder** genera un script en `scripts/` o `scratch/`.
3. El Agente **Tester** ejecuta el script y valida el output.
4. Si es exitoso, MOA integra el código en el destino final.

## 4. TRANSPARENCIA IA-HUMANO
Cualquier archivo generado en el Scratchpad debe incluir un encabezado:
`# [MOA_SCRATCH] - Prototipo para [Tarea]`
Esto permite al usuario humano identificar qué es código estable y qué es experimento.
