"""Aggressive bot that minimizes jumps."""

# Strategy constants
DEFAULT_TARGET_Y = 14
RISING_VELOCITY_THRESHOLD = -2
GAP_OFFSET_BELOW_MIDDLE = 1.5
EMERGENCY_VELOCITY_THRESHOLD = 4
EMERGENCY_MARGIN = 1


class AggressiveBot:
    """aims low and jumps minimally, only jumps when absolutely necessary."""

    def __init__(self, game):
        self.game = game
        self.target_y = DEFAULT_TARGET_Y

    def decide_action(self):
        """True if should jump, False otherwise"""
        bird = self.game.bird
        pipes = self.game.pipes

        if bird.velocity < RISING_VELOCITY_THRESHOLD:
            return False

        if not pipes:
            return bird.y > self.target_y

        next_pipe = self._find_next_pipe(pipes, bird.x)
        if not next_pipe:
            return bird.y > self.target_y

        gap_middle = (next_pipe.y_top + next_pipe.y_bottom) / 2
        risky_target = gap_middle + GAP_OFFSET_BELOW_MIDDLE

        if bird.y > risky_target:
            return True

        if (
            bird.velocity > EMERGENCY_VELOCITY_THRESHOLD
            and bird.y > risky_target - EMERGENCY_MARGIN
        ):
            return True

        return False

    def _find_next_pipe(self, pipes, bird_x):
        """Find the next pipe ahead of the bird."""
        for pipe in pipes:
            if pipe.x + pipe.width > bird_x:
                return pipe
        return None
