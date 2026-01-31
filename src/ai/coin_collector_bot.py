from ai.astar_bot import (
    AStarBot,
    BIRD_HITBOX_OFFSET_X,
    BIRD_HITBOX_OFFSET_Y,
    BIRD_HITBOX_WIDTH,
    BIRD_HITBOX_HEIGHT,
    PIPE_LOOKAHEAD_DISTANCE,
)
from entities.coin import Coin

# Search and performance constants
COIN_COLLECTOR_LOOKAHEAD = 10
MAX_COIN_SEARCH_DISTANCE = 40
MAX_COIN_DISTANCE_SQUARED = 1600

# Coin values and rewards
GOLD_COIN_VALUE = 15
REGULAR_COIN_VALUE = 5
COIN_REWARD_MULTIPLIER = 60.0
DISTANCE_OFFSET = 100

# Navigation and safety constants
GAP_DISTANCE_PENALTY = 5
FALLBACK_PENALTY = 3
SCREEN_MIDDLE_Y = 12
GAP_SAFETY_MARGIN = 1
BIRD_HEIGHT = 3

# Danger zone penalties
DANGER_ZONE_PENALTY = 35
CEILING_DANGER_ZONE = 2
FLOOR_DANGER_ZONE = 21
EXTREME_POSITION_PENALTY = 70

# Collision constants
COLLISION_PENALTY = 10000
SCREEN_TOP = 0
SCREEN_BOTTOM = 23


class CoinCollectorBot(AStarBot):
    """A* bot focused on collecting coins.

    Strategy: Balances coin collection with safety. Uses weighted heuristic
    to evaluate coin proximity, gap safety, and collision avoidance.
    """

    def __init__(self, game):
        super().__init__(game)
        self.lookahead_steps = COIN_COLLECTOR_LOOKAHEAD

    def heuristic(self, state, pipes, items):
        """
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
        collision_penalty = self._check_collision_penalty(state, pipes)
        if collision_penalty > 0:
            return collision_penalty

        total_score = 0
        next_pipe = self.get_next_pipe(state, pipes)

        # PRIORITY 1: Safety penalties (always apply)
        if next_pipe:
            gap_danger = self._calculate_gap_danger_penalty(state, next_pipe)
            total_score += gap_danger

            # If in danger zone, heavily prioritize safety over coins
            if gap_danger > 0:
                total_score += self._calculate_navigation_penalty(state, next_pipe) * 2
            else:
                # Only consider coins if we're safe
                coin_reward = self._calculate_coin_reward(state, items)
                total_score += coin_reward

                if coin_reward == 0:
                    total_score += self._calculate_navigation_penalty(state, next_pipe)
        else:
            coin_reward = self._calculate_coin_reward(state, items)
            total_score += coin_reward

            if coin_reward == 0:
                total_score += abs(state.y - SCREEN_MIDDLE_Y) * FALLBACK_PENALTY

        total_score += self._calculate_extreme_position_penalty(state)

        return total_score

    def _calculate_coin_reward(self, state, items):
        """Calculate reward for nearby coins (negative = good)."""
        coin_reward = 0
        bird_x = self.game.bird.x + state.x_offset

        for item in items:
            if not isinstance(item, Coin):
                continue

            x_dist = item.x - bird_x
            if x_dist < 0 or x_dist >= MAX_COIN_SEARCH_DISTANCE:
                continue

            y_dist = item.y - state.y
            dist_sq = x_dist * x_dist + y_dist * y_dist

            if dist_sq < MAX_COIN_DISTANCE_SQUARED:
                value = GOLD_COIN_VALUE if item.is_gold else REGULAR_COIN_VALUE
                coin_reward -= (
                    value * COIN_REWARD_MULTIPLIER / (dist_sq + DISTANCE_OFFSET)
                )

        return coin_reward

    def _calculate_navigation_penalty(self, state, next_pipe):
        """Calculate penalty for being far from safe navigation path."""
        if next_pipe:
            gap_middle = (next_pipe.y_top + next_pipe.y_bottom) * 0.5
            distance_from_middle = abs(state.y - gap_middle)
            return distance_from_middle * GAP_DISTANCE_PENALTY
        else:
            return abs(state.y - SCREEN_MIDDLE_Y) * FALLBACK_PENALTY

    def _calculate_gap_danger_penalty(self, state, pipe):
        """Calculate penalty for being too close to gap edges."""
        penalty = 0

        if state.y < pipe.y_top - GAP_SAFETY_MARGIN:
            penalty += (pipe.y_top - state.y) * DANGER_ZONE_PENALTY
        elif state.y + BIRD_HEIGHT > pipe.y_bottom + GAP_SAFETY_MARGIN:
            penalty += (state.y + BIRD_HEIGHT - pipe.y_bottom) * DANGER_ZONE_PENALTY

        return penalty

    def _calculate_extreme_position_penalty(self, state):
        """Calculate penalty for being too close to ceiling/floor."""
        if state.y < CEILING_DANGER_ZONE:
            return (CEILING_DANGER_ZONE - state.y) * EXTREME_POSITION_PENALTY
        elif state.y > FLOOR_DANGER_ZONE:
            return (state.y - FLOOR_DANGER_ZONE) * EXTREME_POSITION_PENALTY
        return 0

    def _check_collision_penalty(self, state, pipes):
        """
        Check if state would cause collision.

        Args:
            state: State to check
            pipes: List of pipes

        Returns:
            Large penalty if collision, 0 otherwise
        """
        if state.y <= SCREEN_TOP or state.y + BIRD_HITBOX_HEIGHT > SCREEN_BOTTOM:
            return COLLISION_PENALTY

        # Calculate bird hitbox matching bird.py and astar_bot.py
        hitbox_y = round(state.y + BIRD_HITBOX_OFFSET_Y)
        hitbox_y = max(0, min(hitbox_y, SCREEN_BOTTOM - int(BIRD_HITBOX_HEIGHT)))

        bird_hitbox = {
            "x": self.game.bird.x + BIRD_HITBOX_OFFSET_X,
            "y": hitbox_y,
            "width": BIRD_HITBOX_WIDTH,
            "height": BIRD_HITBOX_HEIGHT,
        }

        for pipe in pipes:
            if pipe.x + pipe.width < bird_hitbox["x"]:
                continue
            if pipe.x > bird_hitbox["x"] + PIPE_LOOKAHEAD_DISTANCE:
                break

            if self.check_collision(bird_hitbox, pipe):
                return COLLISION_PENALTY

        return 0
