This is an implementation of a distance vector routing algorithm using the Bellman-Ford algorithm. It defines a Node class that represents a node in the network and maintains its routing table and distance vector. The Node class has methods for updating the routing table, sending and receiving distance vectors, and printing the routing table.

The Node class uses UDP sockets for sending and receiving data between nodes. It binds a UDP socket to the local port specified as a command line argument, and creates additional sockets for each neighboring port specified as a command line argument. It uses these sockets to send and receive distance vectors to and from its neighbors.

The Node class also maintains a routing table, which is a dictionary that maps destination nodes to the next hop node and the distance to the destination. The update_routing_table method updates the routing table using the Bellman-Ford algorithm, and the send_distance_vector method sends the updated distance vector to its neighbors. The receive_distance_vector method receives a distance vector from a neighbor, updates its own distance vector, updates the routing table if necessary, and sends the updated distance vector to its neighbors if the routing table is updated.

The script takes command line arguments for the local port, the neighboring ports, and their corresponding loss rates. It creates a Node instance with the given local port and neighbors, and then performs routing message exchanges among the nodes by sending and receiving distance vectors using the UDP sockets. The script also has an option to send the distance vector of the last node in the network by passing "last" as the last command line argument.

Command Line arguments: 

<local-port>: The local port number for the node.
<neighbors>: The neighboring nodes, specified as pairs of port numbers and loss rates, separated by spaces. For example, "8000 0.1 8001 0.2" specifies two neighbors with port numbers 8000 and 8001, and loss rates of 0.1 and 0.2 respectively.
<loss-rates>: The loss rates for the neighboring nodes, specified as floating-point numbers separated by spaces. The number of loss rates should be equal to the number of neighboring nodes.
You can also add an optional argument "last" at the end to indicate that the current node is the last node to start sending distance vectors. 
For eg : python dvnode.py 8000 8001 0.1 8002 0.2 last



