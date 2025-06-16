# modules/jobs/base_job.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import json
import traceback
from sqlalchemy.orm import Session

class BaseJob(ABC):
    """Clase base para todos los jobs del sistema"""
    
    def __init__(self):
        self.job_id = self.get_job_id()
        self.name = self.get_name()
        self.description = self.get_description()
        self.default_config = self.get_default_config()
        
    @abstractmethod
    def get_job_id(self) -> str:
        """ID único del job (snake_case)"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Nombre legible del job"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Descripción del job"""
        pass
    
    def get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del job"""
        return {}
    
    @abstractmethod
    def execute(self, config: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Ejecuta el job con la configuración dada
        
        Args:
            config: Configuración del job (JSON parseado)
            db: Sesión de base de datos
            
        Returns:
            Dict con el resultado de la ejecución
        """
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Valida la configuración del job
        
        Returns:
            (is_valid, error_message)
        """
        return True, None
    
    def run(self, config_json: str, db: Session) -> Dict[str, Any]:
        """
        Método principal que ejecuta el job con manejo de errores
        """
        start_time = datetime.now()
        
        try:
            # Parsear configuración
            config = json.loads(config_json) if config_json else {}
            
            # Validar configuración
            is_valid, error_msg = self.validate_config(config)
            if not is_valid:
                return {
                    "status": "failed",
                    "error": f"Configuración inválida: {error_msg}",
                    "started_at": start_time.isoformat(),
                    "finished_at": datetime.now().isoformat()
                }
            
            # Ejecutar job
            result = self.execute(config, db)
            
            # Asegurar formato de respuesta
            if not isinstance(result, dict):
                result = {"output": str(result)}
            
            return {
                "status": "success",
                "started_at": start_time.isoformat(),
                "finished_at": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                **result
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "started_at": start_time.isoformat(),
                "finished_at": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - start_time).total_seconds()
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el job a diccionario para la API"""
        return {
            "job_id": self.job_id,
            "name": self.name,
            "description": self.description,
            "default_config": self.default_config
        }