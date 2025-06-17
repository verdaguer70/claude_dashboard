# modules/jobs/test.py
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from .base_job import BaseJob
import os
import time
import random

class TestJob(BaseJob):
    """
    Job de prueba que demuestra las capacidades del sistema
    """
    
    def get_job_id(self) -> str:
        return "test"
    
    def get_name(self) -> str:
        return "Test Job"
    
    def get_description(self) -> str:
        return "Job de prueba para verificar el funcionamiento del scheduler"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            "enabled": True,
            "iterations": 5,
            "delay_seconds": 1,
            "message": "Ejecutando test",
            "options": {
                "debug": True,
                "simulate_error": False,
                "process_type": "test"
            }
        }
    
    
    
    def execute(self, config: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Ejecuta el job de prueba con la configuración dada
        """
        print(f"🚀 TestJob.execute() iniciado a las {datetime.now().strftime('%H:%M:%S')}")

        patata="NO TROBAT"
        
        if config.get("hola"):
            patata=config.get("hola")
        
       
        
        output_message = f"""
Test Job completado exitosamente!

- Hora de finalización: {datetime.now().strftime('%H:%M:%S')} {patata}
"""
        
        print(f"Hora de finalización: {datetime.now().strftime('%H:%M:%S')} {patata}")
        
        # Retornar resultado detallado
        return {
            "output": output_message.strip(),
          
        }