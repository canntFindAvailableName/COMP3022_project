import heapq
import time
import math
import os
import psutil
from utils import nearest_neighbor_heuristic, build_mst
from nodes import TSPNode

def calculate_lb_mst(node, matrix):
    """MST-based lower bound calculation for TSP nodes"""
    num_cities = len(matrix)
    start = node.path[0]
    current = node.current_city
    unvisited = [i for i in range(num_cities) if i not in node.visited]

    if not unvisited:
        return node.cost + matrix[current][start] if matrix[current][start] != math.inf else math.inf

    lb = node.cost
    min_out = min(matrix[current][c] for c in unvisited)
    min_back = min(matrix[c][start] for c in unvisited)
    
    if min_out == math.inf or min_back == math.inf:
        return math.inf

    lb += min_out + min_back

    if len(unvisited) > 1:
        sub_size = len(unvisited)
        sub_matrix = [[math.inf]*sub_size for _ in range(sub_size)]
        for i, r in enumerate(unvisited):
            for j, c in enumerate(unvisited):
                if i != j and r < len(matrix) and c < len(matrix[r]):
                    sub_matrix[i][j] = matrix[r][c]
                elif i != j:
                    print("Matrix index warning at", (r, c))
                    sub_matrix[i][j] = math.inf
        
        _, mst_cost = build_mst(sub_matrix)
        if mst_cost == math.inf:
            return math.inf
        lb += mst_cost
    
    return lb

def branch_and_bound(matrix, lb_func, strategy, time_limit=None):
    """TSP solver using branch and bound algorithm"""
    proc = psutil.Process(os.getpid())
    start_time = time.perf_counter()
    mem_peak = mem_initial = proc.memory_info().rss

    n = len(matrix)
    if n <= 1:
        stats = {
            'runtime': 0, 'max_memory_absolute_mb': mem_initial/(1024 * 1024),
            'nodes_explored':0, 'nodes_generated':1, 'pruned_count':0,
            'initial_upper_bound':0, 'final_cost':0, 
            'lb_function':lb_func, 'strategy':strategy, 'algorithm':'bnb'
        }
        return 0, [0]*n, stats

    lb_function = calculate_lb_mst  # Only MST supported

    best_cost, init_path = nearest_neighbor_heuristic(matrix)
    best_path = init_path or list(range(n))
    print(f"Initial upper bound: {best_cost}")

    start_node = TSPNode(
        path=[0], cost=0, 
        lower_bound=0, 
        visited={0}
    )
    start_node.lower_bound = lb_function(start_node, matrix)

    if start_node.lower_bound == math.inf:
        print("Initial node is invalid")
        stats = stats_template(proc, start_time, mem_peak, best_cost, 1, lb_func, strategy)
        stats.update({'nodes_explored':0, 'pruned_count':0})
        return math.inf, [], stats

    frontier = []
    nodes_gen = 1
    nodes_exp = 0
    pruned = 0
    
    # Initialize frontier based on search strategy
    if strategy == 'best_first':
        heapq.heappush(frontier, start_node)
    else:
        frontier.append(start_node)

    while frontier:
        if time_limit and (time.perf_counter() - start_time) > time_limit:
            print("Time limit reached")
            break

        current = get_next_node(frontier, strategy)
        nodes_exp += 1

        # Memory tracking
        current_mem = proc.memory_info().rss
        if current_mem > mem_peak:
            mem_peak = current_mem

        if current.lower_bound >= best_cost:
            pruned += 1
            continue

        if len(current.path) == n:
            final_cost = current.cost + matrix[current.current_city][0]
            if final_cost < best_cost and final_cost != math.inf:
                best_cost = final_cost
                best_path = current.path
                print(f"New best: {best_cost} (explored {nodes_exp})")
            continue

        for next_city in (c for c in range(n) if c not in current.visited):
            cost = matrix[current.current_city][next_city]
            if cost == math.inf:
                continue

            new_cost = current.cost + cost
            if new_cost >= best_cost:
                pruned +=1
                continue

            new_path = current.path + [next_city]
            new_visited = current.visited | {next_city}
            child = TSPNode(
                path=new_path, cost=new_cost,
                lower_bound=0, visited=new_visited
            )
            child.lower_bound = lb_function(child, matrix)
            nodes_gen += 1

            if child.lower_bound < best_cost:
                add_to_frontier(frontier, child, strategy)
            else:
                pruned +=1

    stats = stats_template(proc, start_time, mem_peak, best_cost, nodes_gen, lb_func, strategy)
    stats.update({
        'nodes_explored': nodes_exp,
        'pruned_count': pruned,
        'initial_upper_bound': nearest_neighbor_heuristic(matrix)[0]
    })
    return best_cost if best_cost != math.inf else -1, best_path, stats

def get_next_node(frontier, strategy):
    """Node selection helper based on search strategy"""
    if strategy == 'best_first':
        return heapq.heappop(frontier)
    elif strategy == 'dfs':
        return frontier.pop()
    elif strategy == 'bfs':
        return frontier.pop(0)

def add_to_frontier(frontier, node, strategy):
    """Frontier insertion helper"""
    if strategy == 'best_first':
        heapq.heappush(frontier, node)
    else:
        frontier.append(node)

def stats_template(proc, start, mem_peak, best, generated, lb, strat):
    """Helper for stats dictionary creation"""
    return {
        'runtime': time.perf_counter() - start,
        'max_memory_absolute_mb': mem_peak/(1024 * 1024),
        'nodes_generated': generated,
        'final_cost': best if best != math.inf else -1,
        'lb_function': lb,
        'strategy': strat,
        'algorithm': 'bnb'
    }