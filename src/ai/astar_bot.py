"""A* pathfinding bot base class."""

import heapq

# A* algorithm constants
DEFAULT_LOOKAHEAD_STEPS = 7
MAX_SEARCH_ITERATIONS = 40
EARLY_TERMINATION_STEPS = 5
EARLY_TERMINATION_SCORE = 20

# Physics simulation constants (must match bird.py)
SIMULATION_DT = 1.0 / 60.0
GRAVITY = 1.0
JUMP_FORCE = -22
TERMINAL_VELOCITY = 40.0

# Collision detection constants
SCREEN_TOP = 0
SCREEN_BOTTOM = 23
BIRD_HITBOX_WIDTH = 4.0  # 5 * 0.8 (normal bird width * hitbox scale)
BIRD_HITBOX_HEIGHT = 2.4  # 3 * 0.8 (normal bird height * hitbox scale)
BIRD_HITBOX_OFFSET_X = 0.5  # (5 - 4.0) / 2
BIRD_HITBOX_OFFSET_Y = 0.3  # (3 - 2.4) / 2
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
        """
        Args:
            y: Bird Y position (float)
            velocity: Bird velocity (float)
            x_offset: X offset from current position (for planning ahead)
        """
        self.y = y
        self.velocity = velocity
        self.x_offset = x_offset

    def __lt__(self, other):
        """Less than comparison for heapq"""
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

        # gravity is NOT multiplied by dt
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
            "x": self.game.bird.x + BIRD_HITBOX_OFFSET_X,
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

    def aabb_collision(self, box1, box2):
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
        if self.aabb_collision(bird_box, top_hitbox):
            return True

        # Check collision with bottom pipe body
        bottom_hitbox = {
            "x": pipe.x + PIPE_HITBOX_INSET,
            "y": pipe.y_bottom + PIPE_BOTTOM_OFFSET,
            "width": pipe.width - 2 * PIPE_HITBOX_INSET,
            "height": max(0, SCREEN_BOTTOM - (pipe.y_bottom + PIPE_TOP_OFFSET)),
        }
        if self.aabb_collision(bird_box, bottom_hitbox):
            return True

        # Check collision with top cap
        top_cap_box = {
            "x": pipe.x + PIPE_CAP_INSET,
            "y": max(0, pipe.y_top - PIPE_CAP_HEIGHT),
            "width": pipe.width - 2 * PIPE_CAP_INSET,
            "height": PIPE_CAP_HEIGHT,
        }
        if self.aabb_collision(bird_box, top_cap_box):
            return True

        # Check collision with bottom cap
        bottom_cap_box = {
            "x": pipe.x + PIPE_CAP_INSET,
            "y": pipe.y_bottom,
            "width": pipe.width - 2 * PIPE_CAP_INSET,
            "height": PIPE_CAP_HEIGHT,
        }
        if self.aabb_collision(bird_box, bottom_cap_box):
            return True

        return False

    def heuristic(self, state, pipes, items):
        """
        Heuristic function for A* (to be overridden by subclasses).

        Args:
            state: Current state
            pipes: List of pipes
            items: List of items

        Returns:
            Heuristic score (lower is better)
        """
        raise NotImplementedError("Subclasses must implement heuristic()")

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

        Args:
            state: Current state
            item: Item (coin/powerup/debuff)

        Returns:
            Squared distance (float) - faster than euclidean_distance
        """
        bird_x = self.game.bird.x + state.x_offset
        bird_y = state.y
        item_x = item.x
        item_y = item.y

        return (bird_x - item_x) ** 2 + (bird_y - item_y) ** 2

    def get_next_pipe(self, state, pipes):
        """
        Get the next pipe ahead of the bird.
        """
        bird_x = self.game.bird.x + state.x_offset

        for pipe in pipes:
            if pipe.x + pipe.width > bird_x:
                return pipe
        return None
