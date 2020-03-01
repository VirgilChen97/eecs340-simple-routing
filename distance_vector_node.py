from simulator.node import Node
import json


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.dv = {str(self.id): {'path': [], 'latency': 0}}
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
        if latency > -1:
            if neighbor not in self.neighbors:
                self.neighbors[neighbor] = {
                    'seq': -1,
                    'latency': latency
                }
            else:
                self.neighbors[neighbor]['latency'] = latency
        else:
            del self.neighbors[neighbor]
        self.updateDV()

    # Fill in this function

    def process_incoming_routing_message(self, m):
        data = json.loads(m)
        # Received message should be the newest one
        if data['sender'] in self.neighbors and self.neighbors[data['sender']]['seq'] < data['seq']:
            # update seq
            self.neighbors[data['sender']]['seq'] = data['seq']
            self.neighbors[data['sender']]['dv'] = data['dv']
            self.updateDV()

    # Return a neighbor, -1 if no path to destination

    def get_next_hop(self, destination):
        if str(destination) not in self.dv:
            return -1
        else:
            return int(self.dv[str(destination)]['path'][0])

    def updateDV(self):
        # neighbor:{
        #   (neighborId):{
        #       'latency': int,
        #       'dv': object
        #       'seq': int
        #   }
        # }

        # dv: {
        #   (dstId):{
        #       'path': [],
        #       'latency': int
        #   }
        # }

        new_dv = {str(self.id): {'path': [], 'latency': 0}}
                
        for neighbor, detail in self.neighbors.items():
            if 'dv' not in detail:
                if str(neighbor) not in new_dv or new_dv[str(neighbor)]['latency'] > detail['latency']:
                    new_dv[str(neighbor)] = {
                        'path': [neighbor],
                        'latency': detail['latency']
                    }
            else:
                for dst, route in detail['dv'].items():
                    if self.id not in route['path']:
                        if dst not in new_dv or new_dv[dst]['latency'] > route['latency'] + detail['latency']:
                            new_dv[str(dst)] = {
                                'path': [neighbor] + route['path'],
                                'latency': route['latency'] + detail['latency']
                            }
        isUpdated = False
        if len(new_dv.keys())!=len(self.dv.keys()):
            isUpdated = True

        for key, value in new_dv.items():
            if key not in self.dv:
                isUpdated = True
                break
            else:
                if value['latency'] != self.dv[key]['latency'] or value['path'] != self.dv[key]['path']:
                    isUpdated = True
                    break
        
        if isUpdated:
            self.dv = new_dv
            message = {
                    "sender": self.id,
                    "seq": self.seq,
                    "dv": self.dv
                }
            self.seq += 1
            self.send_to_neighbors(json.dumps(message))
