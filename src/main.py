import tkinter as tk
import sys
import time
from cluster import Cluster
from visualizer import Visualizer

def main():
    """Main application entry point"""
    # Configure number of nodes
    node_count = 5
    
    # Create the cluster
    cluster = Cluster(node_count=node_count)
    
    # Create Tkinter root window
    root = tk.Tk()
    
    # Create visualizer
    visualizer = Visualizer(root, cluster)
    
    # Start the cluster simulation
    cluster.start()
    
    # Set up clean shutdown
    def on_closing():
        cluster.stop()
        time.sleep(0.5)  # Allow time for threads to stop
        root.destroy()
        sys.exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Run the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main() 