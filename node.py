#Class for Implementing the Raft Node 
import threading
import random
import time
from state_machine import StateMachine
from persistence import Persistence

class Node:
    def __init__(self, node_id, peer_nodes):
        self.id = node_id
        self.state = "follower"  # Initial state is follower
        self.current_term = 0
        self.voted_for = None
        self.log = []  # List of log entries
        self.commit_index = 0
        self.last_applied = 0
        self.next_index = {peer.id: len(self.log) for peer in peer_nodes}
        self.match_index = {peer.id: 0 for peer in peer_nodes}
        self.peer_nodes = peer_nodes
        #Initialize the state machine
        self.state_machine = StateMachine()
        # Initialize persistence
        self.persistence = Persistence(node_id)

        # Timeout values for election and heartbeat intervals (in seconds)
        self.election_timeout = random.uniform(1.5, 3.0)
        self.heartbeat_interval = 0.5

    def save_state_and_log(self):
        """Save the state machine state and log to storage."""
        self.persistence.save_log(self.log)
        self.persistence.save_state(self.state_machine.state)

         # Load logs and state from storage
        self.log = self.persistence.load_log()
        self.state_machine = StateMachine(self.persistence.load_state())

        
        # Threading to manage timeouts
        self.election_timer = threading.Timer(self.election_timeout, self.start_election)
        self.election_timer.start()
    def apply_committed_entries(self):
        """Apply committed entries to the state machine."""
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied]

            # Apply the entry to the state machine
            self.state_machine.apply_entry(entry)

    def handle_append_entries(self, term, leader_id, prev_log_index, prev_log_term, entries, leader_commit):
        """Handle AppendEntries RPCs from the leader."""
        if term < self.current_term:
            return False, self.current_term  # Reject if term is lower

        # Reset election timer when valid AppendEntries received
        self.reset_election_timer()

        # Check log consistency
        if prev_log_index >= len(self.log) or self.log[prev_log_index].term != prev_log_term:
            return False, self.current_term
        
        # Append entries to the log and update commit index if necessary
        self.log = self.log[:prev_log_index + 1] + entries
        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log) - 1)
            self.apply_committed_entries()
        
        return True, self.current_term

    def handle_request_vote(self, term, candidate_id, last_log_index, last_log_term):
        """Handle RequestVote RPCs from candidates."""
        if term < self.current_term:
            return False, self.current_term  # Reject if term is lower
        
        # If the term is the same or higher, check log consistency and vote
        if (self.voted_for is None or self.voted_for == candidate_id) and (
            last_log_term > self.get_last_log_term() or (
                last_log_term == self.get_last_log_term() and last_log_index >= self.get_last_log_index()
            )
        ):
            self.current_term = term
            self.voted_for = candidate_id
            self.reset_election_timer()
            return True, self.current_term
        
        return False, self.current_term

    def start_election(self):
        """Start an election when the node becomes a candidate."""
        self.current_term += 1
        self.state = "candidate"
        self.voted_for = self.id  # Vote for itself

        # Request votes from other nodes
        votes_received = 1  # Already voted for itself
        for peer in self.peer_nodes:
            granted, term = peer.handle_request_vote(
                self.current_term, self.id, self.get_last_log_index(), self.get_last_log_term()
            )
            if granted:
                votes_received += 1
        
        # Check if a majority of votes is obtained
        if votes_received > len(self.peer_nodes) / 2:
            self.state = "leader"
            # Initialize next_index and match_index for each follower
            for peer in self.peer_nodes:
                self.next_index[peer.id] = len(self.log)
                self.match_index[peer.id] = 0
        else:
            # Failed to become leader, return to follower state
            self.state = "follower"
            self.voted_for = None
        
        # Reset election timer in case the election failed
        self.reset_election_timer()

    def apply_committed_entries(self):
        """Apply committed entries to the state machine."""
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied]
            # Apply the entry to the state machine (you should implement this)
            self.apply_entry_to_state_machine(entry)

    def reset_election_timer(self):
        """Reset the election timer."""
        self.election_timer.cancel()
        self.election_timer = threading.Timer(self.election_timeout, self.start_election)
        self.election_timer.start()

    def get_last_log_index(self):
        """Return the index of the last log entry."""
        return len(self.log) - 1

    def get_last_log_term(self):
        """Return the term of the last log entry."""
        return self.log[-1].term if self.log else 0

    def apply_entry_to_state_machine(self, entry):
        """Apply a log entry to the state machine."""
        # Implement the state machine application logic here
        pass
