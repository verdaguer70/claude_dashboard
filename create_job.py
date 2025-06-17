#!/usr/bin/env python3
"""
Script para crear un nuevo Job en el módulo Job Scheduler
Uso: python create_job.py
"""

import os
import re
import json
from pathlib import Path

def validate_job_id(job_id):
    """Valida que el ID del job sea válido (snake_case)"""
    if not re.match(r'^[a-z0-9_]+$', job_id):
        print("❌ Error: El ID solo puede contener letras minúsculas, números y guiones bajos")
        return False
    return True

def snake_to_class(snake_str):
    """Convierte snake_case a ClassName"""
    return ''.join(word.capitalize() for word in snake_str.split('_'))

def create_job():
    print("🚀 Creador de Jobs para Job Scheduler")
    print("=" * 40)
    
    # Solicitar información del job
    job_name = input("\n📝 Nombre del job (ej: Mi Nuevo Job): ").strip()
    if not job_name:
        print("❌ Error: El nombre no puede estar vacío")
        return
    
    # Generar ID automáticamente desde el nombre
    job_id = job_name.lower().replace(' ', '_')
    job_id = re.sub(r'[^a-z0-9_]', '', job_id)
    
    print(f"📝 ID generado: {job_id}")
    
    job_description = input("📝 Descripción breve: ").strip()
    if not job_description:
        job_description = f"Job {job_name}"
    
    # Confirmar
    print("\n📋 Resumen del job:")
    print(f"  Nombre: {job_name}")
    print(f"  ID: {job_id}")
    print(f"  Descripción: {job_description}")
    
    confirm = input("\n¿Crear job? (s/n): ").strip().lower()
    if confirm != 's':
        print("❌ Cancelado")
        return
    
    # Crear el archivo del job
    if create_job_file(job_id, job_name, job_description):
        # Registrar en el módulo
        register_job_in_module(job_id)

def create_job_file(job_id, job_name, job_description):
    """Crea el archivo del job"""
    
    class_name = snake_to_class(job_id) + "Job"
    
    # Configuración por defecto personalizada
    default_config = {
        "enabled": True,
        "param1": "valor_ejemplo",
        "param2": 100,
        "options": {
            "debug": False,
            "timeout": 30
        }
    }
    
    # Formatear la configuración correctamente para Python
    config_str = json.dumps(default_config, indent=8)
    # Asegurar que los booleanos estén en formato Python
    config_str = config_str.replace(': true', ': True').replace(': false', ': False').replace(': null', ': None')
    
    content = f'''# modules/jobs/{job_id}.py
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from .base_job import BaseJob
import os
import time

class {class_name}(BaseJob):
    """
    {job_description}
    """
    
    def get_job_id(self) -> str:
        return "{job_id}"
    
    def get_name(self) -> str:
        return "{job_name}"
    
    def get_description(self) -> str:
        return "{job_description}"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {config_str}
    
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
            return {{
                "output": "Job deshabilitado",
                "status": "skipped"
            }}
        
        # Obtener parámetros de configuración
        param1 = config.get("param1", "default")
        param2 = config.get("param2", 100)
        debug = config.get("options", {{}}).get("debug", False)
        
        if debug:
            print(f"🔍 Debug: Ejecutando {{self.get_name()}} con param1={{param1}}, param2={{param2}}")
        
        # ========================================
        # TU CÓDIGO AQUÍ
        # ========================================
        
        # Ejemplo de operaciones comunes:
        
        # 1. Consultar base de datos
        # try:
        #     result = db.execute(text("SELECT COUNT(*) as total FROM mi_tabla"))
        #     total = result.scalar()
        # except Exception as e:
        #     return {{"output": f"Error en BD: {{e}}", "status": "error"}}
        
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
        #     return {{"output": f"Error en API: {{e}}", "status": "error"}}
        
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
        return {{
            "output": resultado,
            "param1": param1,
            "param2": param2,
            "timestamp": datetime.now().isoformat()
        }}
'''
    
    # Crear el archivo
    try:
        # Asegurar que existe el directorio
        jobs_dir = Path("modules/jobs")
        jobs_dir.mkdir(parents=True, exist_ok=True)
        
        job_path = Path(f"modules/jobs/{job_id}.py")
        
        # Verificar si ya existe
        if job_path.exists():
            overwrite = input(f"⚠️  El archivo {job_path} ya existe. ¿Sobrescribir? (s/n): ").lower()
            if overwrite != 's':
                print("❌ Cancelado")
                return False
        
        job_path.write_text(content, encoding='utf-8')
        print(f"✅ Creado: {job_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando archivo: {e}")
        return False

