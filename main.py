import time
from node import Node
from communication import RaftClient, start_server
from cluster import Cluster
from state_machine import StateMachine
from persistence import Persistence


def main():
    # Define node IDs and ports for the cluster
    node_ids = [1, 2, 3]
    ports = [50051, 50052, 50053]

    # Create the cluster with the given node IDs and ports
    cluster = Cluster(node_ids, ports)

    # Initialize the cluster
    cluster.start_cluster()

    # Keep the main function running to allow the cluster to operate
    try:
        while True:
            time.sleep(1)  # Sleep to keep the main function running
    except KeyboardInterrupt:
        print("Simulation terminated by user.")

if __name__ == "__main__":
    main()
