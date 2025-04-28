import time
import math
import os
import psutil
import random
from utils import calculate_path_cost, nearest_neighbor_heuristic

def swap_2opt(path, i, j):
    if i > j:
        i, j = j, i
    return path[:i+1] + path[j:i:-1] + path[j+1:]

def hill_climbing_2opt(matrix, init_path=None, max_iters=None, timeout=None):
    start = time.perf_counter()
    proc = psutil.Process(os.getpid())
    mem_peak = mem_start = proc.memory_info().rss
    n = len(matrix)
    
    if n <= 2:
        path = list(range(n))
        cost = calculate_path_cost(path, matrix) if n > 0 else 0
        stats = {
            'runtime': time.perf_counter()-start,
            'max_memory_absolute_mb': mem_start/(1024 * 1024),
            'iterations': 0,
            'algorithm': 'hc_2opt'
        }
        return cost, path, stats

    # Initialize solution
    if init_path:
        best_path = init_path[:]
    else:
        try:
            _, best_path = nearest_neighbor_heuristic(matrix)
            if not best_path:
                best_path = list(range(n))
                random.shuffle(best_path)
        except:
            best_path = list(range(n))
            random.shuffle(best_path)
    
    current_cost = calculate_path_cost(best_path, matrix)
    if current_cost == math.inf:
        stats = {
            'runtime': time.perf_counter()-start,
            'max_memory_absolute_mb': mem_start/(1024 * 1024),
            'iterations': 0,
            'algorithm': 'hc_2opt'
        }
        return math.inf, [], stats

    print(f"Starting cost: {current_cost:.1f}")
    iterations = 0
    improved = True

    while improved:
        if timeout and (time.perf_counter() - start) > timeout:
            print(f"Timeout after {timeout}s")
            break
        if max_iters and iterations >= max_iters:
            print(f"Max iterations {max_iters} reached")
            break

        improved = False
        best_delta = 0
        swap_indices = None

        # Explore possible swaps
        for i in range(n):
            for j in range(i+2, n):
                a, b = best_path[i], best_path[(i+1)%n]
                c, d = best_path[j], best_path[(j+1)%n]
                
                old_cost = matrix[a][b] + matrix[c][d]
                new_cost = matrix[a][c] + matrix[b][d]
                
                if old_cost == math.inf or new_cost == math.inf:
                    continue
                
                delta = new_cost - old_cost
                if delta < best_delta:
                    best_delta = delta
                    swap_indices = (i, j)
                    improved = True

        # Apply best swap found
        if improved:
            best_path = swap_2opt(best_path, *swap_indices)
            current_cost += best_delta
            iterations += 1

        # Update memory usage every 50 iterations
        if iterations % 50 == 0:
            current_mem = proc.memory_info().rss
            if current_mem > mem_peak:
                mem_peak = current_mem

    # Final memory check
    final_mem = proc.memory_info().rss
    if final_mem > mem_peak:
        mem_peak = final_mem

    return current_cost, best_path, {
        'runtime': time.perf_counter() - start,
        'max_memory_absolute_mb': mem_peak/(1024 * 1024),
        'iterations': iterations,
        'final_cost': current_cost,
        'algorithm': 'hc_2opt'
    }