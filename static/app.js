// WebSocket connection
let socket;
let systemRunning = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    setupEventListeners();
    updateStatus();
});

// Initialize WebSocket connection
function initializeWebSocket() {
    socket = io();
    
    socket.on('connect', function() {
        addLog('WebSocket connected', 'success');
    });
    
    socket.on('disconnect', function() {
        addLog('WebSocket disconnected', 'warning');
    });
    
    socket.on('buffer_update', function(data) {
        updateBufferStats(data);
    });
    
    socket.on('connection_response', function(data) {
        console.log('Connection response:', data);
    });
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('startBtn').addEventListener('click', startSystem);
    document.getElementById('stopBtn').addEventListener('click', stopSystem);
    document.getElementById('addItemBtn').addEventListener('click', addManualItem);
    
    // Enable Enter key for manual item
    document.getElementById('itemData').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addManualItem();
        }
    });
}

// Start the system
async function startSystem() {
    const config = {
        num_producers: parseInt(document.getElementById('numProducers').value),
        num_consumers: parseInt(document.getElementById('numConsumers').value),
        items_per_producer: parseInt(document.getElementById('itemsPerProducer').value),
        buffer_size: parseInt(document.getElementById('bufferSize').value)
    };
    
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            systemRunning = true;
            updateControlPanel(true);
            addLog(`System started: ${config.num_producers} producers, ${config.num_consumers} consumers`, 'success');
        } else {
            addLog(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog(`Failed to start system: ${error.message}`, 'error');
    }
}

// Stop the system
async function stopSystem() {
    try {
        const response = await fetch('/api/stop', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            systemRunning = false;
            updateControlPanel(false);
            addLog('System stopped', 'info');
        } else {
            addLog(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog(`Failed to stop system: ${error.message}`, 'error');
    }
}

// Add manual item
async function addManualItem() {
    const priority = document.getElementById('itemPriority').value;
    const data = document.getElementById('itemData').value;
    
    if (!data.trim()) {
        addLog('Please enter item data', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/add_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ priority, data })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            addLog(`Manual item added: ${data} (${priority})`, 'success');
            document.getElementById('itemData').value = '';
        } else {
            addLog(`Error: ${result.error}`, 'error');
        }
    } catch (error) {
        addLog(`Failed to add item: ${error.message}`, 'error');
    }
}

// Update system status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        systemRunning = data.running;
        updateControlPanel(data.running);
        
        if (data.buffer) {
            updateBufferStats(data.buffer);
        }
        
        // Update thread counts
        document.getElementById('totalProducers').textContent = data.num_producers || 0;
        document.getElementById('activeProducers').textContent = data.active_producers || 0;
        document.getElementById('totalConsumers').textContent = data.num_consumers || 0;
        document.getElementById('activeConsumers').textContent = data.active_consumers || 0;
        
    } catch (error) {
        console.error('Failed to update status:', error);
    }
    
    // Poll status every 2 seconds
    setTimeout(updateStatus, 2000);
}

// Update control panel UI
function updateControlPanel(running) {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const statusBadge = document.getElementById('systemStatus');
    
    if (running) {
        startBtn.disabled = true;
        stopBtn.disabled = false;
        statusBadge.textContent = 'RUNNING';
        statusBadge.className = 'status-badge running pulsing';
        
        // Disable config inputs
        document.getElementById('numProducers').disabled = true;
        document.getElementById('numConsumers').disabled = true;
        document.getElementById('itemsPerProducer').disabled = true;
        document.getElementById('bufferSize').disabled = true;
    } else {
        startBtn.disabled = false;
        stopBtn.disabled = true;
        statusBadge.textContent = 'STOPPED';
        statusBadge.className = 'status-badge stopped';
        
        // Enable config inputs
        document.getElementById('numProducers').disabled = false;
        document.getElementById('numConsumers').disabled = false;
        document.getElementById('itemsPerProducer').disabled = false;
        document.getElementById('bufferSize').disabled = false;
    }
}

// Update buffer statistics
function updateBufferStats(data) {
    // Update basic stats
    document.getElementById('bufferSize').textContent = data.size || 0;
    document.getElementById('bufferMax').textContent = data.max_size || 0;
    document.getElementById('totalProduced').textContent = data.total_produced || 0;
    document.getElementById('totalConsumed').textContent = data.total_consumed || 0;
    
    // Update buffer visual
    const maxSize = data.max_size || 1;
    const currentSize = data.size || 0;
    const percentage = Math.round((currentSize / maxSize) * 100);
    
    document.getElementById('bufferBar').style.width = percentage + '%';
    document.getElementById('bufferPercent').textContent = percentage + '%';
    
    // Update priority distribution
    if (data.items_by_priority) {
        updatePriorityChart(data.items_by_priority);
    }
}

// Update priority chart
function updatePriorityChart(items) {
    const priorities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
    const total = Object.values(items).reduce((sum, val) => sum + val, 0) || 1;
    
    priorities.forEach(priority => {
        const count = items[priority] || 0;
        const percentage = Math.round((count / total) * 100);
        
        document.getElementById('priority' + priority.charAt(0) + priority.slice(1).toLowerCase()).style.width = percentage + '%';
        document.getElementById('count' + priority.charAt(0) + priority.slice(1).toLowerCase()).textContent = count;
    });
}

// Add log entry
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('logContainer');
    const timestamp = new Date().toLocaleTimeString();
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.textContent = `[${timestamp}] ${message}`;
    
    logContainer.appendChild(logEntry);
    
    // Auto-scroll to bottom
    logContainer.scrollTop = logContainer.scrollHeight;
    
    // Keep only last 100 entries
    while (logContainer.children.length > 100) {
        logContainer.removeChild(logContainer.firstChild);
    }
}

// Utility function to format numbers
function formatNumber(num) {
    return num.toLocaleString();
}
