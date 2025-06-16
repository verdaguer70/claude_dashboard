# modules/example_module.py
from datetime import datetime
from typing import Dict, Any
import random
from .base_module import BaseModule, ModuleConfig

class ExampleModule(BaseModule):
    """Módulo de ejemplo del Dashboard"""
    
    def get_config(self) -> ModuleConfig:
        """Configuración del módulo de ejemplo"""
        return ModuleConfig(
            id="example",
            name="Ejemplo",
            icon="fas fa-chart-line",
            color="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            endpoint="/api/example",
            description="Módulo de demostración",
            size="medium"
        )
    
    def get_data(self) -> Dict[str, Any]:
        """Datos del módulo de ejemplo"""
        current_time = datetime.now()
        
        return {
            "title": "Módulo de Ejemplo",
            "timestamp": current_time.isoformat(),
            "metrics": {
                "valor1": random.randint(100, 1000),
                "valor2": random.randint(50, 500),
                "valor3": f"{random.uniform(0, 100):.2f}%",
                "valor4": f"{random.randint(1, 24)}h {random.randint(0, 59)}m"
            },
            "chart_data": {
                "labels": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
                "values": [random.randint(20, 100) for _ in range(7)]
            },
            "status": {
                "code": "success",
                "message": "Todo funcionando correctamente"
            }
        }
    
    def setup_routes(self):
        """Configura rutas adicionales del módulo"""
        super().setup_routes()
        
        # Ruta adicional de ejemplo
        @self.router.get(f"{self.config.endpoint}/detail")
        async def get_detail():
            return {
                "module": self.config.name,
                "version": "1.0.0",
                "additional_info": "Esta es información adicional del módulo"
            }