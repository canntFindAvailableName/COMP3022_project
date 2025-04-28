import math

def calculate_path_cost(path, matrix):
    """Calculates the total cost of a given tour path."""
    cost = 0
    num_cities = len(path)
    if num_cities < 2:
        return 0
    for i in range(num_cities - 1):
        u, v = path[i], path[i+1]
        dist = matrix[u][v]
        if dist == math.inf: 
            return math.inf
        cost += dist
    # Add cost to return to start
    last_city, start_city = path[-1], path[0]
    dist_to_start = matrix[last_city][start_city]
    if dist_to_start == math.inf: 
        return math.inf
    cost += dist_to_start
    return cost

def nearest_neighbor_heuristic(matrix, start_node=0):
    """
    Calculates an initial upper bound using the Nearest Neighbor heuristic.
    """
    num_cities = len(matrix)
    if num_cities == 0: return 0, []
    if num_cities == 1: return 0, [0]

    current_city = start_node
    path = [current_city]
    visited = {current_city}
    total_cost = 0

    while len(visited) < num_cities:
        nearest_neighbor = -1
        min_dist = math.inf
        for neighbor in range(num_cities):
            if neighbor not in visited:
                # Check if matrix[current_city] exists and neighbor index is valid
                if current_city < len(matrix) and neighbor < len(matrix[current_city]):
                    dist = matrix[current_city][neighbor]
                    if dist < min_dist:
                        min_dist = dist
                        nearest_neighbor = neighbor

        if nearest_neighbor != -1:
            total_cost += min_dist
            current_city = nearest_neighbor
            path.append(current_city)
            visited.add(current_city)

    # Check indices
    if current_city < len(matrix) and start_node < len(matrix[current_city]):
        cost_to_start = matrix[current_city][start_node]
        if cost_to_start != math.inf:
            total_cost += cost_to_start

    return total_cost, path


def build_mst(matrix):
    """
    Builds a Minimum Spanning Tree using Prim's algorithm.
    """
    num_nodes = len(matrix)
    if num_nodes == 0: return [], 0
    if num_nodes == 1: return [], 0

    key = [math.inf] * num_nodes    # Min edge weight to connect node to MST
    parent = [-1] * num_nodes       
    mst_set = [False] * num_nodes   # True if node is in MST

    # Start Prim's from node 0
    key[0] = 0
    total_mst_cost = 0
    mst_edges = []
    nodes_in_mst = 0

    # Use a simple O(V^2) approach for finding min key node
    for _ in range(num_nodes):
        min_key = math.inf
        u = -1 
        for v in range(num_nodes):
            if not mst_set[v] and key[v] < min_key:
                min_key = key[v]
                u = v

        if u == -1:
            break 

        if min_key == math.inf:
            break


        mst_set[u] = True
        total_mst_cost += min_key 
        nodes_in_mst += 1
        if parent[u] != -1: 
            mst_edges.append(tuple(sorted((parent[u], u))))

        # Update keys of adjacent vertices of u
        for v in range(num_nodes):
            cost_uv = matrix[u][v]
            if not mst_set[v] and cost_uv != math.inf and cost_uv < key[v]:
                key[v] = cost_uv
                parent[v] = u

    return mst_edges, total_mst_cost
