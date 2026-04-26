# Solaria Architecture Ground Truth (v3) - EL ESTÁNDAR ÚNICO

## 🚨 PROHIBICIÓN ABSOLUTA
- NO USAR **ODOO** (nada de `from odoo import...` ni archivos `.xml`).
- NO USAR **DJANGO** (nada de `serializers.py` ni `ModelSerializer`).
- NO USAR **SQLALCHEMY** PURO (nada de `Column`, `String`, `Integer` de sqlalchemy).

## 🟢 EL ESTÁNDAR SOLARIA (USA ESTO)

### 1. Modelos (`models/*.py`)
Usa exclusivamente las herramientas del núcleo de Solaria.
```python
from app.core.database import Base
from app.core.database.fields import Char, Integer, Many2one, One2many

class MiModelo(Base):
    _name = "modulo.modelo"
    _description = "Descripción"
    
    name = Char(string="Nombre", required=True)
    # create_date y write_date YA ESTÁN INCLUIDOS EN BASE, NO LOS REPITAS.
```

### 2. Vistas Declarativas (`config/views/*.json`)
Solaria NO usa XML. Usa JSON para definir las interfaces.
```json
{
    "modulo.modelo": {
        "views": {
            "tree": {
                "type": "tree",
                "template": "layouts/list_htmx.html",
                "fields": ["name"]
            },
            "form": {
                "type": "form",
                "template": "layouts/form_htmx.html",
                "groups": [
                    { "name": "main", "fields": ["name"] }
                ]
            }
        }
    }
}
```

### 3. Manifiesto (`__manifest__.py`)
Debe ser un archivo Python con una variable literal.
```python
__manifest__ = {
    "name": "Nombre Real",
    "depends": ["solaria_studio"],
    "data": [
        "security/permissions.json",
        "config/views/vistas.json",
        "config/menu.json"
    ]
}
```

## Procedimiento de Generación
1. El Arquitecto genera el modelo Python.
2. El Visualizador genera el JSON de vistas basándose en el modelo.
3. El Oficial de Seguridad genera permisos y menú.

---

### 🔄 Tabla Comparativa: Antes vs Después
| Concepto | Odoo / Django (PROHIBIDO) | Solaria (ESTÁNDAR) |
| :--- | :--- | :--- |
| **Modelos** | `models.Model` | `app.core.database.Base` |
| **Importación** | `from odoo import fields` | `from app.core.database import fields` |
| **Vistas** | Archivos `.xml` | Archivos `.json` en `config/views/` |
| **Rutas** | `urls.py` / `urlpatterns` | Automáticas vía `ModelRegistry` |
| **Controladores** | `@http.route` | `@router.get/post` (FastAPI pattern) |
| **Frontend** | QWeb / Django Templates | Alpine.js + HTMX + Jinja2 |

### 🚫 Prohibiciones Críticas
- **Prohibido**: Importar `odoo`, `django`, `sqlalchemy.Column`.
- **Prohibido**: Usar `XML` para layouts o vistas.
- **Prohibido**: Usar `serializers.py` (usar `to_dict()` del core).

### 🛠️ Protocolo si falla el Auditor
Si eres rechazado por usar términos prohibidos:
1. Revisa que no hayas dejado un import fantasma de `odoo`.
2. Asegúrate de que no estás mencionando estas palabras en tu respuesta final (solo en el `<think>` si es necesario).
3. Si estás explicando por qué algo NO es Odoo, usa la tabla anterior para contrastar.
