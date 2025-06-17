#!/usr/bin/env python3
"""
Script para eliminar un Job del módulo Job Scheduler
Uso: python delete_job.py
"""

import os
import re
from pathlib import Path

def list_jobs():
    """Lista todos los jobs disponibles"""
    jobs = []
    
    jobs_dir = Path("modules/jobs")
    if jobs_dir.exists():
        for file in jobs_dir.glob("*.py"):
            if file.name not in ["__init__.py", "base_job.py"]:
                # Leer el archivo para obtener el job_id, name y class name
                try:
                    content = file.read_text(encoding='utf-8')
                    
                    # Buscar nombre de la clase
                    class_match = re.search(r'class\s+(\w+)\s*\(BaseJob\)', content)
                    class_name = class_match.group(1) if class_match else None
                    
                    # Buscar job_id
                    id_match = re.search(r'def get_job_id.*?return\s+["\'](\w+)["\']', content, re.DOTALL)
                    # Buscar job_name
                    name_match = re.search(r'def get_name.*?return\s+["\']([^"\']+)["\']', content, re.DOTALL)
                    
                    if id_match:
                        job_id = id_match.group(1)
                        job_name = name_match.group(1) if name_match else job_id
                        jobs.append({
                            "id": job_id,
                            "name": job_name,
                            "file": file.name,
                            "class_name": class_name
                        })
                except Exception as e:
                    print(f"⚠️  Error leyendo {file.name}: {e}")
    
    return jobs

def delete_job():
    print("🗑️  Eliminador de Jobs del Job Scheduler")
    print("=" * 40)
    
    # Listar jobs disponibles
    jobs = list_jobs()
    
    if not jobs:
        print("\n❌ No se encontraron jobs para eliminar")
        print("   (base_job.py no se puede eliminar)")
        return
    
    print("\n📋 Jobs disponibles:")
    for i, job in enumerate(jobs, 1):
        print(f"  {i}. {job['name']} ({job['id']})")
    
    # Seleccionar job
    choice = input("\n📝 Selecciona el número del job a eliminar (0 para cancelar): ").strip()
    
    if choice == "0":
        print("❌ Cancelado")
        return
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(jobs):
            selected_job = jobs[index]
        else:
            print("❌ Número inválido")
            return
    except ValueError:
        print("❌ Entrada inválida")
        return
    
    # Confirmar eliminación
    print(f"\n⚠️  Se eliminará el job: {selected_job['name']} ({selected_job['id']})")
    confirm = input("¿Estás seguro? (s/n): ").strip().lower()
    
    if confirm != 's':
        print("❌ Cancelado")
        return
    
    # Eliminar archivo
    delete_job_file(selected_job)
    
    # Eliminar del registro
    unregister_job_from_module(selected_job)
    
    # Eliminar de la base de datos
    delete_from_database(selected_job)

def delete_job_file(job):
    """Elimina el archivo del job"""
    
    file_path = Path(f"modules/jobs/{job['file']}")
    
    if file_path.exists():
        try:
            file_path.unlink()
            print(f"✅ Eliminado: {file_path}")
        except Exception as e:
            print(f"❌ Error eliminando archivo: {e}")
    else:
        print(f"⚠️  Archivo no encontrado: {file_path}")

