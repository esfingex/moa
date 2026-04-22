# Solaria Framework — Contexto Base para Agentes IA
# Este archivo se inyecta como RAG en cualquier skill que trabaje con Solaria.
# Actualizar cuando cambie la arquitectura del framework.

## ARQUITECTURA GENERAL

```
/workspace/scw/                      ← Proyecto principal
├── app/
│   ├── core/
│   │   ├── database/
│   │   │   ├── Base               ← Clase base de todos los modelos
│   │   │   ├── fields.py          ← Char, Integer, Many2one, Boolean, etc.
│   │   │   ├── sessions.py        ← get_session() para acceso a DB
│   │   │   └── session_context.py ← db_context, set_current_db_name
│   │   ├── modules/
│   │   │   └── module_registry.py ← Descubrimiento de módulos
│   │   └── settings.py            ← Configuración global
│   └── modules/
│       └── base/                  ← Módulo núcleo del sistema
│           ├── models/            ← Modelos del sistema (sys.*)
│           └── views/             ← Templates HTML
└── solaria_modules/               ← Módulos adicionales (addons)
    ├── solaria_studio/            ← IDE visual (INSTALADO)
    └── [otros]/                   ← No instalados en DB actual
```

## MODELOS DEL SISTEMA (sys.*)

| Modelo | Tabla | Descripción |
|--------|-------|-------------|
| `sys.users` | sys_users | Usuarios del sistema |
| `sys.groups` | sys_groups | Roles y grupos de seguridad |
| `sys.acl` | sys_acl | Permisos CRUD por modelo |
| `sys.field_acl` | sys_field_acl | Permisos a nivel de campo |
| `sys.module` | sys_module | Módulos instalados |

## PATRONES CLAVE

### Consulta a DB (siempre async)
```python
from app.core.database.sessions import get_session
from sqlalchemy import select

async with get_session() as session:
    result = await session.execute(select(MiModelo).where(MiModelo.activo == True))
    rows = result.scalars().all()
```

### Acceso al Registry de Modelos
```python
from app.core.database.registry import registry

modelo_cls = registry.get("sys.users")  # Retorna la clase o None
todos = registry.get_all()              # Dict {_name: clase}
```

### Multi-tenancy (DB por request)
```python
from app.core.database.session_context import db_context

with db_context("nombre_base_de_datos"):
    # Código que usa la DB específica
    async with get_session() as session:
        ...
```

### Módulos Instalados (filtrar por DB activa)
```python
async with get_session() as session:
    stmt = select(SysModule.name).where(SysModule.state == 'installed')
    result = await session.execute(stmt)
    installed = {row[0] for row in result.all()}
```

## DB ACTUAL EN DESARROLLO
- Nombre: `solaria_whp_v1`
- Usuario: `admin` / `admin123`
- Puerto: `9000`
- Solo módulos instalados: `base`, `solaria_studio`
