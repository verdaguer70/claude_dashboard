from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from typing import Dict, Any
import database  # Para crear las tablas


# Importar el gestor de módulos
from modules.module_manager import ModuleManager
from modules.example_module import ExampleModule
from modules.job_scheduler_module import JobSchedulerModule



app = FastAPI(title="Dashboard Modular")

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Inicializar el gestor de módulos
module_manager = ModuleManager(app)

# Modelo para añadir módulos dinámicamente
class DashboardModule(BaseModel):
    id: str
    name: str
    icon: str
    color: str
    endpoint: str
    description: str
    size: str = "medium"

### Registro de modulos ###
example_module = ExampleModule()
module_manager.register_module(example_module)


job_scheduler = JobSchedulerModule()
module_manager.register_module(job_scheduler)



# Rutas principales
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal del dashboard"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "modules": {m["id"]: m for m in module_manager.get_all_modules()}
    })

@app.get("/api/modules")
async def get_modules():
    """Obtiene la lista de todos los módulos registrados"""
    return JSONResponse(content=module_manager.get_all_modules())

@app.post("/api/modules")
async def add_module(module: DashboardModule):
    """Añade un nuevo módulo dinámicamente"""
    try:
        result = module_manager.add_custom_module(module.dict())
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=400
        )

if __name__ == "__main__":
    print("🚀 Dashboard Modular iniciado")
    print("📍 Abre http://localhost:8000 en tu navegador")
    print("📦 Módulos registrados:")
    for module in module_manager.get_all_modules():
        print(f"   - {module['name']} ({module['id']}): {module['endpoint']}")
    
    # Usar string de importación para habilitar reload
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)