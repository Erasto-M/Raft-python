import random
import threading
import time
from node import Node
from communication import RaftClient, start_server

class Cluster:
    def __init__(self, node_ids, ports):
        """Initialize the cluster with a list of node IDs and corresponding ports."""
        self.nodes = []
        self.node_ports = {}
        
        # Create nodes and clients
        for node_id, port in zip(node_ids, ports):
            node = Node(node_id, [])
            self.nodes.append(node)
            self.node_ports[node_id] = port
        
        # Create peer lists and communication clients
        for node in self.nodes:
            peer_nodes = [n for n in self.nodes if n.id != node.id]
            node.peer_nodes = peer_nodes
            
            # Create a client for each peer node
            node.clients = {peer.id: RaftClient(f"localhost:{self.node_ports[peer.id]}") for peer in peer_nodes}

    def start_cluster(self):
        """Start the cluster by initializing servers and threads for each node."""
        threads = []
        
        # Start servers for each node in the cluster
        for node, port in zip(self.nodes, self.node_ports.values()):
            thread = threading.Thread(target=start_server, args=(node, port))
            thread.start()
            threads.append(thread)
        
        # Monitor the cluster indefinitely
        try:
            while True:
                self.monitor_cluster()
                time.sleep(1)  # Monitor every second
        except KeyboardInterrupt:
            print("Shutting down cluster...")
            for thread in threads:
                thread.join()

    def monitor_cluster(self):
        """Monitor the cluster for node failures and initiate recovery."""
        for node in self.nodes:
            if node.state == "leader":
                # Send heartbeats to all followers
                self.send_heartbeats(node)
            elif node.state == "follower":
                # Check if the leader is still active
                if not self.receive_heartbeat(node):
                    # If no heartbeat received, start an election
                    node.start_election()
            elif node.state == "candidate":
                # Check if the candidate has become the leader
                if not self.check_if_leader(node):
                    # If not, start a new election
                    node.start_election()

    def send_heartbeats(self, leader):
        """Send heartbeats from the leader to all followers."""
        for follower in leader.peer_nodes:
            success, term = leader.clients[follower.id].append_entries(
                leader.current_term, leader.id, leader.get_last_log_index(),
                leader.get_last_log_term(), [], leader.commit_index
            )
            
            if not success and term > leader.current_term:
                # Step down to follower if the term is outdated
                leader.state = "follower"
                leader.current_term = term
                leader.voted_for = None

    def receive_heartbeat(self, follower):
        """Check if the follower receives a heartbeat from the leader."""
        # This function would need a mechanism to receive heartbeats from the leader.
        # Implement this based on your specific communication protocol and monitoring strategy.
        # For simplicity, return True if a heartbeat is received.
        return True  # Replace this with actual heartbeat receiving logic.

    def check_if_leader(self, candidate):
        """Check if the candidate has become the leader."""
        votes_received = 1  # Candidate votes for itself
        
        # Request votes from peers
        for peer in candidate.peer_nodes:
            granted, term = candidate.clients[peer.id].request_vote(
                candidate.current_term, candidate.id, candidate.get_last_log_index(),
                candidate.get_last_log_term()
            )
            
            if granted:
                votes_received += 1
        
        # Check if a majority of votes is obtained
        if votes_received > len(candidate.peer_nodes) / 2:
            candidate.state = "leader"
            # Initialize next_index and match_index for each follower
            for peer in candidate.peer_nodes:
                candidate.next_index[peer.id] = len(candidate.log)
                candidate.match_index[peer.id] = 0
            return True
        
        return False
