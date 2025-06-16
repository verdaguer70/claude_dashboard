# 🚀 Dashboard Modular

Un sistema de dashboard modular y extensible construido con **FastAPI** (backend) y **JavaScript vanilla** (frontend). Diseñado para ser fácil de mantener y expandir con nuevos módulos.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Uso Básico](#-uso-básico)
- [Crear un Nuevo Módulo](#-crear-un-nuevo-módulo)
- [Arquitectura](#-arquitectura)
- [API Endpoints](#-api-endpoints)
- [Personalización](#-personalización)
- [Solución de Problemas](#-solución-de-problemas)

## ✨ Características

- ✅ **Sistema modular**: Añade o elimina módulos fácilmente
- ✅ **API REST** con FastAPI y documentación automática
- ✅ **Interfaz moderna** con dark mode y animaciones
- ✅ **Sin dependencias JavaScript**: Todo con vanilla JS
- ✅ **Auto-refresh** configurable por módulo
- ✅ **Responsive** para móviles y tablets
- ✅ **Scripts automatizados** para crear/eliminar módulos
- ✅ **Base de datos** SQLite incluida (opcional)

## 📁 Estructura del Proyecto

```
dashboard-modular/
│
├── app.py                      # Aplicación principal FastAPI
├── database.py                 # Configuración de base de datos (opcional)
├── requirements.txt            # Dependencias Python
├── create_module.py           # Script para crear módulos
├── delete_module.py           # Script para eliminar módulos
│
├── modules/                    # Módulos Python del backend
│   ├── __init__.py
│   ├── base_module.py         # Clase base para todos los módulos
│   ├── module_manager.py      # Gestor de módulos
│   └── example_module.py      # Módulo de ejemplo
│
├── static/                     # Archivos estáticos
│   ├── css/
│   │   ├── style.css          # Estilos globales
│   │   └── modules/           # CSS específico de cada módulo
│   │       └── example.css
│   └── js/
│       ├── base-module.js     # Clase base JavaScript
│       ├── dashboard.js       # Controlador principal
│       └── modules/           # JS específico de cada módulo
│           └── example.js
│
└── templates/
    └── index.html             # Template principal
```

## 🛠️ Instalación

### Requisitos previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/dashboard-modular.git
cd dashboard-modular
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
python app.py
```

5. **Abrir en el navegador**
```
http://localhost:8000
```

## 🎯 Uso Básico

### Navegación
- Click en los módulos del sidebar para ver cada uno
- Botón de refrescar (↻) para actualizar manualmente
- El sidebar se puede ocultar con el botón ☰

### Ver documentación de la API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ➕ Crear un Nuevo Módulo

### Método 1: Usando el script automatizado (Recomendado)

```bash
python create_module.py
```

El script te guiará paso a paso para:
1. Definir el ID y nombre del módulo
2. Seleccionar un icono
3. Elegir colores
4. Configurar el tamaño

**Ejemplo de sesión:**
```
🚀 Creador de Módulos para Dashboard
========================================

📝 ID del módulo (ej: mi-modulo): ventas
📝 Nombre del módulo (ej: Mi Módulo): Gestión de Ventas
📝 Descripción breve: Control y análisis de ventas

🎨 Iconos sugeridos:
  1. fas fa-chart-bar (Gráficos)
  2. fas fa-users (Usuarios)
  3. fas fa-cog (Configuración)
  ...
Elige una opción (1-6): 1

✅ Módulo creado exitosamente!
```

### Método 2: Creación manual

#### 1. Crear el módulo Python (`modules/mi_modulo_module.py`)

```python
from typing import Dict, Any
from .base_module import BaseModule, ModuleConfig

class MiModuloModule(BaseModule):
    def get_config(self) -> ModuleConfig:
        return ModuleConfig(
            id="mi-modulo",
            name="Mi Módulo",
            icon="fas fa-star",
            color="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            endpoint="/api/mi-modulo",
            description="Descripción del módulo",
            size="medium"
        )
    
    def get_data(self) -> Dict[str, Any]:
        return {
            "mensaje": "Hola desde mi módulo",
            "valor": 42,
            "items": ["Item 1", "Item 2", "Item 3"]
        }
```

#### 2. Registrar en `app.py`

```python
from modules.mi_modulo_module import MiModuloModule

mi_modulo = MiModuloModule()
module_manager.register_module(mi_modulo)
```

#### 3. Crear el JavaScript (opcional) (`static/js/modules/mi-modulo.js`)

```javascript
class MiModuloModule extends BaseModule {
    constructor() {
        super({
            id: 'mi-modulo',
            name: 'Mi Módulo',
            icon: 'fas fa-star',
            color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            endpoint: '/api/mi-modulo',
            description: 'Descripción del módulo',
            size: 'medium'
        });
    }

    getTemplate() {
        if (!this.data) return '<div class="loading"></div>';
        
        return `
            <div class="mi-modulo">
                <h3>${this.data.mensaje}</h3>
                <p>Valor: ${this.data.valor}</p>
                <ul>
                    ${this.data.items.map(item => `<li>${item}</li>`).join('')}
                </ul>
            </div>
        `;
    }
}

window.ModuleRegistry.register(MiModuloModule);
```

#### 4. Añadir a `dashboard.js`

En la función `loadModuleScripts()`:
```javascript
await loadScript('/static/js/modules/mi-modulo.js').catch(err => 
    console.log('Módulo mi-modulo.js no encontrado')
);
```

#### 5. Crear CSS (opcional) (`static/css/modules/mi-modulo.css`)

```css
.mi-modulo {
    padding: 1rem;
}

.mi-modulo h3 {
    color: var(--primary-color);
    margin-bottom: 1rem;
}
```

### Eliminar un módulo

```bash
python delete_module.py
```

## 🏗️ Arquitectura

### Backend (Python/FastAPI)

```
BaseModule (ABC)
    ↓
ModuleConfig → Define metadatos
    ↓
Módulo específico → Implementa get_data()
    ↓
ModuleManager → Registra y gestiona
    ↓
FastAPI → Expone endpoints
```

### Frontend (JavaScript)

```
BaseModule (Class)
    ↓
Módulo específico → Implementa getTemplate()
    ↓
ModuleRegistry → Registro global
    ↓
Dashboard.js → Renderiza módulos
```

### Flujo de datos

1. Usuario hace click en módulo
2. Dashboard.js solicita datos a `/api/[modulo]`
3. FastAPI ejecuta `get_data()` del módulo
4. Datos JSON se envían al frontend
5. JavaScript renderiza usando `getTemplate()`
6. CSS específico se aplica automáticamente

## 📡 API Endpoints

### Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Página principal del dashboard |
| GET | `/api/modules` | Lista todos los módulos |
| POST | `/api/modules` | Añade un módulo dinámicamente |
| GET | `/api/[module-id]` | Datos del módulo específico |

### Endpoints de módulos

Cada módulo puede definir endpoints adicionales:

```python
def setup_routes(self):
    super().setup_routes()
    
    @self.router.get(f"{self.config.endpoint}/detail")
    async def get_detail():
        return {"detail": "info"}
    
    @self.router.post(f"{self.config.endpoint}/update")
    async def update_data(data: dict):
        return {"status": "updated"}
```

## 🎨 Personalización

### Temas y colores

Editar variables CSS en `static/css/style.css`:

```css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --bg-color: #0f0f0f;
    --sidebar-bg: #1a1a1a;
    --card-bg: #1f1f1f;
    --text-primary: #ffffff;
    --text-secondary: #b3b3b3;
}
```

### Tamaños de módulos

- `small`: Ocupa 1 columna
- `medium`: Ocupa 1 columna (por defecto)
- `large`: Ocupa 2 columnas

### Iconos

Usa cualquier icono de [Font Awesome 6](https://fontawesome.com/icons):
- `fas fa-chart-line`
- `fas fa-users`
- `fas fa-database`
- etc.

### Intervalos de actualización

En el constructor del módulo JavaScript:
```javascript
refreshInterval: 30000  // milisegundos (30 segundos)
refreshInterval: 0      // Desactivar auto-refresh
```

## 🔧 Solución de Problemas

### El módulo no aparece

1. Verifica que esté registrado en `app.py`
2. Comprueba la consola del navegador (F12)
3. Reinicia el servidor

### Error 404 en archivos estáticos

1. Verifica que la estructura de carpetas sea correcta
2. Los archivos JS/CSS son sensibles a mayúsculas/minúsculas

### El módulo muestra vista genérica

- Esto es normal si no has creado el archivo JS
- Crea `/static/js/modules/[tu-modulo].js` para personalizar

### Base de datos (si usas SQLite)

```bash
# Ver contenido de la base de datos
sqlite3 dashboard.db
.tables
.schema
SELECT * FROM json_data;
.quit
```

## 📚 Ejemplos de módulos

### Módulo simple (solo Python)

```python
class StatusModule(BaseModule):
    def get_config(self) -> ModuleConfig:
        return ModuleConfig(
            id="status",
            name="Estado del Sistema",
            icon="fas fa-heartbeat",
            color="linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
            endpoint="/api/status",
            description="Monitor de estado",
            size="small"
        )
    
    def get_data(self) -> Dict[str, Any]:
        return {
            "status": "online",
            "uptime": "99.9%",
            "last_check": datetime.now().isoformat()
        }
```

### Módulo con base de datos

Ver el ejemplo completo en `modules/json_editor_module.py`

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/NuevoModulo`)
3. Commit cambios (`git commit -m 'Añadir módulo X'`)
4. Push a la rama (`git push origin feature/NuevoModulo`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- FastAPI por el excelente framework
- Font Awesome por los iconos
- La comunidad open source

---

**¿Necesitas ayuda?** Abre un issue en GitHub o contacta al equipo de desarrollo.