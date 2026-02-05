"""A* pathfinding bot base class."""

import heapq

# A* algorithm constants
DEFAULT_LOOKAHEAD_STEPS = 7
MAX_SEARCH_ITERATIONS = 80
EARLY_TERMINATION_STEPS = 6
EARLY_TERMINATION_SCORE = 15

# Physics simulation constants
SIMULATION_DT = 1.0 / 60.0
GRAVITY = 1.0
JUMP_FORCE = -22
TERMINAL_VELOCITY = 40.0

# Collision detection constants
SCREEN_TOP = 0
SCREEN_BOTTOM = 23
BIRD_HITBOX_WIDTH = 4.0
BIRD_HITBOX_HEIGHT = 2.4
BIRD_HITBOX_OFFSET_X = 0.5
BIRD_HITBOX_OFFSET_Y = 0.3
PIPE_LOOKAHEAD_DISTANCE = 20
SCREEN_MIDDLE_Y = 12
PIPE_HITBOX_INSET = 1
PIPE_CAP_INSET = 1
PIPE_CAP_HEIGHT = 2
PIPE_TOP_MARGIN = 1
PIPE_BOTTOM_OFFSET = 2
PIPE_TOP_OFFSET = 3

# State discretization for closed set
STATE_Y_PRECISION = 0.1
STATE_VELOCITY_PRECISION = 0.1
STATE_X_BUCKET_SIZE = 5


class State:
    def __init__(self, y, velocity, x_offset=0):
        self.y = y
        self.velocity = velocity
        self.x_offset = x_offset

    def __lt__(self, other):
        return self.y < other.y


