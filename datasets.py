import math


def load_distance_matrix(filepath):
    """
    Loads distance matrix from a TSPLIB file.
    """
    dimension = 0
    in_weight_section = False
    weights = []

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("COMMENT"): 
                continue

            if line.startswith("NAME"): 
                continue 

            elif line.startswith("DIMENSION"):
                parts = line.split(':')
                if len(parts) > 1:
                    dimension = int(parts[1].strip())
                else:
                    dimension = int(line.split()[-1])

            elif line.startswith("EDGE_WEIGHT_SECTION"):
                in_weight_section = True

            elif line == "EOF":
                break

            elif in_weight_section:
                weights.extend([int(w) for w in line.split()])


    # --- Matrix Construction ---
    matrix = [[math.inf] * dimension for _ in range(dimension)]

    k = 0
    for i in range(dimension):
        for j in range(i + 1):
            dist = float(weights[k])
            if i != j:
                matrix[i][j] = dist
                matrix[j][i] = dist
            k += 1

    print(f"Loaded distances for {dimension} cities from {filepath}.")
    return matrix

