import tkinter as tk
from tkinter import ttk
import math
import time
from node import NodeState
from PIL import Image, ImageTk, ImageDraw
import random

# Define a simpler, more visible color scheme
COLORS = {
    "background": "#121212", 
    "follower": "#4287f5",    # Bright blue
    "candidate": "#ff7700",   # Bright orange
    "leader": "#00e676",      # Bright green
    "failed": "#ff0000",      # Bright red
    "text": "#ffffff",        # White
    "label": "#dddddd",       # Light gray
    "vote": "#ba68c8",        # Purple
    "heartbeat": "#757575"    # Gray
}

class ModernTheme:
    """Custom modern theme for ttk widgets"""
    def __init__(self, root):
        # Configure ttk styles
        self.style = ttk.Style(root)
        self.style.theme_use('default')
        
        # Configure colors
        self.style.configure('TFrame', background=COLORS["background"])
        self.style.configure('TLabelframe', background=COLORS["background"], foreground=COLORS["text_primary"])
        self.style.configure('TLabelframe.Label', background=COLORS["background"], foreground=COLORS["text_primary"])
        
        # Modern button style
        self.style.configure('Modern.TButton',
            background=COLORS["primary"],
            foreground=COLORS["text_primary"],
            borderwidth=0,
            focusthickness=3,
            focuscolor=COLORS["primary"])
        
        # Alternate button style
        self.style.configure('Secondary.TButton',
            background=COLORS["secondary"],
            foreground=COLORS["text_primary"],
            borderwidth=0,
            focusthickness=3,
            focuscolor=COLORS["secondary"])
        
        # Error button style
        self.style.configure('Error.TButton',
            background=COLORS["error"],
            foreground=COLORS["text_primary"],
            borderwidth=0,
            focusthickness=3,
            focuscolor=COLORS["error"])
        
        # Modern combobox style
        self.style.configure('TCombobox',
            fieldbackground=COLORS["surface"],
            background=COLORS["primary"],
            foreground=COLORS["text_primary"],
            arrowcolor=COLORS["primary"],
            borderwidth=0)
        
        self.style.map('TCombobox',
            fieldbackground=[('readonly', COLORS["surface"])],
            selectbackground=[('readonly', COLORS["primary"])],
            selectforeground=[('readonly', COLORS["text_primary"])])
        
        # Text style
        self.style.configure('Log.TFrame', background=COLORS["surface"])

class AnimatedNode:
    """Node with smooth animation capabilities"""
    def __init__(self, canvas, node_id, x, y, radius, state, term):
        self.canvas = canvas
        self.id = node_id
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.radius = radius
        self.state = state
        self.term = term
        self.pulse = 0
        self.pulse_direction = 1
        
        # Create visual elements with empty IDs (will be created when drawn)
        self.circle_id = None
        self.label_id = None
        self.term_id = None
        self.aura_id = None
        
    def set_target_position(self, x, y):
        """Set target position for animation"""
        self.target_x = x
        self.target_y = y
    
    def update(self, state=None, term=None):
        """Update node status"""
        if state is not None:
            self.state = state
        if term is not None:
            self.term = term
    
    def animate(self):
        """Animate movement and effects"""
        # Position animation (for smooth movement)
        if self.x != self.target_x or self.y != self.target_y:
            # Ease towards target position
            self.x += (self.target_x - self.x) * 0.1
            self.y += (self.target_y - self.y) * 0.1
            
            # If very close to target, snap to it
            if abs(self.x - self.target_x) < 0.5:
                self.x = self.target_x
            if abs(self.y - self.target_y) < 0.5:
                self.y = self.target_y
                
            return True  # Needs redraw
        
        # Pulse animation for leader and candidate nodes
        if self.state in [NodeState.LEADER, NodeState.CANDIDATE]:
            self.pulse += 0.05 * self.pulse_direction
            if self.pulse > 1:
                self.pulse = 1
                self.pulse_direction = -1
            elif self.pulse < 0:
                self.pulse = 0
                self.pulse_direction = 1
            return True  # Needs redraw
        
        return False  # No redraw needed
    
    def draw(self):
        """Draw the node on the canvas"""
        # Delete previous drawing
        if self.circle_id:
            self.canvas.delete(self.circle_id)
        if self.label_id:
            self.canvas.delete(self.label_id)
        if self.term_id:
            self.canvas.delete(self.term_id)
        if self.aura_id:
            self.canvas.delete(self.aura_id)
        
        # Determine color based on state
        if not self.state:  # Failed state
            color = COLORS["failed"]
            aura_color = ""
        elif self.state == NodeState.LEADER:
            color = COLORS["leader"]
            # Create aura for leader
            aura_radius = self.radius + 10 + self.pulse * 5
            aura_color = COLORS["leader"]
        elif self.state == NodeState.CANDIDATE:
            color = COLORS["candidate"]
            # Create aura for candidate
            aura_radius = self.radius + 5 + self.pulse * 3
            aura_color = COLORS["candidate"]
        else:  # FOLLOWER
            color = COLORS["follower"]
            aura_color = ""
        
        # Draw aura if needed
        if aura_color:
            self.aura_id = self.canvas.create_oval(
                self.x - aura_radius, self.y - aura_radius,
                self.x + aura_radius, self.y + aura_radius,
                outline=aura_color, width=2,
                fill="", dash=(1, 2)
            )
        
        # Draw node
        self.circle_id = self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill=color, outline=COLORS["text_primary"], width=2
        )
        
        # Draw node ID
        self.label_id = self.canvas.create_text(
            self.x, self.y,
            text=f"{self.id}",
            font=("Arial", 12, "bold"),
            fill=COLORS["text_primary"]
        )
        
        # Draw term
        self.term_id = self.canvas.create_text(
            self.x, self.y + self.radius + 15,
            text=f"T{self.term}",
            font=("Arial", 9),
            fill=COLORS["text_secondary"]
        )

