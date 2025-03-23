import random
import time
import threading
from enum import Enum

class NodeState(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

class Node:
    def __init__(self, node_id, nodes_count, election_timeout_range=(150, 300)):
        # Node identity
        self.id = node_id
        self.nodes_count = nodes_count
        
        # Consensus state
        self.state = NodeState.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.votes_received = 0
        
        # Log state (simplified for this demo)
        self.log = []
        
        # Election timing
        self.election_timeout_range = election_timeout_range
        self.reset_election_timeout()
        self.last_heartbeat = time.time()
        
        # Communication
        self.message_queue = []
        self.observers = []
        
        # Thread control
        self.running = True
        self.thread = threading.Thread(target=self.run)
        
    def register_observer(self, observer):
        """Register a callback function to be notified of state changes"""
        self.observers.append(observer)
        
    def notify_observers(self, message_type, data=None):
        """Notify all observers of state changes"""
        for observer in self.observers:
            observer(self.id, message_type, data)
    
    def reset_election_timeout(self):
        """Reset election timeout with a random value"""
        self.election_timeout = random.randint(
            self.election_timeout_range[0], 
            self.election_timeout_range[1]
        ) / 1000  # Convert to seconds
    
    def start(self):
        """Start the node's thread"""
        self.thread.start()
    
    def stop(self):
        """Stop the node's thread"""
        self.running = False
        
    def run(self):
        """Main execution loop for the node"""
        while self.running:
            current_time = time.time()
            
            if self.state == NodeState.LEADER:
                self.send_heartbeats()
                time.sleep(0.05)  # Send heartbeats every 50ms
                
            elif (current_time - self.last_heartbeat) > self.election_timeout:
                self.start_election()
                
            time.sleep(0.01)  # Small sleep to prevent CPU hogging
    
    def start_election(self):
        """Start an election to become leader"""
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.id
        self.votes_received = 1  # Vote for self
        self.reset_election_timeout()
        self.last_heartbeat = time.time()
        
        # Notify observers of state change
        self.notify_observers("state_change", {"state": self.state, "term": self.current_term})
        
        # Request votes from all other nodes
        self.request_votes()
        
    def request_votes(self):
        """Send RequestVote RPCs to all other nodes"""
        for i in range(self.nodes_count):
            if i != self.id:
                # In a real system, would send messages over the network
                # For simulation, directly add to the message queue
                self.message_queue.append({
                    "type": "request_vote",
                    "from": self.id,
                    "to": i,
                    "term": self.current_term
                })
                
                # Notify observers about message
                self.notify_observers("message_sent", {
                    "from": self.id,
                    "to": i,
                    "type": "request_vote",
                    "term": self.current_term
                })
    
    def send_heartbeats(self):
        """Send AppendEntries RPCs to all other nodes (as heartbeats)"""
        for i in range(self.nodes_count):
            if i != self.id:
                self.message_queue.append({
                    "type": "append_entries",
                    "from": self.id,
                    "to": i,
                    "term": self.current_term,
                    "entries": []  # Empty for heartbeats
                })
                
                # Notify observers about heartbeat
                self.notify_observers("message_sent", {
                    "from": self.id,
                    "to": i,
                    "type": "heartbeat",
                    "term": self.current_term
                })
    
    def receive_message(self, message):
        """Handle incoming messages from other nodes"""
        message_type = message["type"]
        
        if message_type == "request_vote":
            self.handle_vote_request(message)
        elif message_type == "vote_response":
            self.handle_vote_response(message)
        elif message_type == "append_entries":
            self.handle_append_entries(message)
    
    def handle_vote_request(self, message):
        """Handle RequestVote RPC"""
        term = message["term"]
        candidate_id = message["from"]
        
        # Update term if necessary
        if term > self.current_term:
            self.current_term = term
            self.state = NodeState.FOLLOWER
            self.voted_for = None
            self.notify_observers("state_change", {"state": self.state, "term": self.current_term})
        
        # Decide whether to grant vote
        grant_vote = False
        if term >= self.current_term and (self.voted_for is None or self.voted_for == candidate_id):
            grant_vote = True
            self.voted_for = candidate_id
            self.last_heartbeat = time.time()  # Reset election timeout
        
        # Send response
        self.message_queue.append({
            "type": "vote_response",
            "from": self.id,
            "to": candidate_id,
            "term": self.current_term,
            "vote_granted": grant_vote
        })
        
        # Notify observers
        self.notify_observers("message_sent", {
            "from": self.id,
            "to": candidate_id,
            "type": "vote_response",
            "vote_granted": grant_vote,
            "term": self.current_term
        })
    
    def handle_vote_response(self, message):
        """Handle responses to RequestVote RPCs"""
        if self.state != NodeState.CANDIDATE:
            return
            
        term = message["term"]
        vote_granted = message["vote_granted"]
        
        # Update term if necessary
        if term > self.current_term:
            self.current_term = term
            self.state = NodeState.FOLLOWER
            self.voted_for = None
            self.notify_observers("state_change", {"state": self.state, "term": self.current_term})
            return
        
        # Count votes
        if vote_granted and term == self.current_term:
            self.votes_received += 1
            
            # If majority, become leader
            if self.votes_received > self.nodes_count / 2:
                self.state = NodeState.LEADER
                self.notify_observers("state_change", {"state": self.state, "term": self.current_term})
                self.send_heartbeats()  # Send immediate heartbeats
    
    def handle_append_entries(self, message):
        """Handle AppendEntries RPC (also used for heartbeats)"""
        term = message["term"]
        leader_id = message["from"]
        
        # Update term if necessary
        if term > self.current_term:
            self.current_term = term
            self.state = NodeState.FOLLOWER
            self.voted_for = None
            self.notify_observers("state_change", {"state": self.state, "term": self.current_term})
        
        # Accept heartbeat if term is valid
        if term >= self.current_term:
            self.last_heartbeat = time.time()  # Reset election timeout
            
            # If was candidate, step down
            if self.state == NodeState.CANDIDATE:
                self.state = NodeState.FOLLOWER
                self.notify_observers("state_change", {"state": self.state, "term": self.current_term})
                
        # Send response (simplified)
        self.message_queue.append({
            "type": "append_entries_response",
            "from": self.id,
            "to": leader_id,
            "term": self.current_term,
            "success": term >= self.current_term
        })
    
    def simulate_failure(self):
        """Simulate node failure (stop processing messages)"""
        self.running = False
        self.notify_observers("node_failure", {"id": self.id})
    
    def restore(self):
        """Restore node after failure"""
        if not self.running:
            self.running = True
            self.state = NodeState.FOLLOWER
            self.current_term += 1  # Increment term
            self.voted_for = None
            self.last_heartbeat = time.time() - self.election_timeout - 1  # Force timeout
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
            self.notify_observers("node_restore", {"id": self.id}) 