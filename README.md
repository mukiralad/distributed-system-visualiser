# Distributed System Simulation

A visualization and simulation of a simplified Raft consensus algorithm.

## Overview
This project simulates a distributed system with multiple nodes running a consensus protocol based on Raft. 
It demonstrates concepts such as leader election, log replication, and fault tolerance in distributed systems.

## Features
- Multiple node simulation with state visualization
- Leader election algorithm
- Interactive node failure simulation
- Network partition simulation
- Real-time message passing visualization

## Requirements
- Python 3.7+
- Tkinter (for visualization)
- Pillow (for image processing)

## Usage
Run the main simulation:
```
python src/main.py
``` 

## Overview

This application simulates a distributed consensus protocol based on the Raft algorithm. It provides a visual representation of how distributed systems achieve consensus through leader election, heartbeat mechanisms, and fault tolerance.

## Technical Details

### Raft Consensus Algorithm

The Raft consensus algorithm is designed to be more understandable than previous consensus algorithms like Paxos while providing the same guarantees. It works by:

1. **Leader Election**: Nodes start as followers, but if they don't receive communication from a leader, they can become candidates and request votes.
2. **Log Replication**: Once a leader is elected, it handles all client requests and replicates the changes to other nodes.
3. **Safety**: Raft ensures that once a command is committed, it won't be overwritten by future leaders.

### Components

The simulation consists of several key components:

#### Node (node.py)

Each `Node` represents a server in the distributed system. Nodes can be in one of three states:
- **Follower**: Passive state, responds to leaders
- **Candidate**: Actively seeking votes to become leader
- **Leader**: Coordinates the cluster

Nodes contain:
- Current term number
- Voting information
- Communication mechanisms
- State change logic
- Log (simplified in this implementation)

#### Cluster (cluster.py)

The `Cluster` manages all nodes and handles message passing between them. It:
- Coordinates all nodes in the system
- Manages message delivery between nodes
- Simulates network partitions
- Handles node failures and recoveries

#### Visualizer (visualizer.py)

The `Visualizer` creates a graphical representation of the cluster. It:
- Displays node states with different colors
- Shows message passing between nodes
- Provides interactive controls for testing fault scenarios
- Logs important events

#### Main Application (main.py)

The entry point that ties everything together and initializes the simulation.

### Key Algorithms

1. **Leader Election**:
   - Followers become candidates if they don't receive heartbeats
   - Candidates request votes from all other nodes
   - If a candidate receives votes from the majority, it becomes leader
   - If the term changes, nodes update their state accordingly

2. **Heartbeat Mechanism**:
   - Leaders send periodic heartbeats to all followers
   - Followers reset their election timeout upon receiving valid heartbeats
   - If a follower doesn't receive heartbeats within a timeout, it starts an election

3. **Fault Tolerance**:
   - The system continues to function as long as a majority of nodes are operational
   - Failed nodes can be restored
   - Network partitions can split the cluster temporarily

### Network Partition Simulation

The application can simulate network partitions by:
- Dividing nodes into separate groups
- Preventing message delivery between groups
- Demonstrating split-brain scenarios
- Showing recovery when partitions are healed

## User Instructions

### Running the Application

1. Ensure Python 3.7+ is installed
2. Run `python src/main.py` or use the `run.bat` script

### Interface Controls

- **Node Control**: Select a node to fail or restore
- **Network Control**: Create or heal network partitions

### Visualization Elements

- **Blue Nodes**: Followers
- **Orange Nodes**: Candidates
- **Green Nodes**: Leaders
- **Red Nodes**: Failed nodes
- **Purple Lines**: Vote request messages
- **Dark Blue Lines**: Vote response messages
- **Gray Lines**: Heartbeat messages

### Testing Scenarios

1. **Leader Failure**:
   - Select the current leader and click "Fail Node"
   - Observe a new election taking place
   - See a new leader emerge

2. **Network Partition**:
   - Click "Create Partition"
   - Observe multiple leaders emerging in different partitions
   - Click "Heal Partition" and watch the system resolve to a single leader

## Technical Implementation Challenges

1. **Timing and Concurrency**:
   - Using threading to simulate multiple independent nodes
   - Managing race conditions in message delivery
   - Ensuring proper timeout mechanisms

2. **Visualization Synchronization**:
   - Keeping the UI in sync with the distributed system state
   - Animating message passing between nodes
   - Displaying state changes in real-time

3. **Simplified but Accurate Raft Implementation**:
   - Implementing core Raft concepts while simplifying for visualization
   - Ensuring the simulation follows the key safety properties
   - Demonstrating the actual behaviors seen in real distributed systems

## Educational Value

This simulation demonstrates:
- How distributed consensus works in practice
- The importance of leader election
- How systems recover from failures
- The challenges of network partitions
- The trade-offs in distributed system design

## Extensions and Future Work

Possible extensions to this project:
- Add log replication visualization
- Implement membership changes
- Add client interactions
- Simulate network delays and message losses
- Implement more complex partition scenarios 