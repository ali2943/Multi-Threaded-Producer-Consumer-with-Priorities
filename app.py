"""
Flask Web API for Multi-Threaded Producer-Consumer System
Provides REST API and WebSocket for real-time monitoring
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
from producer_consumer import PriorityBuffer, Producer, Consumer, Priority, PriorityItem

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
buffer = None
producers = []
consumers = []
system_running = False
monitor_thread = None


def monitor_buffer():
    """Monitor buffer and emit updates via WebSocket"""
    global buffer, system_running
    
    while system_running:
        if buffer:
            stats = buffer.get_stats()
            socketio.emit('buffer_update', stats)
        time.sleep(0.5)


@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status"""
    global buffer, producers, consumers, system_running
    
    status = {
        'running': system_running,
        'num_producers': len(producers),
        'num_consumers': len(consumers),
        'active_producers': sum(1 for p in producers if p.is_alive()),
        'active_consumers': sum(1 for c in consumers if c.is_alive()),
    }
    
    if buffer:
        status['buffer'] = buffer.get_stats()
    
    return jsonify(status)


@app.route('/api/start', methods=['POST'])
def start_system():
    """Start the producer-consumer system"""
    global buffer, producers, consumers, system_running, monitor_thread
    
    if system_running:
        return jsonify({'error': 'System already running'}), 400
    
    data = request.json or {}
    num_producers = data.get('num_producers', 2)
    num_consumers = data.get('num_consumers', 3)
    items_per_producer = data.get('items_per_producer', 20)
    buffer_size = data.get('buffer_size', 10)
    
    # Create buffer
    buffer = PriorityBuffer(max_size=buffer_size)
    
    # Create and start producers
    producers = []
    for i in range(num_producers):
        producer = Producer(i + 1, buffer, num_items=items_per_producer)
        producers.append(producer)
        producer.start()
    
    # Create and start consumers
    consumers = []
    for i in range(num_consumers):
        consumer = Consumer(i + 1, buffer)
        consumers.append(consumer)
        consumer.start()
    
    system_running = True
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_buffer, daemon=True)
    monitor_thread.start()
    
    return jsonify({
        'message': 'System started',
        'config': {
            'num_producers': num_producers,
            'num_consumers': num_consumers,
            'items_per_producer': items_per_producer,
            'buffer_size': buffer_size
        }
    })


@app.route('/api/stop', methods=['POST'])
def stop_system():
    """Stop the producer-consumer system"""
    global producers, consumers, system_running
    
    if not system_running:
        return jsonify({'error': 'System not running'}), 400
    
    # Stop all producers
    for producer in producers:
        producer.stop()
    
    # Stop all consumers
    for consumer in consumers:
        consumer.stop()
    
    system_running = False
    
    return jsonify({'message': 'System stopped'})


@app.route('/api/add_item', methods=['POST'])
def add_item():
    """Manually add an item to the buffer"""
    global buffer
    
    if not buffer:
        return jsonify({'error': 'System not initialized'}), 400
    
    data = request.json or {}
    priority_name = data.get('priority', 'MEDIUM')
    item_data = data.get('data', 'Manual item')
    
    try:
        priority = Priority[priority_name]
        item = PriorityItem(
            priority=priority.value,
            item_id=-1,  # Manual items have negative IDs
            data=item_data
        )
        
        # Add to buffer in a separate thread to avoid blocking
        threading.Thread(target=buffer.produce, args=(item,), daemon=True).start()
        
        return jsonify({
            'message': 'Item added',
            'item': {
                'priority': priority_name,
                'data': item_data
            }
        })
    except KeyError:
        return jsonify({'error': f'Invalid priority: {priority_name}'}), 400


@app.route('/api/priorities', methods=['GET'])
def get_priorities():
    """Get available priority levels"""
    return jsonify({
        'priorities': [p.name for p in Priority]
    })


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print('Client connected')
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print('Client disconnected')


def main():
    """Run the Flask application"""
    print("Starting Producer-Consumer Web API...")
    print("Navigate to http://localhost:5000 in your browser")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()
