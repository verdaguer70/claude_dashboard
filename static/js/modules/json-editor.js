// static/js/modules/json-editor.js
class JsonEditorModule extends BaseModule {
    constructor() {
        super({
            id: 'json-editor',
            name: 'Editor JSON',
            icon: 'fas fa-code',
            color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            endpoint: '/api/json-editor',
            description: 'Editor y almacenamiento de JSON',
            size: 'large',
            refreshInterval: 0
        });
        
        this.currentData = {
            id: 1, // ID fijo para un único JSON
            content: {
                "mensaje": "¡Bienvenido al editor JSON!",
                "fecha": new Date().toISOString(),
                "configuracion": {
                    "tema": "oscuro",
                    "autoguardado": false,
                    "version": "1.0.0"
                }
            }
        };
    }

    async init(container) {
        this.container = container;
        this.loadModuleCSS();
        await this.loadSavedData();
        this.render();
    }

    async loadSavedData() {
        try {
            const response = await fetch(`${this.endpoint}/get/1`);
            const data = await response.json();
            if (!data.error) {
                this.currentData.content = data.content;
            }
        } catch (error) {
            console.log('No hay datos guardados, usando valores por defecto');
        }
    }

    getTemplate() {
        return `
            <div class="json-editor-redesign">
                <div class="editor-toolbar">
                    <div class="toolbar-title">
                        <i class="fas fa-code"></i>
                        <h2>Editor JSON Visual</h2>
                    </div>
                    <div class="toolbar-actions">
                        <button class="action-btn format-btn" onclick="jsonEditor.formatJson()">
                            <i class="fas fa-magic"></i>
                            <span>Formatear</span>
                        </button>
                        <button class="action-btn save-btn" onclick="jsonEditor.saveJson()">
                            <i class="fas fa-save"></i>
                            <span>Guardar</span>
                        </button>
                    </div>
                </div>
                
                <div class="editor-workspace">
                    <div class="editor-panel">
                        <div class="panel-header">
                            <span class="panel-title">
                                <i class="fas fa-edit"></i> Editor
                            </span>
                            <div id="syntax-status" class="syntax-indicator"></div>
                        </div>
                        <div class="editor-wrapper">
                            <div class="line-numbers" id="lineNumbers"></div>
                            <textarea 
                                id="json-editor-textarea" 
                                class="code-editor"
                                spellcheck="false"
                                placeholder='{\n  "escribe": "tu JSON aquí"\n}'
                            >${JSON.stringify(this.currentData.content, null, 2)}</textarea>
                        </div>
                    </div>
                    
                    <div class="preview-panel">
                        <div class="panel-header">
                            <span class="panel-title">
                                <i class="fas fa-eye"></i> Vista Previa
                            </span>
                        </div>
                        <div id="json-preview" class="json-preview"></div>
                    </div>
                </div>
                
                <div class="editor-footer">
                    <div id="status-message" class="status-message"></div>
                    <div class="footer-info">
                        <span id="char-count">0 caracteres</span>
                        <span class="separator">•</span>
                        <span id="line-count">0 líneas</span>
                    </div>
                </div>
            </div>
        `;
    }

    afterRender() {
        window.jsonEditor = this;
        
        const editor = this.container.querySelector('#json-editor-textarea');
        editor?.addEventListener('input', () => {
            this.updateLineNumbers();
            this.validateAndPreview();
            this.updateStats();
        });
        
        // Inicializar
        this.updateLineNumbers();
        this.validateAndPreview();
        this.updateStats();
        
        // Auto-guardar cada 30 segundos si hay cambios
        this.autoSaveInterval = setInterval(() => {
            if (this.hasChanges) {
                this.saveJson(true);
            }
        }, 30000);
    }

    updateLineNumbers() {
        const editor = this.container.querySelector('#json-editor-textarea');
        const lineNumbers = this.container.querySelector('#lineNumbers');
        const lines = editor.value.split('\n').length;
        
        lineNumbers.innerHTML = Array.from({length: lines}, (_, i) => 
            `<div class="line-number">${i + 1}</div>`
        ).join('');
    }

