import time
import argparse
import math
import psutil
from datasets import load_distance_matrix
from approximation import mst_approximation
from hill_climbing import hill_climbing_2opt
from branch_bound import branch_and_bound
from utils import nearest_neighbor_heuristic

def run_algorithm(args, matrix):
    """Execute selected algorithm and return results"""
    algo = args.algorithm
    if algo == 'bnb':
        return branch_and_bound(matrix, args.lb, args.strategy, args.timelimit)
    elif algo == 'mst_approx':
        return mst_approximation(matrix)
    elif algo == 'hc_2opt':
        return hill_climbing_2opt(matrix, None, args.hc_max_iter, args.timelimit)
    elif algo == 'nn':
        start = time.perf_counter()
        proc = psutil.Process()
        mem = proc.memory_info().rss
        cost, path = nearest_neighbor_heuristic(matrix)
        stats = {
            'runtime': time.perf_counter() - start,
            'max_memory_absolute_mb': proc.memory_info().rss/(1024 * 1024),
            'final_cost': cost,
            'algorithm': 'nn'
        }
        return cost, path, stats
    return math.inf, [], {}

def format_path(path):
    """Convert 0-based indices to 1-based for output"""
    return [i+1 for i in path] if path else []

def write_results(args, stats, cost, path, filename):
    """Save results to output file"""
    with open(filename, 'w') as f:
        f.write(f"Algorithm: {stats.get('algorithm')}\n")
        f.write(f"Input: {args.input_file}\n")
        
        if stats.get('algorithm') == 'bnb':
            f.write(f"LB: {stats.get('lb_function')}, Strategy: {stats.get('strategy')}\n")
        
        if cost not in (math.inf, -1):
            f.write(f"Cost: {cost:.4f}\nPath: {format_path(path)}\n")
        else:
            f.write("No valid solution\n")
        
        f.write("\nStatistics:\n")
        f.write(f"Runtime: {stats.get('runtime',0):.3f}s\n")
        f.write(f"Memory: {stats.get('max_memory_absolute_mb',0):.1f} MB\n")
        
        for metric in ['nodes_explored', 'nodes_generated', 'pruned_count',
                      'initial_upper_bound', 'iterations', 'mst_cost']:
            if metric in stats:
                val = f"{stats[metric]:.4f}" if isinstance(stats[metric], float) else stats[metric]
                f.write(f"{metric.replace('_', ' ').title()}: {val}\n")

def display_results(stats, cost, path):
    """Print results to console"""
    print(f"\nAlgorithm Results: {stats.get('algorithm')}")
    if cost not in (math.inf, -1):
        print(f"Optimal Cost: {cost:.2f}")
        print(f"Solution Path: {format_path(path)}")
    else:
        print("No valid solution found")
    
    print("\nPerformance Metrics:")
    print(f"Time Elapsed: {stats.get('runtime',0):.2f}s")
    print(f"Peak Memory: {stats.get('max_memory_absolute_mb',0):.1f} MB")
    
    if 'nodes_explored' in stats:
        print(f"Explored Nodes: {stats['nodes_explored']}")
    if 'iterations' in stats:
        print(f"Optimization Steps: {stats['iterations']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TSP Solver')
    parser.add_argument("input_file", help="TSP data file")
    parser.add_argument("--algorithm", choices=['bnb','mst_approx','hc_2opt','nn'], 
                       default='bnb')
    parser.add_argument("--output_file", help="Save results path")
    parser.add_argument("--lb", choices=['simple','mst'], default='mst')
    parser.add_argument("--strategy", choices=['best_first','dfs','bfs'], default='best_first')
    parser.add_argument("--hc_max_iter", type=int)
    parser.add_argument("--timelimit", type=float)
    args = parser.parse_args()

    matrix = load_distance_matrix(args.input_file)
    cost, path, stats = run_algorithm(args, matrix)
    
    display_results(stats, cost, path)
    
    if args.output_file:
        write_results(args, stats, cost, path, args.output_file)
        print(f"\nOutput saved to {args.output_file}")