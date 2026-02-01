def uct_value(self, exploration: float = 1.414) -> float:
    """UCT formula for node selection"""
    if self.visits == 0:
        return float('inf')

    exploitation = self.total_reward / self.visits
    exploration_term = exploration * math.sqrt(
        math.log(self.parent.visits) / self.visits
    )

    return exploitation + exploration_term
