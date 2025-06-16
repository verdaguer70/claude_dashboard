#!/usr/bin/env python3
"""
Script para crear un nuevo módulo en el Dashboard
Uso: python create_module.py
"""

import os
import sys
import re
from pathlib import Path

def validate_module_id(module_id):
    """Valida que el ID del módulo sea válido"""
    if not re.match(r'^[a-z0-9-]+$', module_id):
        print("❌ Error: El ID solo puede contener letras minúsculas, números y guiones")
        return False
    return True

def create_module():
    print("🚀 Creador de Módulos para Dashboard")
    print("=" * 40)
    
    # Solicitar información del módulo
    module_id = input("\n📝 ID del módulo (ej: mi-modulo): ").strip().lower()
    if not validate_module_id(module_id):
        return
    
    module_name = input("📝 Nombre del módulo (ej: Mi Módulo): ").strip()
    if not module_name:
        print("❌ Error: El nombre no puede estar vacío")
        return
    
    module_description = input("📝 Descripción breve: ").strip()
    
    # Iconos comunes de Font Awesome
    print("\n🎨 Iconos sugeridos:")
    print("  1. fas fa-chart-bar (Gráficos)")
    print("  2. fas fa-users (Usuarios)")
    print("  3. fas fa-cog (Configuración)")
    print("  4. fas fa-database (Base de datos)")
    print("  5. fas fa-bell (Notificaciones)")
    print("  6. Otro (escribir manualmente)")
    
    icon_choice = input("\nElige una opción (1-6): ").strip()
    icon_map = {
        "1": "fas fa-chart-bar",
        "2": "fas fa-users",
        "3": "fas fa-cog",
        "4": "fas fa-database",
        "5": "fas fa-bell"
    }
    
    if icon_choice in icon_map:
        module_icon = icon_map[icon_choice]
    else:
        module_icon = input("📝 Icono (ej: fas fa-star): ").strip()
    
    # Colores predefinidos
    print("\n🎨 Gradientes sugeridos:")
    print("  1. Púrpura: linear-gradient(135deg, #667eea 0%, #764ba2 100%)")
    print("  2. Rosa: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)")
    print("  3. Azul: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)")
    print("  4. Verde: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)")
    print("  5. Naranja: linear-gradient(135deg, #fa709a 0%, #fee140 100%)")
    print("  6. Otro (escribir manualmente)")
    
    color_choice = input("\nElige una opción (1-6): ").strip()
    color_map = {
        "1": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "2": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "3": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "4": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "5": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
    }
    
    if color_choice in color_map:
        module_color = color_map[color_choice]
    else:
        module_color = input("📝 Gradiente CSS: ").strip()
    
    # Tamaño del módulo
    print("\n📏 Tamaño del módulo:")
    print("  1. small (pequeño)")
    print("  2. medium (mediano)")
    print("  3. large (grande)")
    
    size_choice = input("\nElige una opción (1-3) [2]: ").strip() or "2"
    size_map = {"1": "small", "2": "medium", "3": "large"}
    module_size = size_map.get(size_choice, "medium")
    
    # Confirmar
    print("\n📋 Resumen del módulo:")
    print(f"  ID: {module_id}")
    print(f"  Nombre: {module_name}")
    print(f"  Descripción: {module_description}")
    print(f"  Icono: {module_icon}")
    print(f"  Color: {module_color}")
    print(f"  Tamaño: {module_size}")
    
    confirm = input("\n¿Crear módulo? (s/n): ").strip().lower()
    if confirm != 's':
        print("❌ Cancelado")
        return
    
    # Crear archivos
    create_module_files(module_id, module_name, module_description, 
                       module_icon, module_color, module_size)

