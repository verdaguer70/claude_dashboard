// static/js/dashboard.js
let currentFilter = null;

document.addEventListener('DOMContentLoaded', async () => {
    await loadModuleScripts();
    
    // Establecer el primer módulo como activo por defecto
    const firstNavItem = document.querySelector('.nav-item.active');
    if (firstNavItem) {
        currentFilter = firstNavItem.dataset.module;
    }
    
    initializeModules();
    
    // Event listeners
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            filterModules(item.dataset.module);
            setActiveNavItem(item);
        });
    });
});

// Carga de modulos 
async function loadModuleScripts() {
    // Cargar de modulos
    await loadScript('/static/js/modules/example.js').catch(err => 
        console.log('Módulo example.js no encontrado, usando vista genérica')
    );
    await loadScript('/static/js/modules/json-editor.js').catch(err => 
    console.log('Módulo json-editor.js no encontrado')
    );

   
}

function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

async function initializeModules() {
    try {
        const response = await fetch('/api/modules');
        const serverModules = await response.json();
        renderModules(serverModules);
    } catch (error) {
        console.error('Error inicializando módulos:', error);
    }
}

function renderModules(serverModules) {
    const grid = document.getElementById('modulesGrid');
    grid.innerHTML = '';
    
    // Siempre filtrar por el módulo seleccionado
    const filteredModules = serverModules.filter(m => m.id === currentFilter);
    
    // Si no hay módulo seleccionado, mostrar mensaje
    if (filteredModules.length === 0 || !currentFilter) {
        grid.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                <i class="fas fa-hand-pointer" style="font-size: 2rem; margin-bottom: 1rem; display: block;"></i>
                <p>Selecciona un módulo del menú lateral</p>
            </div>
        `;
        return;
    }
    
    filteredModules.forEach((moduleConfig, index) => {
        const card = createModuleCard(moduleConfig);
        grid.appendChild(card);
        
        const moduleInstance = window.ModuleRegistry.get(moduleConfig.id);
        
        if (moduleInstance) {
            const contentContainer = card.querySelector('.module-content');
            setTimeout(() => {
                moduleInstance.init(contentContainer);
            }, index * 100);
        } else {
            createGenericModule(moduleConfig, card.querySelector('.module-content'));
        }
    });
}

function createModuleCard(module) {
    const card = document.createElement('div');
    card.className = `module-card ${module.size}`;
    card.style.setProperty('--module-color', module.color);
    card.dataset.moduleId = module.id;
    
    card.innerHTML = `
        <div class="module-header">
            <div class="module-icon">
                <i class="${module.icon}"></i>
            </div>
            <div class="module-title">
                <h3>${module.name}</h3>
                <p>${module.description}</p>
            </div>
            <div class="module-actions">
                <button class="module-action-btn" onclick="refreshModule('${module.id}')" title="Refrescar">
                    <i class="fas fa-sync-alt"></i>
                </button>
            </div>
        </div>
        <div class="module-content" id="content-${module.id}">
            <div class="loading"></div>
        </div>
    `;
    
    return card;
}

async function createGenericModule(moduleConfig, container) {
    try {
        const response = await fetch(moduleConfig.endpoint);
        const data = await response.json();
        
        container.innerHTML = `
            <div style="padding: 1rem;">
                <p style="color: #999; margin-bottom: 1rem;">Vista genérica - Crea /static/js/modules/${moduleConfig.id}.js para personalizar</p>
                <pre style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; overflow: auto;">
${JSON.stringify(data, null, 2)}</pre>
            </div>
        `;
    } catch (error) {
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #ff6b6b;">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                <p>Error cargando módulo</p>
            </div>
        `;
    }
}

window.refreshModule = function(moduleId) {
    const moduleInstance = window.ModuleRegistry.get(moduleId);
    if (moduleInstance) {
        moduleInstance.refresh();
    } else {
        location.reload();
    }
};

window.refreshDashboard = function() {
    location.reload();
};

function filterModules(filter) {
    currentFilter = filter;
    initializeModules();
}

function setActiveNavItem(item) {
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    item.classList.add('active');
}

window.toggleSidebar = function() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('collapsed');
    
    // Guardar estado en localStorage
    const isCollapsed = sidebar.classList.contains('collapsed');
    localStorage.setItem('sidebarCollapsed', isCollapsed);
};

// Restaurar estado del sidebar al cargar
document.addEventListener('DOMContentLoaded', () => {
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed) {
        document.querySelector('.sidebar').classList.add('collapsed');
    }
});