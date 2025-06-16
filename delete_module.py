#!/usr/bin/env python3
"""
Script para eliminar un módulo del Dashboard
Uso: python delete_module.py
"""

import os
import sys
import re
from pathlib import Path

def list_modules():
    """Lista todos los módulos disponibles"""
    modules = []
    
    # Buscar módulos en la carpeta modules/
    modules_dir = Path("modules")
    if modules_dir.exists():
        for file in modules_dir.glob("*_module.py"):
            if file.name != "base_module.py" and file.name != "__init__.py":
                # Extraer el nombre del módulo
                module_name = file.stem.replace("_module", "")
                modules.append(module_name)
    
    return modules

def get_module_files(module_id):
    """Obtiene todos los archivos relacionados con un módulo"""
    module_python_name = module_id.replace('-', '_')
    
    files = {
        'python': Path(f"modules/{module_python_name}_module.py"),
        'javascript': Path(f"static/js/modules/{module_id}.js"),
        'css': Path(f"static/css/modules/{module_id}.css")
    }
    
    return files

def delete_module():
    print("🗑️  Eliminador de Módulos del Dashboard")
    print("=" * 40)
    
    # Listar módulos disponibles
    modules = list_modules()
    
    if not modules:
        print("\n❌ No se encontraron módulos para eliminar")
        print("   (Los módulos base no se pueden eliminar)")
        return
    
    print("\n📋 Módulos disponibles:")
    for i, module in enumerate(modules, 1):
        module_id = module.replace('_', '-')
        print(f"  {i}. {module_id}")
    
    # Seleccionar módulo
    choice = input("\n📝 Selecciona el número del módulo a eliminar (0 para cancelar): ").strip()
    
    if choice == "0":
        print("❌ Cancelado")
        return
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(modules):
            module_python_name = modules[index]
            module_id = module_python_name.replace('_', '-')
        else:
            print("❌ Número inválido")
            return
    except ValueError:
        print("❌ Entrada inválida")
        return
    
    # Obtener archivos del módulo
    files = get_module_files(module_id)
    
    print(f"\n⚠️  Se eliminarán los siguientes archivos del módulo '{module_id}':")
    for file_type, file_path in files.items():
        if file_path.exists():
            print(f"  - {file_path}")
        else:
            print(f"  - {file_path} (no existe)")
    
    # Confirmar eliminación
    confirm = input("\n¿Estás seguro de eliminar este módulo? (s/n): ").strip().lower()
    if confirm != 's':
        print("❌ Cancelado")
        return
    
    # Eliminar archivos
    deleted_count = 0
    for file_type, file_path in files.items():
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"✅ Eliminado: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error eliminando {file_path}: {e}")
        else:
            print(f"⚠️  No encontrado: {file_path}")
    
    if deleted_count > 0:
        print(f"\n✨ Módulo '{module_id}' eliminado ({deleted_count} archivos)")
        
        # Instrucciones para limpiar el código
        module_class_name = ''.join(word.capitalize() for word in module_id.split('-'))
        print("\n📝 Pasos siguientes:")
        print("1. En app.py, elimina estas líneas:")
        print(f"   from modules.{module_python_name}_module import {module_class_name}Module")
        print(f"   {module_python_name} = {module_class_name}Module()")
        print(f"   module_manager.register_module({module_python_name})")
        print("\n2. En dashboard.js, elimina de loadModuleScripts():")
        print(f"   await loadScript('/static/js/modules/{module_id}.js')...")
        print("\n3. Si el módulo usaba base de datos, considera limpiar las tablas")
        print("\n4. Reinicia el servidor")
        
        # Buscar referencias en app.py
        print("\n🔍 Buscando referencias en app.py...")
        try:
            with open("app.py", "r", encoding="utf-8") as f:
                app_content = f.read()
                
            if module_python_name in app_content or module_class_name in app_content:
                print("⚠️  Se encontraron referencias al módulo en app.py")
                print("   Recuerda eliminarlas manualmente")
            else:
                print("✅ No se encontraron referencias en app.py")
        except Exception as e:
            print(f"⚠️  No se pudo verificar app.py: {e}")
            
    else:
        print("\n⚠️  No se eliminó ningún archivo")

def list_module_details():
    """Muestra detalles de todos los módulos"""
    print("\n📊 Detalles de módulos instalados:")
    print("-" * 60)
    
    modules = list_modules()
    for module in modules:
        module_id = module.replace('_', '-')
        files = get_module_files(module_id)
        
        print(f"\n📦 Módulo: {module_id}")
        exists_count = sum(1 for f in files.values() if f.exists())
        print(f"   Archivos: {exists_count}/{len(files)}")
        
        for file_type, file_path in files.items():
            status = "✅" if file_path.exists() else "❌"
            print(f"   {status} {file_type.capitalize()}: {file_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Eliminar módulos del Dashboard')
    parser.add_argument('--list', action='store_true', help='Listar detalles de todos los módulos')
    args = parser.parse_args()
    
    if args.list:
        list_module_details()
    else:
        delete_module()