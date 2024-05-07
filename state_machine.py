class StateMachine:
    def __init__(self):
        """Initialize the state machine."""
        self.state = {}  # Dictionary to store key-value pairs

    def apply_entry(self, entry):
        """Apply a committed log entry to the state machine."""
        if entry.operation == "set":
            # Set the key-value pair in the state
            self.state[entry.key] = entry.value
        elif entry.operation == "delete":
            # Remove the key from the state
            if entry.key in self.state:
                del self.state[entry.key]

    def get_value(self, key):
        """Retrieve the value associated with a key from the state machine."""
        return self.state.get(key, None)
