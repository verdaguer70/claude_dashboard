# modules/module_manager.py
from typing import Dict, List, Any
from fastapi import FastAPI
from .base_module import BaseModule, ModuleConfig

class ModuleManager:
    """Gestor central de módulos del dashboard"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.modules: Dict[str, BaseModule] = {}
        self.module_configs: Dict[str, Dict[str, Any]] = {}
    
    def register_module(self, module: BaseModule):
        """Registra un módulo en el sistema"""
        config = module.config
        module_id = config.id
        
        # Guardar el módulo y su configuración
        self.modules[module_id] = module
        self.module_configs[module_id] = config.dict()
        
        # Incluir las rutas del módulo en la aplicación
        self.app.include_router(
            module.router,
            tags=[f"Module: {config.name}"]
        )
        
        print(f"✅ Módulo '{config.name}' registrado: {config.endpoint}")
    
    def get_module(self, module_id: str) -> BaseModule:
        """Obtiene un módulo por su ID"""
        return self.modules.get(module_id)
    
    def get_all_modules(self) -> List[Dict[str, Any]]:
        """Obtiene la configuración de todos los módulos"""
        return list(self.module_configs.values())
    
    def add_custom_module(self, module_config: Dict[str, Any]):
        """Añade un módulo personalizado sin archivo Python"""
        class CustomModule(BaseModule):
            def __init__(self, config_data):
                self.config_data = config_data
                super().__init__()
            
            def get_config(self) -> ModuleConfig:
                return ModuleConfig(**self.config_data)
            
            def get_data(self) -> Dict[str, Any]:
                return {
                    "message": f"Módulo personalizado: {self.config_data['name']}",
                    "info": "Este módulo no tiene implementación Python personalizada",
                    "config": self.config_data
                }
        
        # Crear instancia y registrar
        custom = CustomModule(module_config)
        self.register_module(custom)
        
        return {"status": "success", "module": module_config}