class Message:
    """Animated message between nodes"""
    def __init__(self, canvas, from_pos, to_pos, message_type):
        self.canvas = canvas
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.type = message_type
        self.progress = 0.0
        self.speed = 0.05  # Animation speed
        self.line_id = None
        self.dot_id = None
        self.active = True
        
        # Determine color based on message type
        if message_type == "vote_response":
            self.color = COLORS["vote_response"]
        elif message_type == "request_vote":
            self.color = COLORS["vote"]
        elif message_type == "heartbeat":
            self.color = COLORS["heartbeat"]
        else:
            self.color = COLORS["secondary"]
    
    def animate(self):
        """Animate message movement"""
        if not self.active:
            return False
        
        self.progress += self.speed
        if self.progress >= 1.0:
            self.active = False
            if self.line_id:
                self.canvas.delete(self.line_id)
            if self.dot_id:
                self.canvas.delete(self.dot_id)
            return True
        
        return True
    
    def draw(self):
        """Draw the message animation"""
        # Clear previous drawing
        if self.line_id:
            self.canvas.delete(self.line_id)
        if self.dot_id:
            self.canvas.delete(self.dot_id)
        
        # Only draw if active
        if not self.active:
            return
        
        # Calculate current position
        from_x, from_y = self.from_pos
        to_x, to_y = self.to_pos
        
        # Draw path line (faded)
        self.line_id = self.canvas.create_line(
            from_x, from_y, to_x, to_y,
            fill=self.color, width=1, dash=(3, 3)
        )
        
        # Draw moving dot
        current_x = from_x + (to_x - from_x) * self.progress
        current_y = from_y + (to_y - from_y) * self.progress
        
        self.dot_id = self.canvas.create_oval(
            current_x - 4, current_y - 4,
            current_x + 4, current_y + 4,
            fill=self.color, outline=""
        )

