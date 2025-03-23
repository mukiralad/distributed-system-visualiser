import threading
import time
from node import Node

class Cluster:
    def __init__(self, node_count=5):
        """Initialize a cluster with a specified number of nodes"""
        self.node_count = node_count
        self.nodes = []
        self.message_buffer = []
        self.observers = []
        self.running = True
        
        # Network partition simulation
        self.partitioned = False
        self.partition_groups = []
        
        # Initialize nodes
        for i in range(node_count):
            node = Node(i, node_count)
            node.register_observer(self.node_event_callback)
            self.nodes.append(node)
        
        # Start message processing thread
        self.message_thread = threading.Thread(target=self.process_messages)
        self.message_thread.daemon = True
    
    def register_observer(self, observer):
        """Register an observer for cluster events"""
        self.observers.append(observer)
    
    def notify_observers(self, event_type, data=None):
        """Notify all observers of cluster events"""
        for observer in self.observers:
            observer(event_type, data)
    
    def node_event_callback(self, node_id, event_type, data):
        """Callback function for node events"""
        # Forward node events to cluster observers
        self.notify_observers("node_event", {
            "node_id": node_id,
            "event_type": event_type,
            "data": data
        })
        
        # If a message was sent, add it to the buffer
        if event_type == "message_sent":
            message = data.copy()
            message["from"] = node_id
            self.message_buffer.append(message)
    
    def start(self):
        """Start the cluster simulation"""
        # Start all nodes
        for node in self.nodes:
            node.start()
        
        # Start message processing
        self.message_thread.start()
    
    def stop(self):
        """Stop the cluster simulation"""
        self.running = False
        for node in self.nodes:
            node.stop()
    
    def process_messages(self):
        """Process messages between nodes"""
        while self.running:
            # Copy and clear the buffer to avoid race conditions
            current_messages = self.message_buffer.copy()
            self.message_buffer = []
            
            for message in current_messages:
                # Simulate network delay
                time.sleep(0.01)
                
                from_id = message["from"]
                to_id = message["to"]
                
                # Check if message can be delivered (considering network partitions)
                if self.can_deliver_message(from_id, to_id):
                    # Deliver the message
                    self.nodes[to_id].receive_message(message)
                    
                    # Notify about message delivery
                    self.notify_observers("message_delivered", message)
            
            # Small sleep to prevent CPU hogging
            time.sleep(0.01)
    
    def can_deliver_message(self, from_id, to_id):
        """Check if a message can be delivered considering network partitions"""
        if not self.partitioned:
            return True
            
        # Check if nodes are in the same partition group
        for group in self.partition_groups:
            if from_id in group and to_id in group:
                return True
                
        return False
    
    def create_partition(self, groups):
        """Create a network partition with specified groups"""
        self.partitioned = True
        self.partition_groups = groups
        self.notify_observers("network_partition", {"groups": groups})
    
    def heal_partition(self):
        """Heal network partition"""
        self.partitioned = False
        self.partition_groups = []
        self.notify_observers("network_healed", {})
    
    def fail_node(self, node_id):
        """Simulate failure of a specific node"""
        if 0 <= node_id < self.node_count:
            self.nodes[node_id].simulate_failure()
            self.notify_observers("node_failed", {"node_id": node_id})
    
    def restore_node(self, node_id):
        """Restore a failed node"""
        if 0 <= node_id < self.node_count:
            self.nodes[node_id].restore()
            self.notify_observers("node_restored", {"node_id": node_id}) 