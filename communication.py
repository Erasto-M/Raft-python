import grpc
from concurrent import futures
import time

# Import the generated Python code
import raft_pb2
import raft_pb2_grpc

# Define the server class
class RaftServer(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, node):
        # Store the reference to the node object
        self.node = node

    def RequestVote(self, request, context):
        # Handle RequestVote RPC
        granted, term = self.node.handle_request_vote(request.term, request.candidate_id, request.last_log_index, request.last_log_term)
        return raft_pb2.RequestVoteResponse(vote_granted=granted, term=term)

    def AppendEntries(self, request, context):
        # Handle AppendEntries RPC
        success, term = self.node.handle_append_entries(request.term, request.leader_id, request.prev_log_index, request.prev_log_term, request.entries, request.leader_commit)
        return raft_pb2.AppendEntriesResponse(success=success, term=term)

# Start the server
def start_server(node, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_pb2_grpc.add_RaftServiceServicer_to_server(RaftServer(node), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Raft server started on port {port}")
    try:
        while True:
            time.sleep(86400)  # Keep server running
    except KeyboardInterrupt:
        server.stop(0)

# Define the client class
class RaftClient:
    def __init__(self, address):
        # Create a channel to the server address
        self.channel = grpc.insecure_channel(address)
        # Create a stub (client) for RaftService
        self.stub = raft_pb2_grpc.RaftServiceStub(self.channel)

    def request_vote(self, term, candidate_id, last_log_index, last_log_term):
        # Send a RequestVote RPC
        request = raft_pb2.RequestVoteRequest(term=term, candidate_id=candidate_id, last_log_index=last_log_index, last_log_term=last_log_term)
        response = self.stub.RequestVote(request)
        return response.vote_granted, response.term

    def append_entries(self, term, leader_id, prev_log_index, prev_log_term, entries, leader_commit):
        # Send an AppendEntries RPC
        entry_list = [raft_pb2.Entry(term=e.term, data=e.data) for e in entries]
        request = raft_pb2.AppendEntriesRequest(term=term, leader_id=leader_id, prev_log_index=prev_log_index, prev_log_term=prev_log_term, entries=entry_list, leader_commit=leader_commit)
        response = self.stub.AppendEntries(request)
        return response.success, response.term
