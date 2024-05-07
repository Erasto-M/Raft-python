import os
import pickle

class Persistence:
    def __init__(self, node_id, storage_dir="raft_storage"):
        """Initialize the persistence layer for a node."""
        self.node_id = node_id
        self.storage_dir = storage_dir
        
        # Create the storage directory if it does not exist
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        # Define file paths for log and state
        self.log_path = os.path.join(self.storage_dir, f"{self.node_id}_log.pkl")
        self.state_path = os.path.join(self.storage_dir, f"{self.node_id}_state.pkl")

    def save_log(self, log):
        """Save the log to a file."""
        with open(self.log_path, "wb") as file:
            pickle.dump(log, file)

    def load_log(self):
        """Load the log from a file."""
        if os.path.exists(self.log_path):
            with open(self.log_path, "rb") as file:
                return pickle.load(file)
        return []

    def save_state(self, state):
        """Save the state to a file."""
        with open(self.state_path, "wb") as file:
            pickle.dump(state, file)

    def load_state(self):
        """Load the state from a file."""
        if os.path.exists(self.state_path):
            with open(self.state_path, "rb") as file:
                return pickle.load(file)
        return {}

    def clear_storage(self):
        """Clear the storage files for a node."""
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        if os.path.exists(self.state_path):
            os.remove(self.state_path)
