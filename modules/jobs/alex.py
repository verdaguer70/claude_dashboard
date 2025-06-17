# modules/jobs/alex.py
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from .base_job import BaseJob
import os
import time

class AlexJob(BaseJob):
    """
    hehe
    """
    
    def get_job_id(self) -> str:
        return "alex"
    
    def get_name(self) -> str:
        return "alex"
    
    def get_description(self) -> str:
        return "hehe"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
        "param1": "valor_ejemplo",
        "param2": 100
}
    
    
    
    def execute(self, config: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Ejecuta el job con la configuración dada
        
        Args:
            config: Configuración del job
            db: Sesión de base de datos
            
        Returns:
            Dict con el resultado de la ejecución
        """
        
        
        # Obtener parámetros de configuración
        param1 = config.get("param1")
        param2 = config.get("param2")
        
        
        # ========================================
        # TU CÓDIGO AQUÍ
        # ========================================
        
        # Ejemplo de operaciones comunes:
        

        # try:
        #     response = requests.get("https://api.example.com/data", timeout=30)
        #     data = response.json()
        # except Exception as e:
        #     return {"output": f"Error en API: {e}", "status": "error"}
        

        
        # ========================================
        # FIN DE TU CÓDIGO
        # ========================================
        
      
        
        output_message = f"Test Job completado exitosamente! {param1} {datetime.now().strftime('%H:%M:%S')}"

        
        # Retornar resultado
        return {
            "output": output_message.strip(),
        }
