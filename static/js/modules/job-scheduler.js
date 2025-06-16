// static/js/modules/job-scheduler.js
class JobSchedulerModule extends BaseModule {
    constructor() {
        super({
            id: 'job-scheduler',
            name: 'Job Scheduler',
            icon: 'fas fa-clock',
            color: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
            endpoint: '/api/job-scheduler',
            description: 'Gestión y programación de scripts automáticos',
            size: 'large',
            refreshInterval: 30000 // Actualizar cada 30 segundos
        });
        
        this.selectedJob = null;
        this.jobs = [];
        this.scheduledJobs = [];
    }

    async init(container) {
        this.container = container;
        this.loadModuleCSS();
        await this.loadData();
        await this.loadJobs();
        this.render();
    }

    async loadJobs() {
        try {
            const response = await fetch(`${this.endpoint}/jobs`);
            this.jobs = await response.json();
            
            // Cargar jobs programados
            const scheduledResponse = await fetch(`${this.endpoint}/scheduled`);
            this.scheduledJobs = await scheduledResponse.json();
        } catch (error) {
            console.error('Error cargando jobs:', error);
        }
    }

    async loadJobConfig(jobId) {
        try {
            const response = await fetch(`${this.endpoint}/jobs/${jobId}`);
            return await response.json();
        } catch (error) {
            console.error('Error cargando configuración:', error);
            return null;
        }
    }

