// static/js/modules/example.js
class ExampleModule extends BaseModule {
    constructor() {
        super({
            id: 'example',
            name: 'Ejemplo',
            icon: 'fas fa-chart-line',
            color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            endpoint: '/api/example',
            description: 'Módulo de demostración',
            size: 'medium',
            refreshInterval: 30000 // 30 segundos
        });
    }

    getTemplate() {
        if (!this.data) return '<div class="loading"></div>';
        
        return `
            <div class="example-module">
                <h3>${this.data.title}</h3>
                
                <div class="metrics-grid">
                    <div class="metric-box">
                        <div class="metric-value">${this.formatNumber(this.data.metrics.valor1)}</div>
                        <div class="metric-label">Métrica 1</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-value">${this.formatNumber(this.data.metrics.valor2)}</div>
                        <div class="metric-label">Métrica 2</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-value">${this.data.metrics.valor3}</div>
                        <div class="metric-label">Porcentaje</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-value">${this.data.metrics.valor4}</div>
                        <div class="metric-label">Tiempo</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <canvas id="example-chart"></canvas>
                </div>
                
                <div class="status-bar ${this.data.status.code}">
                    <i class="fas fa-check-circle"></i>
                    <span>${this.data.status.message}</span>
                </div>
            </div>
        `;
    }

    afterRender() {
        this.drawChart();
    }

    drawChart() {
        const canvas = this.container.querySelector('#example-chart');
        if (!canvas || !this.data.chart_data) return;
        
        const ctx = canvas.getContext('2d');
        const data = this.data.chart_data;
        
        // Configurar canvas
        canvas.width = canvas.offsetWidth;
        canvas.height = 200;
        
        const width = canvas.width;
        const height = canvas.height;
        const padding = 20;
        const barWidth = (width - padding * 2) / data.labels.length;
        
        // Limpiar canvas
        ctx.clearRect(0, 0, width, height);
        
        // Encontrar valor máximo
        const maxValue = Math.max(...data.values);
        
        // Dibujar barras
        data.values.forEach((value, index) => {
            const barHeight = (value / maxValue) * (height - padding * 2);
            const x = padding + index * barWidth + barWidth * 0.1;
            const y = height - padding - barHeight;
            const w = barWidth * 0.8;
            
            // Gradiente para las barras
            const gradient = ctx.createLinearGradient(0, y, 0, height - padding);
            gradient.addColorStop(0, '#667eea');
            gradient.addColorStop(1, '#764ba2');
            
            ctx.fillStyle = gradient;
            ctx.fillRect(x, y, w, barHeight);
            
            // Etiquetas
            ctx.fillStyle = '#999';
            ctx.font = '12px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(data.labels[index], x + w/2, height - 5);
            
            // Valores
            ctx.fillStyle = '#fff';
            ctx.fillText(value, x + w/2, y - 5);
        });
    }
}

// Registrar el módulo
window.ModuleRegistry.register(ExampleModule);