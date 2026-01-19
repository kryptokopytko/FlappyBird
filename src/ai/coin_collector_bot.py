"""Coin-collecting A* bot that seeks coins while avoiding death."""

from ai.astar_bot import AStarBot
from entities.coin import Coin


class CoinCollectorBot(AStarBot):
    """A* bot focused on collecting coins."""

    def __init__(self, game):
        """Initialize CoinCollectorBot."""
        super().__init__(game)
        self.lookahead_steps = 6  # Reduced for performance

    def heuristic(self, state, pipes, items):
        """
        Coin-collecting heuristic.

        Rewards:
        - Being close to coins (especially gold coins)
        - Collecting more valuable coins

        Penalizes:
        - Collision risk (still avoid death)
        - Distance from gap middle if no coins nearby

        Args:
            state: Current state
            pipes: List of pipes
            items: List of items (coins, powerups, debuffs)

        Returns:
            Heuristic score (lower is better, negative = reward)
        """
        total_score = 0

        # 1. Base collision safety check
        collision_penalty = self._check_collision_penalty(state, pipes)
        if collision_penalty > 0:
            return collision_penalty  # Collision = very bad, override everything

        # 2. Reward being close to coins (optimized - no sqrt, use dist_sq directly)
        coin_reward = 0
        bird_x = self.game.bird.x + state.x_offset

        # Direct iteration - avoid list comprehension overhead
        for item in items:
            # Quick type check
            if not isinstance(item, Coin):
                continue

            x_dist = item.x - bird_x
            if x_dist < 0 or x_dist >= 30:
                continue

            # Calculate squared distance only for nearby items
            y_dist = item.y - state.y
            dist_sq = x_dist * x_dist + y_dist * y_dist

            # Only consider coins within reasonable range (30^2 = 900)
            if dist_sq < 900:
                # Gold coins are worth 3x more (15 vs 5 points)
                value = 15 if item.is_gold else 5

                # Reward inversely proportional to SQUARED distance (no sqrt!)
                # Using dist_sq directly is much faster
                coin_reward -= value * 100.0 / (dist_sq + 100)

        total_score += coin_reward

        # 3. Get next pipe once (cache it)
        next_pipe = self.get_next_pipe(state, pipes)

        # 4. If no coins nearby, fall back to safe navigation
        if coin_reward == 0:
            if next_pipe:
                gap_middle = (next_pipe.y_top + next_pipe.y_bottom) * 0.5
                distance_from_middle = abs(state.y - gap_middle)
                total_score += distance_from_middle * 5
            else:
                # No pipes - stay in middle
                total_score += abs(state.y - 12) * 3

        # 5. Penalize being outside gap range (don't die for coins)
        if next_pipe:
            if state.y < next_pipe.y_top - 1:
                # Too high - danger zone
                total_score += (next_pipe.y_top - state.y) * 30
            elif state.y + 3 > next_pipe.y_bottom + 1:
                # Too low - danger zone
                total_score += (state.y + 3 - next_pipe.y_bottom) * 30

        # 6. Penalize extreme positions (ceiling/floor)
        if state.y < 2:
            total_score += (2 - state.y) * 80
        elif state.y > 21:
            total_score += (state.y - 21) * 80

        return total_score

    def _check_collision_penalty(self, state, pipes):
        """
        Check if state would cause collision.

        Args:
            state: State to check
            pipes: List of pipes

        Returns:
            Large penalty if collision, 0 otherwise
        """
        # Check ceiling/floor
        if state.y <= 0 or state.y + 3 > 23:
            return 10000

        # Check pipe collisions
        bird_hitbox = {
            'x': self.game.bird.x + 1,
            'y': round(state.y),
            'width': 3,
            'height': 3
        }

        for pipe in pipes:
            # Only check nearby pipes
            if pipe.x + pipe.width < bird_hitbox['x']:
                continue
            if pipe.x > bird_hitbox['x'] + 20:
                break

            if self.check_collision(bird_hitbox, pipe):
                return 10000

        return 0
