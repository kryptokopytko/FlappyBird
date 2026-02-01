def compute_novelty(self, behavior: Tuple[float, ...], k: int = 15) -> float:
    """Compute novelty as average distance to k-nearest neighbors"""
    if len(self.individuals) < k:
        return float('inf')

    distances = [
        euclidean_distance(behavior, ind.behavior)
        for ind in self.individuals
    ]

    k_nearest = sorted(distances)[:k]
    return sum(k_nearest) / k

def euclidean_distance(b1, b2):
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(b1, b2)))
