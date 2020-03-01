from simulator.node import Node
import json


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.dv = {}
        # {
        #   destId:{
        #       path: [],
        #       latency: integer
        #   }
        # }
        self.neighbors = {}
        self.seq = 0

    # Return a string
    def __str__(self):
        return "{}: \nDV:{}\nneighbor:{}".format(self.id, self.dv, self.neighbors)

    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if neighbor not in self.neighbors:
            self.neighbors[neighbor] = {
                'seq': -1,
                'latency': latency
            }
        else:
            self.neighbors[neighbor]['latency'] = latency

        if neighbor not in self.dv or self.dv[neighbor]['latency'] > latency or len(self.dv[neighbor]['path']) == 0:
            new_path = {'path': [], 'latency': latency}
            self.dv[neighbor] = new_path
            message = {
                "sender": self.id,
                "seq": self.seq,
                "dv": self.dv
            }
            self.seq += 1
            self.send_to_neighbors(json.dumps(message))

    # Fill in this function
    def process_incoming_routing_message(self, m):
        hasUpdated = False
        data = json.loads(m)
        # Received message should be the newest one
        if self.neighbors[data["sender"]] < data["seq"]:
            # update seq
            self.neighbors[data["sender"]] = data['seq']
            for dst, vec in data["dv"].items():
                # if self in path, there is a loop, discard
                if self.id in vec['path']:
                    continue
                # DV comes from the node which current dv passed, update it 
                if data["sender"] == self.dv[dst]['path'][0]:
                    self.updateDV(dst, [data["sender"]] + vec['path'], self.dv[data['sender']]['latency'] + vec['latency'])
                    hasUpdated = True
                # DV comes from different source, compare the latency, if lower, update
                else:
                    if dst not in self.dv or self.dv[dst]['latency'] > self.dv[data['sender']]['latency'] + vec['latency']:
                        self.updateDV(dst, [data["sender"]] + vec['path'], self.dv[data['sender']]['latency'] + vec['latency'])
                        hasUpdated = True
            
            # if DV has been updated, then send new dv to neighbors
            if hasUpdated:
                message = {
                    "sender": self.id,
                    "seq": self.seq,
                    "dv": self.dv
                }
                self.seq += 1
                self.send_to_neighbors(json.dumps(message))

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        if destination not in self.dv:
            return -1
        elif len(self.dv[destination]['path']) == 0:
            return destination
        else:
            return self.dv[destination]['path'][0]

    def updateDV(self, dst, path, latency):
        if dst in self.neighbors and self.neighbors[dst]['latency'] <= latency:
            new_path = {
                'path': [],
                'latency': self.neighbors[dst]['latency']
            }
        else:
            new_path = {
                'path': path,
                'latency': latency
            }

        self.dv[dst] = new_path