    getTemplate() {
        return `
            <div class="job-scheduler-container">
                <!-- Panel lateral de jobs -->
                <div class="jobs-sidebar">
                    <div class="sidebar-header">
                        <h3><i class="fas fa-list"></i> Jobs Disponibles</h3>
                        <span class="jobs-count">${this.jobs.length} jobs</span>
                    </div>
                    <div class="jobs-list">
                        ${this.jobs.map(job => `
                            <div class="job-item ${this.selectedJob?.job_id === job.job_id ? 'active' : ''}" 
                                 onclick="jobScheduler.selectJob('${job.job_id}')">
                                <div class="job-icon">
                                    <i class="fas fa-code"></i>
                                </div>
                                <div class="job-info">
                                    <h4>${job.name}</h4>
                                    <p>${job.description}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Panel principal -->
                <div class="job-main-panel">
                    ${this.selectedJob ? this.getJobDetailTemplate() : this.getDashboardTemplate()}
                </div>
            </div>
        `;
    }

    getDashboardTemplate() {
        return `
            <div class="job-dashboard">
                <div class="dashboard-header">
                    <h2><i class="fas fa-tachometer-alt"></i> Dashboard de Jobs</h2>
                    <p>Selecciona un job del panel lateral para configurarlo</p>
                </div>
                
                <!-- Jobs activos -->
                <div class="scheduled-jobs-section">
                    <h3><i class="fas fa-calendar-alt"></i> Jobs Activos</h3>
                    <div class="scheduled-jobs-grid">
                        ${this.scheduledJobs.length > 0 ? 
                            this.scheduledJobs.map(job => `
                                <div class="scheduled-job-card ${job.is_active ? '' : 'inactive'}" 
                                     onclick="jobScheduler.selectJob('${job.job_id}')">
                                    <div class="job-header">
                                        <h4>${job.job_name}</h4>
                                        <span class="job-status ${job.last_status || 'pending'}">${job.last_status || 'pendiente'}</span>
                                    </div>
                                    <div class="job-schedule">
                                        <i class="fas fa-clock"></i>
                                        <span>${this.getScheduleDescription(job.schedule_type, job.schedule_value)}</span>
                                    </div>
                                    <div class="job-times">
                                        ${job.last_run ? `
                                            <div class="time-info">
                                                <label>Última ejecución:</label>
                                                <span>${this.formatDateTime(job.last_run)}</span>
                                            </div>
                                        ` : ''}
                                        ${job.next_run && job.schedule_type !== 'manual' ? `
                                            <div class="time-info">
                                                <label>Próxima ejecución:</label>
                                                <span>${this.formatDateTime(job.next_run)}</span>
                                            </div>
                                        ` : ''}
                                    </div>
                                </div>
                            `).join('')
                            :
                            '<p class="no-scheduled">No hay jobs configurados</p>'
                        }
                    </div>
                </div>
            </div>
        `;
    }

    getJobDetailTemplate() {
        const job = this.selectedJob;
        if (!job) return '';
        
        return `
            <div class="job-detail">
                <div class="job-detail-header">
                    <div class="header-info">
                        <h2><i class="fas fa-code"></i> ${job.job_name}</h2>
                        <p>${job.description}</p>
                    </div>
                    <div class="header-actions">
                        <button class="btn btn-primary" onclick="jobScheduler.executeJob()">
                            <i class="fas fa-play"></i> Ejecutar Ahora
                        </button>
                        <button class="btn btn-success" onclick="jobScheduler.saveConfig()">
                            <i class="fas fa-save"></i> Guardar
                        </button>
                    </div>
                </div>
                
                <div class="job-detail-content">
                    <!-- Estado actual -->
                    ${job.last_run ? `
                        <div class="status-section">
                            <h3><i class="fas fa-info-circle"></i> Última Ejecución</h3>
                            <div class="status-info">
                                <div class="status-row">
                                    <span>Estado:</span>
                                    <span class="job-status ${job.last_status || 'pending'}">${job.last_status || 'Sin ejecutar'}</span>
                                </div>
                                <div class="status-row">
                                    <span>Fecha:</span>
                                    <span>${this.formatDateTime(job.last_run)}</span>
                                </div>
                                ${job.last_output ? `
                                    <div class="status-output">
                                        <button class="btn-small" onclick="jobScheduler.showLastOutput()">
                                            <i class="fas fa-terminal"></i> Ver salida
                                        </button>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    ` : ''}
                    
                    <!-- Configuración del Job -->
                    <div class="config-section">
                        <h3><i class="fas fa-cog"></i> Configuración del Job</h3>
                        
                        <!-- Editor JSON -->
                        <div class="json-editor-wrapper">
                            <div class="editor-header">
                                <span>Configuración JSON</span>
                                <div class="editor-actions">
                                    <button class="btn-small" onclick="jobScheduler.formatJson()">
                                        <i class="fas fa-magic"></i> Formatear
                                    </button>
                                    <button class="btn-small" onclick="jobScheduler.resetConfig()">
                                        <i class="fas fa-undo"></i> Restaurar
                                    </button>
                                </div>
                            </div>
                            <textarea id="job-config-editor" class="json-editor" rows="10">${job.config_json || '{}'}</textarea>
                        </div>
                        
                        <!-- Programación -->
                        <div class="schedule-config">
                            <h4><i class="fas fa-clock"></i> Programación</h4>
                            <div class="schedule-options">
                                <div class="form-group">
                                    <label>Tipo de programación:</label>
                                    <select id="schedule-type" onchange="jobScheduler.onScheduleTypeChange()">
                                        <option value="manual" ${job.schedule_type === 'manual' ? 'selected' : ''}>Manual</option>
                                        <option value="interval" ${job.schedule_type === 'interval' ? 'selected' : ''}>Intervalo</option>
                                        <option value="cron" ${job.schedule_type === 'cron' ? 'selected' : ''}>Cron</option>
                                        <option value="daily" ${job.schedule_type === 'daily' ? 'selected' : ''}>Diario</option>
                                        <option value="weekly" ${job.schedule_type === 'weekly' ? 'selected' : ''}>Semanal</option>
                                    </select>
                                </div>
                                
                                <div id="schedule-value-group" class="form-group" style="display: ${job.schedule_type === 'interval' || job.schedule_type === 'cron' ? 'block' : 'none'}">
                                    <label id="schedule-value-label">
                                        ${job.schedule_type === 'interval' ? 'Intervalo (minutos):' : 'Expresión Cron:'}
                                    </label>
                                    <input type="text" id="schedule-value" value="${job.schedule_value || ''}" 
                                           placeholder="${job.schedule_type === 'interval' ? '60' : '0 * * * *'}">
                                    ${job.schedule_type === 'cron' ? '<small>Formato: minuto hora día mes día_semana</small>' : ''}
                                </div>
                                
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="is-active" ${job.is_active ? 'checked' : ''}>
                                        <span>Job activo</span>
                                    </label>
                                </div>
                                
                                ${job.next_run && job.schedule_type !== 'manual' ? `
                                    <div class="next-run-info">
                                        <i class="fas fa-calendar-check"></i>
                                        Próxima ejecución: ${this.formatDateTime(job.next_run)}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async selectJob(jobId) {
        const jobInfo = this.jobs.find(j => j.job_id === jobId);
        if (!jobInfo) return;
        
        // Cargar configuración completa
        const config = await this.loadJobConfig(jobId);
        if (config) {
            this.selectedJob = { ...jobInfo, ...config };
            this.render();
        }
    }

    async executeJob() {
        if (!this.selectedJob) return;
        
        const config = document.getElementById('job-config-editor')?.value;
        
        try {
            const response = await fetch(`${this.endpoint}/jobs/${this.selectedJob.job_id}/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_id: this.selectedJob.job_id,
                    config_json: config
                })
            });
            
            const result = await response.json();
            if (result.status === 'started') {
                this.showNotification('Job iniciado correctamente', 'success');
                
                // Recargar estado después de 3 segundos
                setTimeout(() => {
                    this.loadJobConfig(this.selectedJob.job_id).then(config => {
                        if (config) {
                            this.selectedJob = { ...this.selectedJob, ...config };
                            this.render();
                        }
                    });
                }, 3000);
            }
        } catch (error) {
            this.showNotification('Error ejecutando job', 'error');
        }
    }

    async saveConfig() {
        if (!this.selectedJob) return;
        
        const config = document.getElementById('job-config-editor')?.value;
        const scheduleType = document.getElementById('schedule-type')?.value;
        const scheduleValue = document.getElementById('schedule-value')?.value;
        const isActive = document.getElementById('is-active')?.checked;
        
        try {
            // Validar JSON
            JSON.parse(config);
            
            const response = await fetch(`${this.endpoint}/jobs/${this.selectedJob.job_id}/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_id: this.selectedJob.job_id,
                    config_json: config,
                    schedule_type: scheduleType,
                    schedule_value: scheduleValue,
                    is_active: isActive
                })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                this.showNotification('Configuración guardada', 'success');
                
                // Actualizar job seleccionado
                this.selectedJob.config_json = config;
                this.selectedJob.schedule_type = scheduleType;
                this.selectedJob.schedule_value = scheduleValue;
                this.selectedJob.is_active = isActive;
                
                // Recargar jobs programados
                await this.loadJobs();
                this.render();
            }
        } catch (error) {
            if (error instanceof SyntaxError) {
                this.showNotification('JSON inválido', 'error');
            } else {
                this.showNotification('Error guardando configuración', 'error');
            }
        }
    }

