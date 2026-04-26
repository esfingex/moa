## REGLAS DE MANIPULACIÓN DE ARCHIVOS (CAVEMAN)

Como agente de MOA, tienes permiso para interactuar con el sistema de archivos de `project_core` siguiendo estas reglas:

1. **Lectura Segura**: Antes de editar un archivo, léelo completamente para entender el contexto.
2. **Edición Atómica**: Prefiere hacer cambios pequeños y específicos en lugar de sobrescribir archivos grandes.
3. **Validación de Rutas**: Todas las rutas deben ser relativas a la raíz del proyecto o usar la variable `project_core`.
4. **No Destructivo**: No borres archivos a menos que sea explícitamente solicitado.

Si generas un comando para ejecutar en la terminal, asegúrate de que sea compatible con Ubuntu Linux.
