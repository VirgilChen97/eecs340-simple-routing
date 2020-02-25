def get_next_hop(graph, src, dst):
    # ============Initialization===============
    # Current shortest distance
    d = {}
    # Current previous hop
    prev = {} 
    # 0 latency to self
    d[src] = 0
    # Initialize latency to neighbor
    for neighbor, latency in graph[src].items():
        d[neighbor] = latency
        prev[neighbor] = src
    # Node that already found shortest path
    S = set()
    # Node haven't found shortest path
    Q = set(graph.keys())

    while len(Q) != 0:
        d_exclude_S = {key: value for key, value in d.items() if key not in S}
        u = min(d_exclude_S, key=d_exclude_S.get)
        S.add(u)
        Q.remove(u)
        for neighbor, latency in graph[u].items():
            if neighbor not in d or d[neighbor] >= d[u] + latency:
                d[neighbor] = d[u] + latency
                prev[neighbor] = u

    next_hop = dst
    while prev[next_hop] != src:
        next_hop = prev[next_hop]

    return next_hop

    

graph = {
    1: {2:3, 3:1},
    2: {1:3, 3:1, 4:2},
    3: {1:1, 2:1, 4:3},
    4: {2:2, 3:3}
}

print(get_next_hop(graph, 1, 4))