    validateAndPreview() {
        const editor = this.container.querySelector('#json-editor-textarea');
        const preview = this.container.querySelector('#json-preview');
        const syntaxStatus = this.container.querySelector('#syntax-status');
        
        try {
            const json = JSON.parse(editor.value);
            this.hasChanges = true;
            
            // Actualizar indicador de sintaxis
            syntaxStatus.innerHTML = '<i class="fas fa-check-circle"></i> JSON válido';
            syntaxStatus.className = 'syntax-indicator valid';
            
            // Renderizar preview
            preview.innerHTML = this.renderJsonTree(json);
            
        } catch (error) {
            syntaxStatus.innerHTML = '<i class="fas fa-exclamation-circle"></i> Error de sintaxis';
            syntaxStatus.className = 'syntax-indicator invalid';
            
            preview.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>JSON inválido</p>
                    <small>${error.message}</small>
                </div>
            `;
        }
    }

    renderJsonTree(obj, level = 0) {
        if (obj === null) return '<span class="json-null">null</span>';
        if (typeof obj === 'boolean') return `<span class="json-boolean">${obj}</span>`;
        if (typeof obj === 'number') return `<span class="json-number">${obj}</span>`;
        if (typeof obj === 'string') return `<span class="json-string">"${obj}"</span>`;
        
        if (Array.isArray(obj)) {
            if (obj.length === 0) return '<span class="json-array">[]</span>';
            
            return `
                <div class="json-array">
                    <span class="json-bracket">[</span>
                    <div class="json-items">
                        ${obj.map((item, i) => `
                            <div class="json-item">
                                <span class="json-index">${i}:</span>
                                ${this.renderJsonTree(item, level + 1)}
                            </div>
                        `).join('')}
                    </div>
                    <span class="json-bracket">]</span>
                </div>
            `;
        }
        
        if (typeof obj === 'object') {
            const keys = Object.keys(obj);
            if (keys.length === 0) return '<span class="json-object">{}</span>';
            
            return `
                <div class="json-object">
                    <span class="json-bracket">{</span>
                    <div class="json-properties">
                        ${keys.map(key => `
                            <div class="json-property">
                                <span class="json-key">"${key}":</span>
                                ${this.renderJsonTree(obj[key], level + 1)}
                            </div>
                        `).join('')}
                    </div>
                    <span class="json-bracket">}</span>
                </div>
            `;
        }
        
        return String(obj);
    }

    updateStats() {
        const editor = this.container.querySelector('#json-editor-textarea');
        const charCount = this.container.querySelector('#char-count');
        const lineCount = this.container.querySelector('#line-count');
        
        charCount.textContent = `${editor.value.length} caracteres`;
        lineCount.textContent = `${editor.value.split('\n').length} líneas`;
    }

    formatJson() {
        const editor = this.container.querySelector('#json-editor-textarea');
        try {
            const json = JSON.parse(editor.value);
            editor.value = JSON.stringify(json, null, 2);
            
            this.updateLineNumbers();
            this.validateAndPreview();
            this.updateStats();
            this.showStatus('JSON formateado correctamente', 'success');
            
        } catch (error) {
            this.showStatus('Error: JSON inválido', 'error');
        }
    }

    async saveJson(isAutoSave = false) {
        const editor = this.container.querySelector('#json-editor-textarea');
        
        try {
            const content = JSON.parse(editor.value);
            const response = await fetch(`${this.endpoint}/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: 1, // Siempre usar ID 1 para un único JSON
                    name: 'configuracion_principal',
                    content: content
                })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                this.hasChanges = false;
                this.showStatus(
                    isAutoSave ? 'Guardado automático' : 'Guardado correctamente', 
                    'success'
                );
            }
        } catch (error) {
            this.showStatus('Error al guardar: JSON inválido', 'error');
        }
    }

    showStatus(message, type) {
        const status = this.container.querySelector('#status-message');
        status.textContent = message;
        status.className = `status-message ${type}`;
        
        setTimeout(() => {
            status.classList.add('fade-out');
            setTimeout(() => {
                status.textContent = '';
                status.className = 'status-message';
            }, 300);
        }, 3000);
    }

    destroy() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
        super.destroy();
    }
}

window.ModuleRegistry.register(JsonEditorModule);