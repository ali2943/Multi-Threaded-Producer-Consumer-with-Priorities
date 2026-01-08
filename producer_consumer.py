"""
Multi-Threaded Producer-Consumer with Priorities
Uses semaphores, bounded buffer, and priority queue
"""

import threading
import time
import queue
import random
from dataclasses import dataclass
from typing import List
from enum import IntEnum


class Priority(IntEnum):
    """Priority levels for items (lower value = higher priority)"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass(order=True)
class PriorityItem:
    """Item with priority for the queue"""
    priority: int
    item_id: int
    data: str
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class PriorityBuffer:
    """Bounded buffer with priority queue and semaphore synchronization"""
    
    def __init__(self, max_size=10):
        self.max_size = max_size
        self.buffer = queue.PriorityQueue(maxsize=max_size)
        
        # Semaphores for synchronization
        self.empty_slots = threading.Semaphore(max_size)  # Available slots
        self.filled_slots = threading.Semaphore(0)  # Items available to consume
        self.mutex = threading.Lock()  # For thread-safe operations
        
        # Statistics
        self.total_produced = 0
        self.total_consumed = 0
        self.items_by_priority = {p: 0 for p in Priority}
        
    def produce(self, item: PriorityItem):
        """Add item to buffer (blocks if full)"""
        self.empty_slots.acquire()  # Wait for empty slot
        
        with self.mutex:
            self.buffer.put(item)
            self.total_produced += 1
            if item.priority in Priority:
                self.items_by_priority[Priority(item.priority)] += 1
        
        self.filled_slots.release()  # Signal item available
        
    def consume(self) -> PriorityItem:
        """Remove highest priority item from buffer (blocks if empty)"""
        self.filled_slots.acquire()  # Wait for item
        
        with self.mutex:
            item = self.buffer.get()
            self.total_consumed += 1
        
        self.empty_slots.release()  # Signal slot available
        return item
    
    def get_stats(self):
        """Get current buffer statistics"""
        with self.mutex:
            return {
                'size': self.buffer.qsize(),
                'max_size': self.max_size,
                'total_produced': self.total_produced,
                'total_consumed': self.total_consumed,
                'items_by_priority': {p.name: count for p, count in self.items_by_priority.items()}
            }


class Producer(threading.Thread):
    """Producer thread that generates items with priorities"""
    
    def __init__(self, producer_id: int, buffer: PriorityBuffer, 
                 num_items: int = 10, delay_range=(0.1, 0.5)):
        super().__init__()
        self.producer_id = producer_id
        self.buffer = buffer
        self.num_items = num_items
        self.delay_range = delay_range
        self.running = True
        self.item_counter = 0
        
    def run(self):
        """Produce items with random priorities"""
        while self.running and self.item_counter < self.num_items:
            # Generate random priority
            priority = random.choice(list(Priority))
            
            # Create item
            item = PriorityItem(
                priority=priority.value,
                item_id=self.item_counter,
                data=f"Producer-{self.producer_id}-Item-{self.item_counter}"
            )
            
            # Produce item
            self.buffer.produce(item)
            print(f"[PRODUCER {self.producer_id}] Produced: {item.data} "
                  f"(Priority: {priority.name})")
            
            self.item_counter += 1
            
            # Random delay
            time.sleep(random.uniform(*self.delay_range))
        
        print(f"[PRODUCER {self.producer_id}] Finished producing {self.item_counter} items")
    
    def stop(self):
        """Stop the producer"""
        self.running = False


class Consumer(threading.Thread):
    """Consumer thread that processes items by priority"""
    
    def __init__(self, consumer_id: int, buffer: PriorityBuffer, 
                 process_time_range=(0.1, 0.3)):
        super().__init__()
        self.consumer_id = consumer_id
        self.buffer = buffer
        self.process_time_range = process_time_range
        self.running = True
        self.consumed_count = 0
        self.daemon = True  # Allow program to exit even if consumers are running
        
    def run(self):
        """Consume items prioritizing highest priority first"""
        while self.running:
            try:
                # Consume item (blocks if empty)
                item = self.buffer.consume()
                self.consumed_count += 1
                
                priority_name = Priority(item.priority).name
                wait_time = time.time() - item.timestamp
                
                print(f"[CONSUMER {self.consumer_id}] Consuming: {item.data} "
                      f"(Priority: {priority_name}, Wait: {wait_time:.2f}s)")
                
                # Simulate processing time
                time.sleep(random.uniform(*self.process_time_range))
                
                print(f"[CONSUMER {self.consumer_id}] Finished: {item.data}")
                
            except Exception as e:
                if self.running:
                    print(f"[CONSUMER {self.consumer_id}] Error: {e}")
                break
        
        print(f"[CONSUMER {self.consumer_id}] Stopped after consuming {self.consumed_count} items")
    
    def stop(self):
        """Stop the consumer"""
        self.running = False


def run_simulation(num_producers=2, num_consumers=3, items_per_producer=10, buffer_size=10):
    """Run a simulation of the producer-consumer system"""
    print("=" * 80)
    print("Multi-Threaded Producer-Consumer Simulation with Priorities")
    print(f"Producers: {num_producers}, Consumers: {num_consumers}, "
          f"Items per producer: {items_per_producer}, Buffer size: {buffer_size}")
    print("=" * 80)
    
    # Create shared buffer
    buffer = PriorityBuffer(max_size=buffer_size)
    
    # Create and start producers
    producers: List[Producer] = []
    for i in range(num_producers):
        producer = Producer(i + 1, buffer, num_items=items_per_producer)
        producers.append(producer)
        producer.start()
    
    # Create and start consumers
    consumers: List[Consumer] = []
    for i in range(num_consumers):
        consumer = Consumer(i + 1, buffer)
        consumers.append(consumer)
        consumer.start()
    
    # Wait for all producers to finish
    for producer in producers:
        producer.join()
    
    print("\n" + "=" * 80)
    print("All producers finished. Waiting for consumers to empty the buffer...")
    print("=" * 80 + "\n")
    
    # Wait a bit for consumers to finish processing
    time.sleep(2)
    
    # Stop all consumers
    for consumer in consumers:
        consumer.stop()
    
    # Print final statistics
    stats = buffer.get_stats()
    print("\n" + "=" * 80)
    print("Final Statistics:")
    print(f"Total Produced: {stats['total_produced']}")
    print(f"Total Consumed: {stats['total_consumed']}")
    print(f"Remaining in Buffer: {stats['size']}")
    print(f"Items by Priority: {stats['items_by_priority']}")
    print("=" * 80)
    
    return buffer


if __name__ == "__main__":
    # Run the simulation
    run_simulation(
        num_producers=2,
        num_consumers=3,
        items_per_producer=10,
        buffer_size=10
    )
