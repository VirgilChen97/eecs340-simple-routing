from simulator.node import Node
import json


class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.latestSeqList = {}
        self.graph = {}
        self.graph[self.id] = {}

    # Return a string
    def __str__(self):
        arr = sorted(self.graph.items(), key = lambda item:item[0])
        res = {}
        for i in range(len(arr)):
            res[arr[i][0]] = sorted(arr[i][1].items(), key = lambda item:item[0])

        return str(self.id) + ":" + str(res) + "\nseq:" + str(self.latestSeqList)

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        
        # If adding a link
        if latency >= 0:
            self.graph[self.id][neighbor] = latency
            if neighbor in self.graph:
                self.graph[neighbor][self.id] = latency
            else:
                self.graph[neighbor] = {self.id:latency}
        # if deleting a link
        else:
            del self.graph[self.id][neighbor]
            if neighbor in self.graph:
                del self.graph[neighbor][self.id]

        link = frozenset([self.id, neighbor])
        if link not in self.latestSeqList:
            self.latestSeqList[link] = -1

        self.latestSeqList[link] += 1
        # send update of the link to old neighbors
        for old_neighbor in self.graph[self.id].keys():
            if old_neighbor != neighbor:
                message = {
                    "link": [self.id, neighbor],
                    "sender": self.id,
                    "latency": latency,
                    "seq": self.latestSeqList[link]
                }
                self.send_to_neighbor(old_neighbor, json.dumps({"data":[message]}))

        # send entire graph to new neighbor
        graph_dump = []
        for start, ends in self.graph.items():
            for end, old_latency in ends.items():
                graph_dump.append({
                    "link": [start, end],
                    "sender": self.id,
                    "latency": old_latency,
                    "seq": self.latestSeqList[frozenset([start, end])]
                })
        self.send_to_neighbor(neighbor, json.dumps({"data":graph_dump}))


    # Fill in this function
    def process_incoming_routing_message(self, m):
        data = json.loads(m)
       
        for info in data["data"]:
            # discard message about the node itself
            if self.id == info["link"][0] or self.id == info["link"][1]:
                continue

            link = frozenset([info["link"][0], info["link"][1]])
            # Received message is newest one
            if link not in self.latestSeqList or info["seq"] > self.latestSeqList[link]: 

                # Add link from a direction
                if info["link"][0] not in self.graph:
                    self.graph[info["link"][0]] = {}
                if info["latency"] >= 0:
                    self.graph[info["link"][0]][info["link"][1]] = info["latency"]
                else:
                    del self.graph[info["link"][0]][info["link"][1]]

                # Add link from another direction
                if info["link"][1] not in self.graph:
                    self.graph[info["link"][1]] = {}
                if info["latency"] >= 0:
                    self.graph[info["link"][1]][info["link"][0]] = info["latency"]
                else: 
                    del self.graph[info["link"][1]][info["link"][0]]

                # Update stored newest seq
                self.latestSeqList[link] = info["seq"]

                # relay the message
                old_sender = info["sender"]
                info["sender"] = self.id
                for neighbor in self.graph[self.id].keys():
                    if neighbor != old_sender:
                        self.send_to_neighbor(neighbor, json.dumps({"data": [info]}))

            # The received message is older one
            elif info["seq"] < self.latestSeqList[link]:
                # Send newest info to sender 
                message = {
                    "link": [info["link"][0], info["link"][1]],
                    "sender": self.id,
                    "seq": self.latestSeqList[link]
                }
                if info["link"][0] in self.graph and info["link"][1] in self.graph[info["link"][0]]:
                    message["latency"] = self.graph[info["link"][0]][info["link"][1]]
                else:
                    message["latency"] = -1
                self.send_to_neighbor(info["sender"], json.dumps({"data": [message]}))

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # ============Initialization===============
        # Current shortest distance
        d = {}
        # Current previous hop
        prev = {} 
        # 0 latency to self
        d[self.id] = 0
        # Initialize latency to neighbor
        for neighbor, latency in self.graph[self.id].items():
            d[neighbor] = latency
            prev[neighbor] = self.id
        # Node that already found shortest path
        S = set()
        # Node haven't found shortest path
        Q = set(self.graph.keys())

        while len(Q) != 0:
            d_exclude_S = {key: value for key, value in d.items() if key not in S}
            u = min(d_exclude_S, key=d_exclude_S.get)
            S.add(u)
            Q.remove(u)
            for neighbor, latency in self.graph[u].items():
                if neighbor not in d or d[neighbor] >= d[u] + latency:
                    d[neighbor] = d[u] + latency
                    prev[neighbor] = u

        if destination not in prev:
            return -1
        else:
            next_hop = destination
            while prev[next_hop] != self.id:
                next_hop = prev[next_hop]

            return next_hop
