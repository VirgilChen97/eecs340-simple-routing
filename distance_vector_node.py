from simulator.node import Node

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.table = {}
        # {
        #   neighbourId:{
        #       path: [],
        #       latency: integer
        #   }
        # }
        self.neighbors = set()

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if neighbor not in self.neighbors:
            self.neighbors.add(neighbor)

        if neighbor not in self.table or (neighbor in self.table and self.table[neighbor].latency > latency):
            new_path = {'path':[self.id], 'latency': latency}
            table[neighbor] = new_path
                
        pass

    # Fill in this function
    def process_incoming_routing_message(self, m):
        pass

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        return -1
