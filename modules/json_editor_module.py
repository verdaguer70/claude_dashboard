# modules/json_editor_module.py
from datetime import datetime
from typing import Dict, Any
import json
from .base_module import BaseModule, ModuleConfig
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db, JsonData

class JsonEditorModule(BaseModule):
    def get_config(self) -> ModuleConfig:
        return ModuleConfig(
            id="json-editor",
            name="Editor JSON",
            icon="fas fa-code",
            color="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            endpoint="/api/json-editor",
            description="Editor y almacenamiento de JSON",
            size="large"
        )
    
    def get_data(self) -> Dict[str, Any]:
        return {"status": "ok"}
    
    def setup_routes(self):
        # Obtener el JSON principal (ID=1)
        @self.router.get(f"{self.config.endpoint}/get/1")
        async def get_main_json(db: Session = Depends(get_db)):
            json_data = db.query(JsonData).filter(JsonData.id == 1).first()
            if json_data:
                return {
                    "id": json_data.id,
                    "name": json_data.name,
                    "content": json.loads(json_data.content),
                    "updated_at": json_data.updated_at.isoformat()
                }
            return {"error": "No data found"}
        
        # Guardar el JSON principal
        @self.router.post(f"{self.config.endpoint}/save")
        async def save_main_json(data: dict, db: Session = Depends(get_db)):
            content = data.get("content", {})
            
            # Buscar si existe el registro con ID=1
            json_data = db.query(JsonData).filter(JsonData.id == 1).first()
            
            if json_data:
                # Actualizar existente
                json_data.content = json.dumps(content)
                json_data.updated_at = datetime.now()
            else:
                # Crear nuevo con ID=1
                json_data = JsonData(
                    id=1,
                    name="configuracion_principal",
                    content=json.dumps(content)
                )
                db.add(json_data)
            
            db.commit()
            
            return {
                "status": "success",
                "message": "JSON guardado correctamente"
            }