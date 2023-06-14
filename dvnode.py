import socket
import sys
import time

# Maximum number of nodes in the network
MAX_NODES = 16


# Node class to store routing table and distance vector
class Node:
    def __init__(self, port, neighbors):
        self.port = port
        self.routing_table = {}  # {destination: (next_hop, distance)}
        self.distance_vector = {local_port: 0}  # {destination: distance}
        self.neighbors = neighbors  # [(port, loss_rate)]
        self.sockets = {}

        # Create UDP socket for sending and receiving data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', local_port))

        # Create sockets for each neighboring port
        for neighbor_port, _ in neighbors:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('localhost', neighbor_port))
            sock.settimeout(50)
            self.sockets[neighbor_port] = sock
        
        for i in range(len(self.neighbors)):
            neighbor, loss_rate = self.neighbors[i]
            next_hop = neighbors[(i + 1) % len(neighbors)][0]  
            self.routing_table[neighbor] = (next_hop, 1)

        for neighbor_port, loss_rate in self.neighbors:
            # Distance to self is 0
            if neighbor_port == self.port:
                self.distance_vector[self.port] = 0.0
                self.routing_table[self.port] = (None, 0.0)
            else:
                self.distance_vector[neighbor_port] = float('inf')

    # Update routing table using Bellman-Ford algorithm
    def update_routing_table(self):
        updated = False
        for dest, (next_hop, distance) in self.routing_table.items():
            min_distance = distance
            for neighbor_port, loss_rate in self.neighbors:
                if neighbor_port != next_hop:
                    # Calculate distance to destination via neighbor
                    neighbor_distance = self.distance_vector[neighbor_port] + self.routing_table[neighbor_port][1]
                    if neighbor_distance < min_distance:
                        min_distance = neighbor_distance
                        next_hop = neighbor_port

            # Update routing table if necessary
            if next_hop != self.routing_table[dest][0]:
                self.routing_table[dest] = (next_hop, min_distance)
                updated = True
        return updated

    # Send distance vector to neighbors
    def send_distance_vector(self):

        for neighbor_port, _ in self.neighbors:


            distance = self.routing_table.get(neighbor_port, (None, float('inf')))[1] + self.distance_vector[neighbor_port]
            self.distance_vector[neighbor_port] = distance

        
        for neighbor_port, loss_rate in self.neighbors:
            if neighbor_port != self.port:
                # Create UDP packet with distance vector
                packet = str(self.port) + ',' + ','.join([str(dest) + ':' + str(distance) for dest, distance in self.distance_vector.items()])

                self.sock.sendto(packet.encode(), ('localhost', neighbor_port))
                print('[{}] Message sent from Node {} to Node {}'.format(time.strftime('%Y-%m-%d %H:%M:%S'), self.port, neighbor_port))

    # Receive distance vector from neighbor
    def receive_distance_vector(self, data, neighbor_port):
        # Extract source port and distance vector from received data

        source_port, distance_vector = data.decode().split(',', 1)

        source_port = int(source_port)
        distance_vector = dict([dest.split(':') for dest in distance_vector.split(',')])

        # Update distance vector
        self.distance_vector[source_port] = 0.0  # Distance to self is 0
        for dest, distance in distance_vector.items():
            self.distance_vector[int(dest)] = float(distance)

        # Update routing table if necessary
        updated = self.update_routing_table()

        print('[{}] Message received at Node {} from Node {}'.format(time.strftime('%Y-%m-%d %H:%M:%S'), neighbor_port, source_port))
        print_routing_table(self)

        # If routing table is updated, send updated distance vector to neighbors
        if updated:
            self.send_distance_vector()

# Utility function to print routing table
def print_routing_table(node):

    print('[{}] Node {} Routing Table'.format(time.strftime('%Y-%m-%d %H:%M:%S'), node.port))
    for dest, (next_hop, distance) in node.routing_table.items():
        if next_hop == None:
            print('- ({}) -> Node {}'.format(distance, dest))
        else:
            print('- ({}) -> Node {}; Next hop -> Node {}'.format(distance, dest, next_hop))

# Check command line arguments
if len(sys.argv) < 4:
    print('Usage: python dvnode.py <local-port> <neighbors> <loss-rates>')
    sys.exit(1)

local_port = int(sys.argv[1])
neighbors = []
for i in range(2, len(sys.argv)-1, 2):
    neighbor_port = int(sys.argv[i])
    loss_rate = float(sys.argv[i+1])
    neighbors.append((neighbor_port, loss_rate))


# Create node instance with given local port and neighbors
node = Node(local_port, neighbors)


# Perform routing message exchanges among the nodes

if sys.argv[-1] == "last":
    node.send_distance_vector()
try:
    for neighbor_port, _ in neighbors:
        data, addr = node.sockets[neighbor_port].recvfrom(1024)
        node.receive_distance_vector(data, neighbor_port)
except socket.timeout:
    pass

node.update_routing_table()
time.sleep(1)