    formatJson() {
        const editor = document.getElementById('job-config-editor');
        if (!editor) return;
        
        try {
            const json = JSON.parse(editor.value);
            editor.value = JSON.stringify(json, null, 2);
        } catch (error) {
            this.showNotification('JSON inválido', 'error');
        }
    }

    resetConfig() {
        if (!this.selectedJob) return;
        
        const defaultConfig = this.jobs.find(j => j.job_id === this.selectedJob.job_id)?.default_config;
        if (defaultConfig) {
            document.getElementById('job-config-editor').value = JSON.stringify(defaultConfig, null, 2);
        }
    }

    onScheduleTypeChange() {
        const type = document.getElementById('schedule-type').value;
        const valueGroup = document.getElementById('schedule-value-group');
        const valueLabel = document.getElementById('schedule-value-label');
        const valueInput = document.getElementById('schedule-value');
        
        if (type === 'interval') {
            valueGroup.style.display = 'block';
            valueLabel.textContent = 'Intervalo (minutos):';
            valueInput.placeholder = '60';
        } else if (type === 'cron') {
            valueGroup.style.display = 'block';
            valueLabel.textContent = 'Expresión Cron:';
            valueInput.placeholder = '0 * * * *';
        } else {
            valueGroup.style.display = 'none';
        }
    }

    showLastOutput() {
        if (!this.selectedJob?.last_output) return;
        
        try {
            const output = JSON.parse(this.selectedJob.last_output);
            const message = `Última ejecución: ${output.status}\n` +
                           `Fecha: ${output.timestamp}\n` +
                           `Duración: ${output.duration_seconds}s\n\n` +
                           (output.summary ? `Salida:\n${output.summary}` : '') +
                           (output.error ? `\nError: ${output.error}` : '');
            
            alert(message);
        } catch (error) {
            alert('Error mostrando salida');
        }
    }

    getScheduleDescription(type, value) {
        switch (type) {
            case 'manual': return 'Ejecución manual';
            case 'interval': return `Cada ${value} minutos`;
            case 'cron': return `Cron: ${value}`;
            case 'daily': return 'Diariamente';
            case 'weekly': return 'Semanalmente';
            default: return type;
        }
    }

    formatDateTime(dateStr) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    showNotification(message, type) {
        // Simple notificación con estilo
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => notification.classList.add('show'), 10);
        
        // Remover después de 3 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    afterRender() {
        window.jobScheduler = this;
    }

    async refresh() {
        await this.loadJobs();
        if (this.selectedJob) {
            const config = await this.loadJobConfig(this.selectedJob.job_id);
            if (config) {
                this.selectedJob = { ...this.selectedJob, ...config };
            }
        }
        this.render();
    }
}

// Registrar el módulo
window.ModuleRegistry.register(JobSchedulerModule);