class LogDisplay:
    """Efficient log display with limited buffer"""
    def __init__(self, parent, max_lines=100):
        self.max_lines = max_lines
        self.buffer = []
        
        self.frame = ttk.Frame(parent, style='Log.TFrame')
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create text widget with dark theme
        self.text = tk.Text(
            self.frame, 
            height=6,
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
            insertbackground=COLORS["primary"],
            relief="flat",
            font=("Consolas", 9)
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(self.text, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)
        
        # Define tags for different message types
        self.text.tag_configure("leader", foreground=COLORS["leader"])
        self.text.tag_configure("follower", foreground=COLORS["follower"])
        self.text.tag_configure("candidate", foreground=COLORS["candidate"])
        self.text.tag_configure("failed", foreground=COLORS["error"])
        self.text.tag_configure("network", foreground=COLORS["secondary"])
        self.text.tag_configure("timestamp", foreground=COLORS["text_secondary"])
    
    def add_message(self, message, tag=None):
        """Add a message to the log with timestamp"""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        
        # Add to buffer
        log_entry = (timestamp, message, tag)
        self.buffer.append(log_entry)
        
        # Trim buffer if necessary
        if len(self.buffer) > self.max_lines:
            self.buffer = self.buffer[-self.max_lines:]
            
            # Clear text and redraw from buffer
            self.text.delete(1.0, tk.END)
            for ts, msg, tg in self.buffer:
                self.text.insert(tk.END, f"[{ts}] ", "timestamp")
                self.text.insert(tk.END, f"{msg}\n", tg if tg else "")
        else:
            # Just append
            self.text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.text.insert(tk.END, f"{message}\n", tag if tag else "")
        
        self.text.see(tk.END)

class Visualizer:
    def __init__(self, root, cluster):
        """Initialize the visualization window"""
        self.root = root
        self.cluster = cluster
        self.node_count = cluster.node_count
        
        # Register as observer
        cluster.register_observer(self.cluster_event_callback)
        
        # Configure the window
        self.root.title("Distributed System Simulation")
        self.root.geometry("800x600")
        self.root.configure(bg=COLORS["background"])
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create title
        self.title_label = tk.Label(
            self.main_frame, 
            text="RAFT CONSENSUS VISUALIZATION",
            font=("Arial", 16, "bold"),
            fg="#ff7700",
            bg=COLORS["background"]
        )
        self.title_label.pack(pady=10)
        
        # Create canvas for node visualization
        self.canvas = tk.Canvas(
            self.main_frame, 
            bg=COLORS["background"], 
            height=350,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create controls frame
        self.controls_frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        self.controls_frame.pack(fill=tk.X, pady=10)
        
        # Add control buttons
        self.add_controls()
        
        # Create log frame
        self.log_frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            self.log_frame, 
            height=8, 
            width=80,
            bg="#1e1e1e",
            fg=COLORS["label"],
            font=("Consolas", 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # Configure text tags
        self.log_text.tag_configure("follower", foreground="#4287f5")
        self.log_text.tag_configure("candidate", foreground="#ff7700")
        self.log_text.tag_configure("leader", foreground="#00e676")
        self.log_text.tag_configure("failed", foreground="#ff0000")
        self.log_text.tag_configure("time", foreground="#999999")
        
        # Initialize node visualization data
        self.node_positions = []
        self.node_circles = []
        self.node_labels = []
        self.message_lines = []
        
        # Calculate node positions (circle arrangement)
        self.calculate_node_positions()
        
        # Draw the initial state
        self.draw_nodes()
        
        # Start the animation loop
        self.animate()
    
    def calculate_node_positions(self):
        """Calculate positions for nodes in a circle"""
        self.node_positions = [] # Reset positions
        
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 350
        
        radius = min(canvas_width, canvas_height) * 0.35
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        
        for i in range(self.node_count):
            angle = 2 * math.pi * i / self.node_count
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.node_positions.append((x, y))
    
    def draw_nodes(self):
        """Draw nodes on the canvas"""
        node_radius = 35
        
        # Clear canvas completely
        self.canvas.delete("all")
        
        # Draw each node
        self.node_circles = []
        self.node_labels = []
        
        for i, (x, y) in enumerate(self.node_positions):
            node = self.cluster.nodes[i]
            
            # Determine node color based on state
            if not node.running:
                color = COLORS["failed"]
                state_name = "FAILED"
            elif node.state == NodeState.LEADER:
                color = COLORS["leader"]
                state_name = "LEADER"
            elif node.state == NodeState.CANDIDATE:
                color = COLORS["candidate"]
                state_name = "CANDIDATE"
            else:  # FOLLOWER
                color = COLORS["follower"]
                state_name = "FOLLOWER"
            
            # Draw node circle with thicker outline
            circle = self.canvas.create_oval(
                x - node_radius, y - node_radius,
                x + node_radius, y + node_radius,
                fill=color, outline="white", width=2
            )
            self.node_circles.append(circle)
            
            # Draw node ID
            label = self.canvas.create_text(
                x, y,
                text=f"{i}",
                font=("Arial", 16, "bold"),
                fill=COLORS["text"]
            )
            self.node_labels.append(label)
            
            # Draw state below
            state_label = self.canvas.create_text(
                x, y + node_radius + 15,
                text=state_name,
                font=("Arial", 9),
                fill=COLORS["text"]
            )
            
            # Draw term number
            term_label = self.canvas.create_text(
                x, y + node_radius + 30,
                text=f"Term: {node.current_term}",
                font=("Arial", 9),
                fill=COLORS["label"]
            )
    
    def draw_message(self, from_id, to_id, message_type):
        """Draw a message line between nodes"""
        if from_id >= len(self.node_positions) or to_id >= len(self.node_positions):
            return
            
        from_x, from_y = self.node_positions[from_id]
        to_x, to_y = self.node_positions[to_id]
        
        # Determine color based on message type
        if message_type == "vote_response":
            color = COLORS["vote"]
        elif message_type == "request_vote":
            color = COLORS["vote"]
        elif message_type == "heartbeat":
            color = COLORS["heartbeat"]
        else:
            color = COLORS["vote"]
        
        # Draw arrow line
        line = self.canvas.create_line(
            from_x, from_y, to_x, to_y,
            fill=color, width=2, arrow=tk.LAST
        )
        
        # Store the line with timestamp for cleanup
        self.message_lines.append((line, time.time()))
    
    def clean_old_messages(self):
        """Remove old message lines"""
        current_time = time.time()
        remaining_lines = []
        
        for line, timestamp in self.message_lines:
            if current_time - timestamp > 0.5:  # Remove after 0.5 seconds
                self.canvas.delete(line)
            else:
                remaining_lines.append((line, timestamp))
        
        self.message_lines = remaining_lines
    
    def add_log_message(self, message, tag=None):
        """Add a message to the log display"""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime())
        self.log_text.insert(tk.END, timestamp + " ", "time")
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)  # Auto-scroll to the end
    
    def add_controls(self):
        """Add control buttons to the interface"""
        # Node Control Frame
        self.node_control_frame = tk.LabelFrame(
            self.controls_frame, 
            text="Node Control",
            bg=COLORS["background"],
            fg=COLORS["label"],
            bd=1
        )
        self.node_control_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.fail_node_var = tk.StringVar()
        self.fail_node_var.set("0")  # Default to first node
        
        # Style for combobox
        node_combo = ttk.Combobox(
            self.node_control_frame, 
            textvariable=self.fail_node_var,
            values=[str(i) for i in range(self.node_count)],
            width=5
        )
        node_combo.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create buttons with modern style
        fail_button = tk.Button(
            self.node_control_frame,
            text="Fail Node",
            bg="#ff0000",
            fg="white",
            activebackground="#cc0000",
            relief="flat",
            padx=10,
            command=self.fail_selected_node
        )
        fail_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        restore_button = tk.Button(
            self.node_control_frame,
            text="Restore Node",
            bg="#4287f5",
            fg="white",
            activebackground="#3269c7",
            relief="flat",
            padx=10,
            command=self.restore_selected_node
        )
        restore_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Network partition controls
        self.partition_frame = tk.LabelFrame(
            self.controls_frame, 
            text="Network Control",
            bg=COLORS["background"],
            fg=COLORS["label"],
            bd=1
        )
        self.partition_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        create_partition_button = tk.Button(
            self.partition_frame,
            text="Create Partition",
            bg="#9c27b0",
            fg="white",
            activebackground="#7b1fa2",
            relief="flat",
            padx=10,
            command=self.create_random_partition
        )
        create_partition_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        heal_partition_button = tk.Button(
            self.partition_frame,
            text="Heal Partition",
            bg="#00e676",
            fg="white",
            activebackground="#00c853",
            relief="flat",
            padx=10,
            command=self.heal_partition
        )
        heal_partition_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def fail_selected_node(self):
        """Fail the selected node"""
        try:
            node_id = int(self.fail_node_var.get())
            self.cluster.fail_node(node_id)
        except ValueError:
            pass
    
    def restore_selected_node(self):
        """Restore the selected node"""
        try:
            node_id = int(self.fail_node_var.get())
            self.cluster.restore_node(node_id)
        except ValueError:
            pass
    
    def create_random_partition(self):
        """Create a random network partition"""
        # Simple partition: divide nodes into two groups
        group1 = list(range(0, self.node_count // 2))
        group2 = list(range(self.node_count // 2, self.node_count))
        self.cluster.create_partition([group1, group2])
        
        partition_msg = f"Network partitioned: Group 1 {group1}, Group 2 {group2}"
        self.add_log_message(partition_msg)
    
    def heal_partition(self):
        """Heal the network partition"""
        self.cluster.heal_partition()
        self.add_log_message("Network partition healed")
    
    def cluster_event_callback(self, event_type, data):
        """Handle cluster events"""
        if event_type == "node_event":
            node_id = data["node_id"]
            node_event_type = data["event_type"]
            node_data = data["data"]
            
            if node_event_type == "state_change":
                # Node state changed, redraw nodes
                self.draw_nodes()
                
                state_name = node_data["state"].name.lower()
                self.add_log_message(
                    f"Node {node_id} → {state_name} (Term: {node_data['term']})",
                    state_name
                )
                
            elif node_event_type == "message_sent":
                # Message was sent between nodes
                to_node = node_data["to"]
                msg_type = node_data["type"]
                
                # Visualize the message
                self.draw_message(node_id, to_node, msg_type)
        
        elif event_type == "node_failed":
            node_id = data["node_id"]
            self.add_log_message(f"Node {node_id} failed", "failed")
            self.draw_nodes()
            
        elif event_type == "node_restored":
            node_id = data["node_id"]
            self.add_log_message(f"Node {node_id} restored", "follower")
            self.draw_nodes()
    
    def animate(self):
        """Animation loop"""
        # Clean up old message lines
        self.clean_old_messages()
        
        # Forcibly redraw nodes every 5 frames to ensure visibility
        if hasattr(self, 'frame_counter'):
            self.frame_counter += 1
            if self.frame_counter % 5 == 0:
                self.draw_nodes()
        else:
            self.frame_counter = 0
            
        # Schedule the next frame
        self.root.after(50, self.animate) 