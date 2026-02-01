def heuristic(self, state, pipes, items):
    """A* heuristic for coin collector bot"""
    # f(state) = g(state) + h(state)
    h_score = 0

    # Safety penalty
    collision_penalty = self._check_collision_penalty(state, pipes)
    if collision_penalty > 0:
        return collision_penalty

    # Coin rewards (negative = good)
    coin_reward = self._calculate_coin_reward(state, items)
    h_score += coin_reward

    # Gap navigation penalty
    h_score += self._calculate_navigation_penalty(state, next_pipe)

    return h_score