def register_job_in_module(job_id):
    """Registra el job en job_scheduler_module.py"""
    
    class_name = snake_to_class(job_id) + "Job"
    module_file = Path("modules/job_scheduler_module.py")
    
    if not module_file.exists():
        print("❌ Error: No se encuentra job_scheduler_module.py")
        return
    
    try:
        content = module_file.read_text(encoding='utf-8')
        
        # 1. Añadir import
        # Buscar la sección de imports de jobs
        import_section = re.search(
            r'(# Importar jobs\n)((?:from \.jobs\.\w+ import \w+\n)*)',
            content
        )
        
        if import_section:
            imports_start = import_section.start(2)
            imports_end = import_section.end(2)
            
            new_import = f"from .jobs.{job_id} import {class_name}\n"
            
            # Verificar si ya existe
            if new_import.strip() not in content:
                # Insertar al final de los imports de jobs
                content = content[:imports_end] + new_import + content[imports_end:]
                print(f"✅ Import añadido: {new_import.strip()}")
            else:
                print("⚠️  Import ya existe")
        else:
            print("⚠️  No se encontró la sección de imports de jobs")
            print("   Añade manualmente después de '# Importar jobs':")
            print(f"   from .jobs.{job_id} import {class_name}")
        
        # 2. Registrar el job
        # Buscar el método _discover_jobs
        discover_section = re.search(
            r'def _discover_jobs\(self\):\s*\n\s*"""[^"]*"""\s*\n(.*?)(?=\n\s*def|\n\s*\n\s*def|\Z)',
            content,
            re.DOTALL
        )
        
        if discover_section:
            method_content = discover_section.group(1)
            method_start = discover_section.start(1)
            
            # Buscar el último register_job
            registers = list(re.finditer(r'self\.register_job\([^)]+\)\)', method_content))
            
            if registers:
                last_register = registers[-1]
                insert_pos = method_start + last_register.end()
                
                # Determinar la indentación
                last_line_start = method_content.rfind('\n', 0, last_register.start()) + 1
                last_line = method_content[last_line_start:last_register.start()]
                indent = len(last_line) - len(last_line.lstrip())
                
                new_register = f"\n{' ' * indent}self.register_job({class_name}())"
                
                # Verificar si ya existe
                if f"register_job({class_name}())" not in content:
                    content = content[:insert_pos] + new_register + content[insert_pos:]
                    print(f"✅ Job registrado: self.register_job({class_name}())")
                else:
                    print("⚠️  Job ya está registrado")
            else:
                print("⚠️  No se encontraron otros jobs registrados")
                print("   Añade manualmente en _discover_jobs():")
                print(f"   self.register_job({class_name}())")
        
        # Guardar cambios
        module_file.write_text(content, encoding='utf-8')
        
        print("\n✨ ¡Job creado exitosamente!")
        print("\n📝 Pasos siguientes:")
        print(f"1. Edita modules/jobs/{job_id}.py y añade tu lógica")
        print("2. Reinicia el servidor (Ctrl+C y python app.py)")
        print("3. Ve al módulo Job Scheduler en el dashboard")
        print("4. Configura y ejecuta tu nuevo job")
        
    except Exception as e:
        print(f"❌ Error registrando job: {e}")
        print("\n⚠️  Deberás registrar manualmente el job:")
        print(f"1. En modules/job_scheduler_module.py, añade el import:")
        print(f"   from .jobs.{job_id} import {class_name}")
        print(f"2. En _discover_jobs(), añade:")
        print(f"   self.register_job({class_name}())")

if __name__ == "__main__":
    create_job()