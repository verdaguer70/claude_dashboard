// static/js/base-module.js
class BaseModule {
    constructor(config) {
        this.id = config.id;
        this.name = config.name;
        this.icon = config.icon;
        this.color = config.color;
        this.endpoint = config.endpoint;
        this.description = config.description;
        this.size = config.size || 'medium';
        this.refreshInterval = config.refreshInterval || 30000;
        this.data = null;
        this.container = null;
        this.refreshTimer = null;
    }

    async init(container) {
        this.container = container;
        
        // Cargar CSS específico del módulo si existe
        this.loadModuleCSS();
        
        // Cargar datos iniciales
        await this.loadData();
        
        // Renderizar
        this.render();
        
        // Configurar auto-refresh si está habilitado
        if (this.refreshInterval > 0) {
            this.startAutoRefresh();
        }
    }

    loadModuleCSS() {
        const cssId = `module-css-${this.id}`;
        if (!document.getElementById(cssId)) {
            const link = document.createElement('link');
            link.id = cssId;
            link.rel = 'stylesheet';
            link.type = 'text/css';
            link.href = `/static/css/modules/${this.id}.css`;
            link.onerror = () => console.log(`No hay CSS específico para el módulo ${this.id}`);
            document.head.appendChild(link);
        }
    }

    async loadData() {
        try {
            const response = await fetch(this.endpoint);
            this.data = await response.json();
            this.onDataLoaded();
        } catch (error) {
            console.error(`Error cargando datos para ${this.id}:`, error);
            this.onDataError(error);
        }
    }

    render() {
        if (!this.container) return;
        
        this.container.innerHTML = '';
        
        const moduleContent = document.createElement('div');
        moduleContent.className = 'module-inner-content';
        moduleContent.innerHTML = this.getTemplate();
        
        this.container.appendChild(moduleContent);
        this.afterRender();
    }

    getTemplate() {
        return `
            <div class="module-default">
                <p>Implementa getTemplate() en tu módulo</p>
                <pre>${JSON.stringify(this.data, null, 2)}</pre>
            </div>
        `;
    }

    onDataLoaded() {
        // Override en módulos específicos si es necesario
    }

    onDataError(error) {
        this.container.innerHTML = `
            <div class="module-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error cargando módulo</p>
            </div>
        `;
    }

    afterRender() {
        // Override para añadir event listeners, gráficos, etc.
    }

    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.refresh();
        }, this.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    async refresh() {
        await this.loadData();
        this.render();
    }

    destroy() {
        this.stopAutoRefresh();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }

    // Utilidades
    formatNumber(num) {
        return num.toLocaleString('es-ES');
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    }

    formatDate(date) {
        return new Intl.DateTimeFormat('es-ES').format(new Date(date));
    }
}

// Registro global de módulos
window.ModuleRegistry = {
    modules: {},
    
    register(ModuleClass) {
        const instance = new ModuleClass();
        this.modules[instance.id] = instance;
        return instance;
    },
    
    get(moduleId) {
        return this.modules[moduleId];
    },
    
    getAll() {
        return Object.values(this.modules);
    }
};