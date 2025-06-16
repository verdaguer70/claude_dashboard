# modules/base_module.py
from abc import ABC, abstractmethod
from fastapi import APIRouter
from typing import Dict, Any
from pydantic import BaseModel

class ModuleConfig(BaseModel):
    """Configuración base para un módulo del dashboard"""
    id: str
    name: str
    icon: str
    color: str
    endpoint: str
    description: str
    size: str = "medium"  # small, medium, large

class BaseModule(ABC):
    """Clase base para todos los módulos del dashboard"""
    
    def __init__(self):
        self.router = APIRouter()
        self.config = self.get_config()
        self.setup_routes()
    
    @abstractmethod
    def get_config(self) -> ModuleConfig:
        """Retorna la configuración del módulo"""
        pass
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Retorna los datos del módulo"""
        pass
    
    def setup_routes(self):
        """Configura las rutas del módulo"""
        self.router.get(self.config.endpoint)(self.get_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración del módulo a diccionario"""
        return self.config.dict()