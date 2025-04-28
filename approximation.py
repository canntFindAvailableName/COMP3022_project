import time
import os
import psutil
from utils import calculate_path_cost, build_mst

def mst_approximation(matrix):
    """
    Implements the MST-based 2-approximation algorithm for TSP.
    """
    start_time = time.perf_counter()
    process = psutil.Process(os.getpid()) # Get process for memory tracking
    initial_mem_rss = process.memory_info().rss
    max_memory_rss = initial_mem_rss

    num_cities = len(matrix)
    mst_edges, mst_cost = build_mst(matrix)

    # Track memory after MST build
    current_mem_rss = process.memory_info().rss
    if current_mem_rss > max_memory_rss: 
        max_memory_rss = current_mem_rss

    # Build adjacency list representation of the MST
    adj = {i: [] for i in range(num_cities)}
    for u, v in mst_edges:
        adj[u].append(v)
        adj[v].append(u)

    # Perform DFS traversal on MST to get preorder walk
    start_node_dfs = 0
    preorder_walk = []
    visited_dfs = set()
    stack = [start_node_dfs]

    while stack:
        u = stack.pop()
        if u not in visited_dfs:
             preorder_walk.append(u)
             visited_dfs.add(u)
             if u in adj:
                  for v in reversed(adj[u]):
                      if v not in visited_dfs:
                          stack.append(v)

    tour_path = preorder_walk 

    # Calculate cost of the approximate tour
    approx_cost = calculate_path_cost(tour_path, matrix)
    runtime = time.perf_counter() - start_time

    # Final memory check
    final_mem_rss = process.memory_info().rss
    if final_mem_rss > max_memory_rss: max_memory_rss = final_mem_rss
    max_memory_mb_absolute = max_memory_rss / (1024 * 1024)


    stats = {
        'runtime': runtime,
        'max_memory_absolute_mb': max_memory_mb_absolute,
        'final_cost': approx_cost,
        'mst_cost': mst_cost,
        'algorithm': 'mst_approx'
    }
    return approx_cost, tour_path, stats
