class TSPNode:
    """Represents a node in the B&B search tree."""
    def __init__(self, path, cost, lower_bound, visited):
        self.path = path              
        self.cost = cost              
        self.lower_bound = lower_bound 
        self.visited = visited        
        self.current_city = path[-1] if path else -1

    def __lt__(self, other):
        return self.lower_bound < other.lower_bound

    def __eq__(self, other):
        return self.lower_bound == other.lower_bound