def create_module_files(module_id, module_name, module_description, 
                       module_icon, module_color, module_size):
    """Crea todos los archivos necesarios para el módulo"""
    
    # Convertir module_id a formato Python (guiones a guiones bajos)
    module_class_name = ''.join(word.capitalize() for word in module_id.split('-'))
    module_python_name = module_id.replace('-', '_')
    
    # 1. Crear archivo Python del módulo
    python_content = f'''# modules/{module_python_name}_module.py
from datetime import datetime
from typing import Dict, Any
import random
from .base_module import BaseModule, ModuleConfig

class {module_class_name}Module(BaseModule):
    """
    Módulo: {module_name}
    Descripción: {module_description}
    """
    
    def get_config(self) -> ModuleConfig:
        """Configuración del módulo"""
        return ModuleConfig(
            id="{module_id}",
            name="{module_name}",
            icon="{module_icon}",
            color="{module_color}",
            endpoint="/api/{module_id}",
            description="{module_description}",
            size="{module_size}"
        )
    
    def get_data(self) -> Dict[str, Any]:
        """
        Retorna los datos del módulo.
        
        TODO: Reemplaza estos datos de ejemplo con tu lógica real.
        Puedes conectar a una base de datos, API externa, etc.
        """
        current_time = datetime.now()
        
        return {{
            "title": "{module_name}",
            "timestamp": current_time.isoformat(),
            "last_update": current_time.strftime("%H:%M:%S"),
            
            # TODO: Añade aquí tus datos específicos
            "ejemplo_metrica_1": random.randint(100, 1000),
            "ejemplo_metrica_2": random.randint(50, 500),
            "ejemplo_porcentaje": f"{{random.uniform(0, 100):.2f}}%",
            
            # Ejemplo de datos para gráfico
            "chart_data": {{
                "labels": ["Lun", "Mar", "Mié", "Jue", "Vie"],
                "values": [random.randint(10, 100) for _ in range(5)]
            }},
            
            # Ejemplo de lista
            "items": [
                {{"id": 1, "name": "Item 1", "status": "active"}},
                {{"id": 2, "name": "Item 2", "status": "inactive"}},
                {{"id": 3, "name": "Item 3", "status": "active"}}
            ],
            
            "status": {{
                "code": "success",
                "message": "Módulo funcionando correctamente"
            }}
        }}
    
    def setup_routes(self):
        """Configura rutas adicionales del módulo"""
        super().setup_routes()
        
        # TODO: Añade aquí rutas adicionales si las necesitas
        
        # Ejemplo: Ruta para obtener detalles
        @self.router.get(f"{{self.config.endpoint}}/detail")
        async def get_detail():
            return {{
                "module": self.config.name,
                "version": "1.0.0",
                "info": "Información detallada del módulo"
            }}
        
        # Ejemplo: Ruta para actualizar datos
        @self.router.post(f"{{self.config.endpoint}}/update")
        async def update_data(data: dict):
            # TODO: Implementar lógica de actualización
            return {{
                "status": "success",
                "message": "Datos actualizados"
            }}
'''
    
    # 2. Crear archivo JavaScript del módulo
    js_content = f'''// static/js/modules/{module_id}.js

/**
 * Módulo: {module_name}
 * Descripción: {module_description}
 */
class {module_class_name}Module extends BaseModule {{
    constructor() {{
        super({{
            id: '{module_id}',
            name: '{module_name}',
            icon: '{module_icon}',
            color: '{module_color}',
            endpoint: '/api/{module_id}',
            description: '{module_description}',
            size: '{module_size}',
            refreshInterval: 30000 // Actualizar cada 30 segundos
        }});
    }}

    getTemplate() {{
        if (!this.data) return '<div class="loading"></div>';
        
        return `
            <div class="{module_id}-module">
                <!-- Header del módulo -->
                <div class="module-header-content">
                    <h3>${{this.data.title}}</h3>
                    <p class="last-update">Última actualización: ${{this.data.last_update}}</p>
                </div>
                
                <!-- TODO: Personaliza el contenido según tus necesidades -->
                
                <!-- Ejemplo: Grid de métricas -->
                <div class="metrics-grid">
                    <div class="metric-box">
                        <div class="metric-value">${{this.formatNumber(this.data.ejemplo_metrica_1)}}</div>
                        <div class="metric-label">Métrica 1</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-value">${{this.formatNumber(this.data.ejemplo_metrica_2)}}</div>
                        <div class="metric-label">Métrica 2</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-value">${{this.data.ejemplo_porcentaje}}</div>
                        <div class="metric-label">Porcentaje</div>
                    </div>
                </div>
                
                <!-- Ejemplo: Gráfico -->
                <div class="chart-container">
                    <h4>Gráfico de ejemplo</h4>
                    <canvas id="{module_id}-chart"></canvas>
                </div>
                
                <!-- Ejemplo: Lista de items -->
                <div class="items-list">
                    <h4>Items</h4>
                    ${{this.data.items.map(item => `
                        <div class="item ${{item.status}}">
                            <span class="item-name">${{item.name}}</span>
                            <span class="item-status">${{item.status}}</span>
                        </div>
                    `).join('')}}
                </div>
                
                <!-- Estado -->
                <div class="module-status ${{this.data.status.code}}">
                    <i class="fas fa-check-circle"></i>
                    <span>${{this.data.status.message}}</span>
                </div>
            </div>
        `;
    }}

    afterRender() {{
        // TODO: Añade aquí la lógica post-renderizado
        // Por ejemplo: inicializar gráficos, event listeners, etc.
        
        this.drawChart();
    }}

    drawChart() {{
        // TODO: Implementa tu lógica de gráfico aquí
        const canvas = this.container.querySelector('#{module_id}-chart');
        if (!canvas || !this.data.chart_data) return;
        
        const ctx = canvas.getContext('2d');
        const data = this.data.chart_data;
        
        // Ejemplo simple de gráfico de barras
        canvas.width = canvas.offsetWidth;
        canvas.height = 200;
        
        // ... implementar lógica del gráfico
        
        console.log('TODO: Implementar gráfico para {module_name}');
    }}
}}

// Registrar el módulo
window.ModuleRegistry.register({module_class_name}Module);
'''
    
    # 3. Crear archivo CSS del módulo
    css_content = f'''/* static/css/modules/{module_id}.css */

/**
 * Estilos para el módulo: {module_name}
 */

.{module_id}-module {{
    padding: 1rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}}

/* Header del módulo */
.{module_id}-module .module-header-content {{
    text-align: center;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}}

.{module_id}-module h3 {{
    color: var(--text-primary);
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}}

.{module_id}-module .last-update {{
    color: var(--text-secondary);
    font-size: 0.875rem;
}}

/* Grid de métricas */
.{module_id}-module .metrics-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
}}

.{module_id}-module .metric-box {{
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}}

.{module_id}-module .metric-box:hover {{
    background: rgba(255, 255, 255, 0.08);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}}

.{module_id}-module .metric-value {{
    font-size: 2rem;
    font-weight: bold;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}}

.{module_id}-module .metric-label {{
    font-size: 0.875rem;
    color: var(--text-secondary);
}}

/* Contenedor del gráfico */
.{module_id}-module .chart-container {{
    background: rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    padding: 1.5rem;
}}

.{module_id}-module .chart-container h4 {{
    color: var(--text-primary);
    margin-bottom: 1rem;
}}

.{module_id}-module canvas {{
    width: 100%;
    height: 200px;
}}

/* Lista de items */
.{module_id}-module .items-list {{
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
}}

.{module_id}-module .items-list h4 {{
    color: var(--text-primary);
    margin-bottom: 1rem;
}}

.{module_id}-module .item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    transition: all 0.3s ease;
}}

.{module_id}-module .item:hover {{
    background: rgba(255, 255, 255, 0.08);
}}

.{module_id}-module .item-status {{
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    text-transform: uppercase;
}}

.{module_id}-module .item.active .item-status {{
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
}}

.{module_id}-module .item.inactive .item-status {{
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}}

/* Estado del módulo */
.{module_id}-module .module-status {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem;
    border-radius: 8px;
    margin-top: auto;
}}

.{module_id}-module .module-status.success {{
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
}}

/* TODO: Añade aquí más estilos según necesites */
'''
    
    # Crear archivos
    try:
        # Archivo Python
        python_path = Path(f"modules/{module_python_name}_module.py")
        python_path.write_text(python_content, encoding='utf-8')
        print(f"✅ Creado: {python_path}")
        
        # Archivo JavaScript
        js_path = Path(f"static/js/modules/{module_id}.js")
        js_path.parent.mkdir(parents=True, exist_ok=True)
        js_path.write_text(js_content, encoding='utf-8')
        print(f"✅ Creado: {js_path}")
        
        # Archivo CSS
        css_path = Path(f"static/css/modules/{module_id}.css")
        css_path.parent.mkdir(parents=True, exist_ok=True)
        css_path.write_text(css_content, encoding='utf-8')
        print(f"✅ Creado: {css_path}")
        
        # Instrucciones finales
        print("\n✨ ¡Módulo creado exitosamente!")
        print("\n📝 Pasos siguientes:")
        print(f"1. Edita los archivos creados y personaliza el contenido")
        print(f"2. En app.py, añade estas líneas después de los imports:")
        print(f"   from modules.{module_python_name}_module import {module_class_name}Module")
        print(f"\n3. Y después de registrar otros módulos:")
        print(f"   {module_python_name} = {module_class_name}Module()")
        print(f"   module_manager.register_module({module_python_name})")
        print(f"\n4. En dashboard.js, añade en loadModuleScripts():")
        print(f"   await loadScript('/static/js/modules/{module_id}.js').catch(err => ")
        print(f"       console.log('Módulo {module_id}.js no encontrado')")
        print(f"   );")
        print(f"\n5. Reinicia el servidor y prueba tu nuevo módulo")
        
    except Exception as e:
        print(f"❌ Error creando archivos: {e}")

if __name__ == "__main__":
    create_module()