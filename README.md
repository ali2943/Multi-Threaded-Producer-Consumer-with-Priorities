# Multi-Threaded Producer-Consumer with Priorities

A sophisticated implementation of the classic producer-consumer problem using Python's threading and semaphores, with a priority queue for task management. Includes a real-time web dashboard built with Flask, HTML, CSS, and JavaScript.

## 🌟 Features

- **Priority-Based Processing**: Items are consumed in order of priority (CRITICAL → HIGH → MEDIUM → LOW)
- **Thread Synchronization**: Uses semaphores for thread-safe operations
- **Bounded Buffer**: Implements a size-limited queue to prevent resource exhaustion
- **Real-Time Monitoring**: WebSocket-based live updates of system state
- **Web Dashboard**: Interactive UI to control and monitor the system
- **Manual Item Injection**: Add items to the queue with custom priorities
- **Statistics Tracking**: Comprehensive metrics on production, consumption, and priority distribution

## 📋 Key Concepts Demonstrated

- **Semaphores**: For synchronizing access to the bounded buffer
- **Priority Queue**: High-priority items are consumed first
- **Multithreading**: Multiple producers and consumers running concurrently
- **Bounded Buffer**: Fixed-size queue with blocking operations
- **Producer-Consumer Pattern**: Classic concurrency problem solution

## 🛠️ Technology Stack

- **Backend**: Python 3.x
  - Threading & Semaphores
  - Flask (Web Framework)
  - Flask-SocketIO (WebSocket Support)
  - Priority Queue (heapq-based)
  
- **Frontend**: 
  - HTML5
  - CSS3 (with Flexbox & Grid)
  - JavaScript (ES6+)
  - Socket.IO (Real-time Communication)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/ali2943/Multi-Threaded-Producer-Consumer-with-Priorities.git
cd Multi-Threaded-Producer-Consumer-with-Priorities
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Command-Line Mode

Run the standalone producer-consumer simulation:

```bash
python producer_consumer.py
```

This will run a demo with:
- 2 Producers
- 3 Consumers
- 10 items per producer
- Buffer size of 10

### Web Dashboard Mode

1. Start the Flask web server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Use the web interface to:
   - Configure number of producers and consumers
   - Set buffer size and items per producer
   - Start/stop the system
   - Add manual items with custom priorities
   - Monitor real-time statistics and buffer state

## 🎮 Web Dashboard Controls

### Control Panel
- **Producers**: Number of producer threads (1-10)
- **Consumers**: Number of consumer threads (1-10)
- **Items/Producer**: How many items each producer generates (1-100)
- **Buffer Size**: Maximum queue capacity (1-50)

### Real-Time Monitoring
- **Buffer Occupancy**: Visual representation of buffer fullness
- **Priority Distribution**: Chart showing items by priority level
- **Thread Status**: Active/total producers and consumers
- **System Log**: Timestamped event log

### Manual Item Addition
Add custom items to the queue while the system is running:
- Select priority level (CRITICAL, HIGH, MEDIUM, LOW)
- Enter item data
- Click "Add Item"

## 🏗️ Architecture

### Core Components

1. **PriorityItem**: Data class representing a task with priority
2. **PriorityBuffer**: Thread-safe bounded buffer with semaphores
   - `empty_slots`: Semaphore tracking available buffer space
   - `filled_slots`: Semaphore tracking items ready for consumption
   - `mutex`: Lock for thread-safe operations
   
3. **Producer**: Thread that generates items with random priorities
4. **Consumer**: Thread that processes items starting with highest priority

### Synchronization Mechanism

```
Producer:                    Buffer:                     Consumer:
   |                           |                            |
   | acquire(empty_slots) ---> |                            |
   | lock(mutex)               |                            |
   | buffer.put(item)          |                            |
   | unlock(mutex)             |                            |
   | release(filled_slots) --> | <--- acquire(filled_slots) |
   |                           |      lock(mutex)           |
   |                           |      item = buffer.get()   |
   |                           |      unlock(mutex)         |
   |                           | <--- release(empty_slots)  |
```

### Web API Endpoints

- `GET /api/status` - Get current system state
- `POST /api/start` - Start the producer-consumer system
- `POST /api/stop` - Stop the system
- `POST /api/add_item` - Add a manual item to the queue
- `GET /api/priorities` - Get available priority levels

### WebSocket Events

- `buffer_update` - Real-time buffer statistics (emitted every 0.5s)
- `connect` - Client connection established
- `disconnect` - Client disconnected

## 📊 Priority Levels

| Priority  | Value | Color    | Description              |
|-----------|-------|----------|--------------------------|
| CRITICAL  | 1     | Red      | Highest priority         |
| HIGH      | 2     | Orange   | High priority            |
| MEDIUM    | 3     | Yellow   | Medium priority          |
| LOW       | 4     | Green    | Lowest priority          |

Items with lower priority values are consumed first.

## 🔍 Example Output

```
[PRODUCER 1] Produced: Producer-1-Item-0 (Priority: HIGH)
[PRODUCER 2] Produced: Producer-2-Item-0 (Priority: CRITICAL)
[CONSUMER 1] Consuming: Producer-2-Item-0 (Priority: CRITICAL, Wait: 0.05s)
[CONSUMER 2] Consuming: Producer-1-Item-0 (Priority: HIGH, Wait: 0.12s)
[CONSUMER 1] Finished: Producer-2-Item-0
[PRODUCER 1] Produced: Producer-1-Item-1 (Priority: MEDIUM)
...
```

## 🧪 Testing

The system demonstrates:
- Thread-safe operations with semaphores
- Priority-based consumption
- Blocking behavior when buffer is full/empty
- Concurrent producer-consumer execution
- Real-time statistics tracking

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 👨‍💻 Author

**Ali**

## 📚 References

- [Producer-Consumer Problem](https://en.wikipedia.org/wiki/Producer%E2%80%93consumer_problem)
- [Semaphores in Python](https://docs.python.org/3/library/threading.html#semaphore-objects)
- [Priority Queue](https://docs.python.org/3/library/queue.html#queue.PriorityQueue)
