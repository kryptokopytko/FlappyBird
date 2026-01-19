"""A* pathfinding bot base class."""

import heapq


class State:
    """Represents a bird state for A* search."""

    def __init__(self, y, velocity, x_offset=0):
        """
        Create a state.

        Args:
            y: Bird Y position (float)
            velocity: Bird velocity (float)
            x_offset: X offset from current position (for planning ahead)
        """
        self.y = y
        self.velocity = velocity
        self.x_offset = x_offset

    def __lt__(self, other):
        """Less than comparison for heapq (arbitrary but consistent)."""
        return self.y < other.y


class AStarBot:
    """Base A* bot with pathfinding capabilities."""

    # Action constants
    JUMP = True
    NO_JUMP = False

    def __init__(self, game):
        """
        Initialize A* bot.

        Args:
            game: Game instance for accessing state
        """
        self.game = game
        self.lookahead_steps = 7  # Reduced for performance

    def decide_action(self):
        """
        Decide whether to jump using A* pathfinding.

        Returns:
            True if should jump, False otherwise
        """
        bird = self.game.bird
        pipes = self.game.pipes
        items = self.game.items

        # Create current state
        current_state = State(bird.y, bird.velocity, 0)

        # Run A* search
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
        # Priority queue: (f_score, g_score, state, action_sequence)
        open_set = [(0, 0, current_state, [])]
        closed_set = set()

        iterations = 0
        max_iterations = 40  # Reduced for performance

        while open_set and iterations < max_iterations:
            iterations += 1

            f_score, g_score, state, actions = heapq.heappop(open_set)

            # Goal: planned ahead enough steps
            if len(actions) >= self.lookahead_steps:
                return actions[0] if actions else self.NO_JUMP

            # Early termination: if we found a good path, use it immediately
            if len(actions) >= 5 and f_score < 20:
                return actions[0] if actions else self.NO_JUMP

            # Skip if already visited (discretize state for efficiency)
            state_key = (round(state.y, 1), round(state.velocity, 1), state.x_offset // 5)
            if state_key in closed_set:
                continue
            closed_set.add(state_key)

            # Try both actions
            for action in [self.JUMP, self.NO_JUMP]:
                new_state = self.predict_next_state(state, action)

                # Check if state is valid (not dead)
                if self.is_dead(new_state, pipes):
                    continue

                new_actions = actions + [action]
                new_g_score = g_score + 1  # Cost of 1 per step
                h_score = self.heuristic(new_state, pipes, items)
                new_f_score = new_g_score + h_score

                heapq.heappush(open_set, (new_f_score, new_g_score, new_state, new_actions))

        # No valid path found or timed out - use fallback
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
        dt = 1.0 / 60.0  # One frame at 60 FPS
        gravity = 1.0
        jump_force = -22
        terminal_velocity = 40.0
        scroll_speed = self.game.scroll_speed

        # Update velocity (CRITICAL: gravity is NOT multiplied by dt - matches bird.py:26)
        new_velocity = state.velocity
        if action == self.JUMP:
            new_velocity = jump_force
        else:
            new_velocity += gravity  # NO dt multiplication here!
            new_velocity = min(new_velocity, terminal_velocity)

        # Update position (dt IS used here - matches bird.py:28)
        new_y = state.y + new_velocity * dt
        new_x_offset = state.x_offset + scroll_speed * dt

        return State(new_y, new_velocity, new_x_offset)

    def is_dead(self, state, pipes):
        """
        Check if state represents a collision/death.

        Args:
            state: State to check
            pipes: List of pipes

        Returns:
            True if dead, False otherwise
        """
        # Check ceiling/floor collision
        if state.y <= 0 or state.y + 3 > 23:  # Hitbox height = 3
            return True

        # Check pipe collisions
        bird_hitbox = {
            'x': self.game.bird.x + 1,  # Bird is at fixed x=15, hitbox offset
            'y': round(state.y),
            'width': 3,
            'height': 3
        }

        for pipe in pipes:
            # Check if pipe is in range
            if pipe.x + pipe.width < bird_hitbox['x']:
                continue  # Pipe is behind bird
            if pipe.x > bird_hitbox['x'] + 20:
                continue  # Pipe is too far ahead

            # Check collision with pipe
            if self.check_collision(bird_hitbox, pipe):
                return True

        return False

    def check_collision(self, bird_box, pipe):
        """
        Check AABB collision between bird hitbox and pipe.

        Args:
            bird_box: Bird hitbox dict
            pipe: Pipe object

        Returns:
            True if collision, False otherwise
        """
        # Check collision with top pipe
        if (bird_box['x'] < pipe.x + pipe.width and
            bird_box['x'] + bird_box['width'] > pipe.x):
            # X overlap - check Y
            if bird_box['y'] < pipe.y_top:
                return True
            if bird_box['y'] + bird_box['height'] > pipe.y_bottom:
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
        Fallback action when A* fails or times out.

        Args:
            state: Current state
            pipes: List of pipes

        Returns:
            Safe action (JUMP or NO_JUMP)
        """
        # Simple reactive fallback: jump if below gap middle
        if not pipes:
            return state.y > 12  # Middle of screen

        next_pipe = None
        for pipe in pipes:
            if pipe.x + pipe.width > self.game.bird.x:
                next_pipe = pipe
                break

        if not next_pipe:
            return state.y > 12

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

        Args:
            state: Current state
            pipes: List of pipes

        Returns:
            Next pipe or None
        """
        bird_x = self.game.bird.x + state.x_offset

        for pipe in pipes:
            if pipe.x + pipe.width > bird_x:
                return pipe
        return None