class AStarBot:
    JUMP = True
    NO_JUMP = False

    def __init__(self, game):
        self.game = game
        self.lookahead_steps = DEFAULT_LOOKAHEAD_STEPS

    def decide_action(self):
        """True if should jump, False otherwise"""
        bird = self.game.bird
        pipes = self.game.pipes
        items = self.game.items

        current_state = State(bird.y, bird.velocity, 0)

        return self.a_star_search(current_state, pipes, items)

    def a_star_search(self, current_state, pipes, items):
        """
        A* pathfinding to find optimal action sequence.

        Args:
            current_state: Current bird state (y, velocity)
            pipes: List of upcoming pipes
            items: List of coins/powerups/debuffs

        Returns:
            Best action (JUMP or NO_JUMP) for current frame
        """
        open_set = [(0, 0, current_state, [])]
        closed_set = set()

        iterations = 0

        while open_set and iterations < MAX_SEARCH_ITERATIONS:
            iterations += 1

            f_score, g_score, state, actions = heapq.heappop(open_set)

            if len(actions) >= self.lookahead_steps:
                return actions[0] if actions else self.NO_JUMP

            if (
                len(actions) >= EARLY_TERMINATION_STEPS
                and f_score < EARLY_TERMINATION_SCORE
            ):
                return actions[0] if actions else self.NO_JUMP

            state_key = (
                round(state.y / STATE_Y_PRECISION) * STATE_Y_PRECISION,
                round(state.velocity / STATE_VELOCITY_PRECISION)
                * STATE_VELOCITY_PRECISION,
                state.x_offset // STATE_X_BUCKET_SIZE,
            )
            if state_key in closed_set:
                continue
            closed_set.add(state_key)

            for action in [self.JUMP, self.NO_JUMP]:
                new_state = self.predict_next_state(state, action)

                if self.is_dead(new_state, pipes):
                    continue

                new_actions = actions + [action]
                new_g_score = g_score + 1
                h_score = self.heuristic(new_state, pipes, items)
                new_f_score = new_g_score + h_score

                heapq.heappush(
                    open_set, (new_f_score, new_g_score, new_state, new_actions)
                )

        return self.fallback_action(current_state, pipes)

    def predict_next_state(self, state, action):
        """
        Predict next state given current state and action.

        Args:
            state: Current state
            action: Action to take (JUMP or NO_JUMP)

        Returns:
            New State after action
        """
        scroll_speed = self.game.scroll_speed

        new_velocity = state.velocity
        if action == self.JUMP:
            new_velocity = JUMP_FORCE
        else:
            new_velocity += GRAVITY
            new_velocity = min(new_velocity, TERMINAL_VELOCITY)

        new_y = state.y + new_velocity * SIMULATION_DT
        new_x_offset = state.x_offset + scroll_speed * SIMULATION_DT

        return State(new_y, new_velocity, new_x_offset)

    def is_dead(self, state, pipes):
        if state.y <= SCREEN_TOP or state.y + BIRD_HITBOX_HEIGHT > SCREEN_BOTTOM:
            return True

        hitbox_y = round(state.y + BIRD_HITBOX_OFFSET_Y)
        hitbox_y = max(0, min(hitbox_y, SCREEN_BOTTOM - int(BIRD_HITBOX_HEIGHT)))

        bird_hitbox = {
            "x": self.game.bird.x + state.x_offset + BIRD_HITBOX_OFFSET_X,
            "y": hitbox_y,
            "width": BIRD_HITBOX_WIDTH,
            "height": BIRD_HITBOX_HEIGHT,
        }

        for pipe in pipes:
            if pipe.x + pipe.width < bird_hitbox["x"]:
                continue
            if pipe.x > bird_hitbox["x"] + PIPE_LOOKAHEAD_DISTANCE:
                continue

            if self.check_collision(bird_hitbox, pipe):
                return True

        return False

    def bounding_box_collision(self, box1, box2):
        """
        True if collision, False otherwise
        """
        return (
            box1["x"] < box2["x"] + box2["width"]
            and box1["x"] + box1["width"] > box2["x"]
            and box1["y"] < box2["y"] + box2["height"]
            and box1["y"] + box1["height"] > box2["y"]
        )

    def check_collision(self, bird_box, pipe):
        """
        True if collision, False otherwise
        """
        # Check collision with top pipe body
        top_hitbox = {
            "x": pipe.x + PIPE_HITBOX_INSET,
            "y": PIPE_TOP_MARGIN,
            "width": pipe.width - 2 * PIPE_HITBOX_INSET,
            "height": max(0, pipe.y_top - PIPE_TOP_OFFSET),
        }
        if self.bounding_box_collision(bird_box, top_hitbox):
            return True

        # Check collision with bottom pipe body
        bottom_hitbox = {
            "x": pipe.x + PIPE_HITBOX_INSET,
            "y": pipe.y_bottom + PIPE_BOTTOM_OFFSET,
            "width": pipe.width - 2 * PIPE_HITBOX_INSET,
            "height": max(0, SCREEN_BOTTOM - (pipe.y_bottom + PIPE_TOP_OFFSET)),
        }
        if self.bounding_box_collision(bird_box, bottom_hitbox):
            return True

        # Check collision with top cap
        top_cap_box = {
            "x": pipe.x + PIPE_CAP_INSET,
            "y": max(0, pipe.y_top - PIPE_CAP_HEIGHT),
            "width": pipe.width - 2 * PIPE_CAP_INSET,
            "height": PIPE_CAP_HEIGHT,
        }
        if self.bounding_box_collision(bird_box, top_cap_box):
            return True

        # Check collision with bottom cap
        bottom_cap_box = {
            "x": pipe.x + PIPE_CAP_INSET,
            "y": pipe.y_bottom,
            "width": pipe.width - 2 * PIPE_CAP_INSET,
            "height": PIPE_CAP_HEIGHT,
        }
        if self.bounding_box_collision(bird_box, bottom_cap_box):
            return True

        return False

    def heuristic(self, state, pipes, items):
        """
        Heuristic function for A* (to be overridden by subclasses).
        """
        raise NotImplementedError("Subclasses must implement heuristic()")

    def evaluate_items(self, state, items):
        """
        Evaluate nearby items (buffs and debuffs).
        Lower priority than safety - small bonuses/penalties.

        Args:
            state: Current state
            items: List of items (Coin or PowerUp objects)

        Returns:
            Score adjustment (negative = good, positive = bad)
        """
        from entities.coin import Coin
        from entities.powerup import PowerUp

        score = 0
        bird_x = self.game.bird.x + state.x_offset

        # Constants for item evaluation
        ITEM_SEARCH_DISTANCE = 30
        BUFF_REWARD = 2.0  # Small reward for buffs
        DEBUFF_PENALTY = 3.0  # Small penalty for debuffs
        DISTANCE_WEIGHT = 50  # Distance matters less than for coins

        for item in items:
            # Skip if item is too far behind or too far ahead
            x_dist = item.x - bird_x
            if x_dist < -5 or x_dist >= ITEM_SEARCH_DISTANCE:
                continue

            y_dist = item.y - state.y
            dist_sq = x_dist * x_dist + y_dist * y_dist

            # Identify item type using isinstance
            if isinstance(item, Coin):
                # Coins are neutral for base A* (subclasses can handle them)
                continue
            elif isinstance(item, PowerUp):
                # PowerUp has is_debuff attribute
                if item.is_debuff:
                    # Penalize being near debuffs (speed_up, large)
                    score += DEBUFF_PENALTY / (dist_sq + DISTANCE_WEIGHT)
                else:
                    # Reward being near buffs (shield, slow_motion, small)
                    score -= BUFF_REWARD / (dist_sq + DISTANCE_WEIGHT)

        return score

    def fallback_action(self, state, pipes):
        """
        Safe action (JUMP or NO_JUMP) to be in the middle of the gap.
        """
        if not pipes:
            return state.y > SCREEN_MIDDLE_Y

        next_pipe = None
        for pipe in pipes:
            if pipe.x + pipe.width > self.game.bird.x:
                next_pipe = pipe
                break

        if not next_pipe:
            return state.y > SCREEN_MIDDLE_Y

        gap_middle = (next_pipe.y_top + next_pipe.y_bottom) / 2
        return state.y >= gap_middle

    def squared_distance(self, state, item):
        """
        Calculate squared Euclidean distance from state to item.
        """
        bird_x = self.game.bird.x + state.x_offset
        bird_y = state.y
        item_x = item.x
        item_y = item.y

        return (bird_x - item_x) ** 2 + (bird_y - item_y) ** 2

    def get_next_pipe(self, state, pipes):
        bird_x = self.game.bird.x + state.x_offset

        for pipe in pipes:
            if pipe.x + pipe.width > bird_x:
                return pipe
        return None