def unregister_job_from_module(job):
    """Elimina el registro del job de job_scheduler_module.py"""
    
    module_file = Path("modules/job_scheduler_module.py")
    
    if not module_file.exists():
        print("❌ Error: No se encuentra job_scheduler_module.py")
        return
    
    try:
        content = module_file.read_text(encoding='utf-8')
        original_content = content
        
        # Leer el archivo del job para encontrar el nombre real de la clase
        job_file_path = Path(f"modules/jobs/{job['file']}")
        class_name = None
        
        if job_file_path.exists():
            job_content = job_file_path.read_text(encoding='utf-8')
            # Buscar la definición de la clase
            class_match = re.search(r'class\s+(\w+)\s*\(BaseJob\)', job_content)
            if class_match:
                class_name = class_match.group(1)
        
        # Si no encontramos el nombre de la clase, intentar deducirlo
        if not class_name:
            job_file_base = job['file'].replace('.py', '')
            class_name = ''.join(word.capitalize() for word in job_file_base.split('_')) + "Job"
        
        print(f"🔍 Buscando referencias de: {class_name}")
        
        # Buscar y eliminar import (puede estar en diferentes formatos)
        job_file_base = job['file'].replace('.py', '')
        
        # Patrón 1: from .jobs.archivo import Clase
        import_pattern1 = f"from \\.jobs\\.{job_file_base} import {class_name}\\s*\\n"
        content = re.sub(import_pattern1, '', content)
        
        # Patrón 2: from .jobs.archivo import * (si existe)
        import_pattern2 = f"from \\.jobs\\.{job_file_base} import \\*\\s*\\n"
        content = re.sub(import_pattern2, '', content)
        
        # Eliminar registro del job
        # Buscar cualquier línea que contenga self.register_job(ClaseEncontrada())
        register_pattern = f"\\s*self\\.register_job\\({class_name}\\(.*?\\)\\)\\s*\\n?"
        content = re.sub(register_pattern, '', content)
        
        # También buscar si hay comentarios relacionados
        comment_pattern = f"\\s*#.*{job['id']}.*\\n"
        content = re.sub(comment_pattern, '', content, flags=re.IGNORECASE)
        
        if content != original_content:
            module_file.write_text(content, encoding='utf-8')
            print(f"✅ Job eliminado de job_scheduler_module.py")
            
            # Mostrar qué se eliminó
            if import_pattern1 in original_content or import_pattern2 in original_content:
                print(f"   - Eliminado import de {class_name}")
            if f"register_job({class_name}" in original_content:
                print(f"   - Eliminado registro de {class_name}")
        else:
            print("⚠️  No se encontraron referencias en job_scheduler_module.py")
            print("   Puede que necesites eliminar manualmente:")
            print(f"   - Import: from .jobs.{job_file_base} import ...")
            print(f"   - Registro: self.register_job({class_name}())")
        
    except Exception as e:
        print(f"❌ Error actualizando job_scheduler_module.py: {e}")

def delete_from_database(job):
    """Elimina el job de la base de datos"""
    
    print("\n🗄️  Limpiando base de datos...")
    
    try:
        from database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        try:
            # Eliminar de scheduled_jobs (las ejecuciones se eliminan en cascada)
            result = db.execute(
                text("DELETE FROM scheduled_jobs WHERE job_id = :job_id"),
                {"job_id": job['id']}
            )
            db.commit()
            
            if result.rowcount > 0:
                print(f"✅ Eliminado de la base de datos ({result.rowcount} registros)")
            else:
                print("ℹ️  No había registros en la base de datos")
                
        except Exception as e:
            print(f"⚠️  Error en base de datos: {e}")
            db.rollback()
        finally:
            db.close()
            
    except ImportError:
        print("⚠️  No se pudo conectar a la base de datos")
        print("   Ejecuta manualmente: DELETE FROM scheduled_jobs WHERE job_id = '{}'".format(job['id']))

def list_all_jobs_detail():
    """Muestra información detallada de todos los jobs"""
    
    print("\n📊 Jobs instalados:")
    print("-" * 60)
    
    jobs = list_jobs()
    
    if not jobs:
        print("No hay jobs personalizados instalados")
        return
    
    for job in jobs:
        print(f"\n📦 Job: {job['name']}")
        print(f"   ID: {job['id']}")
        print(f"   Clase: {job.get('class_name', 'No detectada')}")
        print(f"   Archivo: modules/jobs/{job['file']}")
        
        # Verificar si está registrado
        module_file = Path("modules/job_scheduler_module.py")
        if module_file.exists():
            content = module_file.read_text(encoding='utf-8')
            job_file_base = job['file'].replace('.py', '')
            class_name = job.get('class_name', '')
            
            # Verificar import
            if f"from .jobs.{job_file_base}" in content:
                print("   ✅ Import encontrado")
            else:
                print("   ❌ Import no encontrado")
            
            # Verificar registro
            if class_name and f"register_job({class_name}(" in content:
                print("   ✅ Registrado en módulo")
            else:
                print("   ❌ No registrado en módulo")
        
        # Verificar en BD
        try:
            from database import SessionLocal
            from sqlalchemy import text
            
            db = SessionLocal()
            result = db.execute(
                text("SELECT COUNT(*) FROM scheduled_jobs WHERE job_id = :job_id"),
                {"job_id": job['id']}
            ).scalar()
            db.close()
            
            if result > 0:
                print(f"   📊 En base de datos: Sí ({result} config)")
            else:
                print("   📊 En base de datos: No")
        except:
            print("   📊 En base de datos: No verificado")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Eliminar jobs del Job Scheduler')
    parser.add_argument('--list', action='store_true', help='Listar todos los jobs con detalles')
    args = parser.parse_args()
    
    if args.list:
        list_all_jobs_detail()
    else:
        print("\n✨ ¡Job eliminado exitosamente!")
        print("\n📝 Pasos siguientes:")
        print("1. Reinicia el servidor (Ctrl+C y python app.py)")
        print("2. El job ya no aparecerá en el dashboard")
        
        delete_job()