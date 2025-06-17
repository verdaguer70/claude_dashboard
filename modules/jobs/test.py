# modules/jobs/test.py
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from .base_job import BaseJob
import os
import time

class TestJob(BaseJob):
    """
    test job
    """
    
    def get_job_id(self) -> str:
        return "test"
    
    def get_name(self) -> str:
        return "test"
    
    def get_description(self) -> str:
        return "test job"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
        "enabled": True,
        "param1": "valor_ejemplo",
        "param2": 100,
        "options": {
                "debug": False,
                "timeout": 30
        }
    }
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """Validación de la configuración"""
        # Ejemplo de validación
        if not config.get("enabled", True):
            return True, None  # Permitir deshabilitar el job
            
        # Añadir más validaciones según necesites
        # if config.get("param2", 0) < 0:
        #     return False, "param2 no puede ser negativo"
        
        return True, None
    
    def execute(self, config: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Ejecuta el job con la configuración dada
        
        Args:
            config: Configuración del job
            db: Sesión de base de datos
            
        Returns:
            Dict con el resultado de la ejecución
        """
        # Verificar si está habilitado
        if not config.get("enabled", True):
            return {
                "output": "Job deshabilitado",
                "status": "skipped"
            }
        
        # Obtener parámetros de configuración
        param1 = config.get("param1", "default")
        param2 = config.get("param2", 100)
        debug = config.get("options", {}).get("debug", False)
        
        if debug:
            print(f"🔍 Debug: Ejecutando {self.get_name()} con param1={param1}, param2={param2}")
        
        # ========================================
        # TU CÓDIGO AQUÍ
        # ========================================
        
        # Ejemplo de operaciones comunes:
        
        # 1. Consultar base de datos
        # try:
        #     result = db.execute(text("SELECT COUNT(*) as total FROM mi_tabla"))
        #     total = result.scalar()
        # except Exception as e:
        #     return {"output": f"Error en BD: {e}", "status": "error"}
        
        # 2. Procesar archivos
        # import glob
        # files = glob.glob("/path/to/files/*.txt")
        # for file in files:
        #     with open(file, 'r') as f:
        #         content = f.read()
        #         # Procesar contenido
        
        # 3. Llamar APIs externas
        # import requests
        # try:
        #     response = requests.get("https://api.example.com/data", timeout=30)
        #     data = response.json()
        # except Exception as e:
        #     return {"output": f"Error en API: {e}", "status": "error"}
        
        # 4. Enviar notificaciones
        # if resultado_importante:
        #     # send_email("admin@example.com", "Alerta", "Mensaje")
        #     pass
        
        # ========================================
        # FIN DE TU CÓDIGO
        # ========================================
        
        # Simular trabajo (eliminar esto)
        time.sleep(1)  # Simular proceso
        resultado = f"Proceso completado con éxito"
        
        # Retornar resultado
        return {
            "output": resultado,
            "param1": param1,
            "param2": param2,
            "timestamp": datetime.now().isoformat()
        }
