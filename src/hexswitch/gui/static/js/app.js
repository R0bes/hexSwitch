// HexSwitch Admin GUI JavaScript

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.getAttribute('data-tab');
        
        // Update button states
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Update content visibility
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');
        
        // Load data for active tab
        loadTabData(tabName);
    });
});

// Load data for a specific tab
async function loadTabData(tabName) {
    switch(tabName) {
        case 'overview':
            await loadOverview();
            break;
        case 'ports':
            await loadPorts();
            break;
        case 'handlers':
            await loadHandlers();
            break;
        case 'adapters':
            await loadAdapters();
            break;
        case 'metrics':
            await loadMetrics();
            break;
    }
}

// Load overview data
async function loadOverview() {
    try {
        const [healthRes, adaptersRes, portsRes, handlersRes] = await Promise.all([
            fetch('/api/health'),
            fetch('/api/adapters'),
            fetch('/api/ports'),
            fetch('/api/handlers')
        ]);

        const health = await healthRes.json();
        const adapters = await adaptersRes.json();
        const ports = await portsRes.json();
        const handlers = await handlersRes.json();

        // Update health status
        const healthStatus = document.getElementById('health-status');
        healthStatus.textContent = health.status || 'unknown';
        healthStatus.className = 'status-indicator ' + (health.status === 'healthy' ? 'healthy' : 'unhealthy');

        // Update counts
        document.getElementById('adapter-count').textContent = adapters.adapters?.length || 0;
        document.getElementById('port-count').textContent = ports.ports?.length || 0;
        document.getElementById('handler-count').textContent = handlers.handlers?.length || 0;
    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

// Load ports
async function loadPorts() {
    try {
        const response = await fetch('/api/ports');
        const data = await response.json();
        const portsList = document.getElementById('ports-list');
        
        if (data.ports && data.ports.length > 0) {
            portsList.innerHTML = data.ports.map(port => `
                <div class="data-item">
                    <h4>${port.name || 'Unknown'}</h4>
                    <p>Type: ${port.type || 'N/A'}</p>
                </div>
            `).join('');
        } else {
            portsList.innerHTML = '<p>No ports registered</p>';
        }
    } catch (error) {
        console.error('Error loading ports:', error);
        document.getElementById('ports-list').innerHTML = '<p>Error loading ports</p>';
    }
}

// Load handlers
async function loadHandlers() {
    try {
        const response = await fetch('/api/handlers');
        const data = await response.json();
        const handlersList = document.getElementById('handlers-list');
        
        if (data.handlers && data.handlers.length > 0) {
            handlersList.innerHTML = data.handlers.map(handler => `
                <div class="data-item">
                    <h4>${handler.name || 'Unknown'}</h4>
                    <p>Port: ${handler.port || 'N/A'}</p>
                </div>
            `).join('');
        } else {
            handlersList.innerHTML = '<p>No handlers registered</p>';
        }
    } catch (error) {
        console.error('Error loading handlers:', error);
        document.getElementById('handlers-list').innerHTML = '<p>Error loading handlers</p>';
    }
}

// Load adapters
async function loadAdapters() {
    try {
        const response = await fetch('/api/adapters');
        const data = await response.json();
        const adaptersList = document.getElementById('adapters-list');
        
        if (data.adapters && data.adapters.length > 0) {
            adaptersList.innerHTML = data.adapters.map(adapter => `
                <div class="data-item">
                    <h4>${adapter.name || 'Unknown'}</h4>
                    <p>Type: ${adapter.type || 'N/A'}</p>
                    <p>Status: ${adapter.running || adapter.connected ? 'Active' : 'Inactive'}</p>
                </div>
            `).join('');
        } else {
            adaptersList.innerHTML = '<p>No adapters configured</p>';
        }
    } catch (error) {
        console.error('Error loading adapters:', error);
        document.getElementById('adapters-list').innerHTML = '<p>Error loading adapters</p>';
    }
}

// Load metrics
async function loadMetrics() {
    try {
        const response = await fetch('/api/metrics');
        const data = await response.json();
        const metricsContent = document.getElementById('metrics-content');
        
        metricsContent.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        console.error('Error loading metrics:', error);
        document.getElementById('metrics-content').textContent = 'Error loading metrics';
    }
}

// Auto-refresh overview every 5 seconds
setInterval(() => {
    if (document.getElementById('overview').classList.contains('active')) {
        loadOverview();
    }
}, 5000);

// Initial load
loadTabData('overview');

