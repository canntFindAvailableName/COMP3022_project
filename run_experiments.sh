#!/bin/bash

# --- config ---
PYTHON_SCRIPT="tsp.py" 
DATA_DIR="tsp_data"          
RESULTS_DIR="results"         
TIME_LIMIT=600             


DATASETS=(
    "gr17.tsp" 
    "gr21.tsp"
    "gr24.tsp"
    "gr48.tsp"
    "fri26.tsp"
)

mkdir -p "${RESULTS_DIR}"

# --- exp ---
for dataset in "${DATASETS[@]}"; do
    dataset_name=$(basename "${dataset}" .tsp)
    input_file="${DATA_DIR}/${dataset}"

    echo "--- Running experiments for ${dataset_name} ---"

    # --- 1. Branch and Bound ---
    # B&B: MST Lower Bound, Best-First Search
    echo "Running B&B (MST, Best-First) for ${dataset_name}..."
    python "${PYTHON_SCRIPT}" "${input_file}" --algorithm bnb --lb mst --strategy best_first --timelimit ${TIME_LIMIT} --output "${RESULTS_DIR}/${dataset_name}_bnb_mst_bestfirst.txt"

    # B&B: MST Lower Bound, Depth-First Search
    echo "Running B&B (MST, DFS) for ${dataset_name}..."
    python "${PYTHON_SCRIPT}" "${input_file}" --algorithm bnb --lb mst --strategy dfs --timelimit ${TIME_LIMIT} --output "${RESULTS_DIR}/${dataset_name}_bnb_mst_dfs.txt"

    # --- 2. MST Approximation Algorithm ---
    echo "Running MST Approximation for ${dataset_name}..."
    python "${PYTHON_SCRIPT}" "${input_file}" --algorithm mst_approx --timelimit ${TIME_LIMIT} --output "${RESULTS_DIR}/${dataset_name}_mst_approx.txt"


    # --- 3. Hill Climbing (2-opt) ---
    echo "Running Hill Climbing (2-opt) for ${dataset_name}..."
    python "${PYTHON_SCRIPT}" "${input_file}" --algorithm hc_2opt --timelimit ${TIME_LIMIT} --output "${RESULTS_DIR}/${dataset_name}_hc_2opt.txt"


    # --- 4. Nearest Neighbor (Baseline Heuristic) ---
    echo "Running Nearest Neighbor for ${dataset_name}..."
    python "${PYTHON_SCRIPT}" "${input_file}" --algorithm nn --timelimit ${TIME_LIMIT} --output "${RESULTS_DIR}/${dataset_name}_nn.txt"


    echo "--- Finished experiments for ${dataset_name} ---"
    echo ""

done

