SCREEN_MIDDLE_Y = 12
RISING_VELOCITY_THRESHOLD = -3
FAST_FALLING_VELOCITY = 3
SAFETY_MARGIN = 0.5


class ReactiveBot:
    """A simple reactive bot that doesn't predict - just reacts.

    Strategy: Responds to current position relative to gap center.
    Includes safety margin for fast falling to prevent crashes.
    """

    def __init__(self, game):
        self.game = game
        self.target_y = SCREEN_MIDDLE_Y

    def decide_action(self):
        """
        True if should jump, False otherwise
        """
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

        if bird.y >= gap_middle:
            return True

        if (
            bird.velocity > FAST_FALLING_VELOCITY
            and bird.y > gap_middle - SAFETY_MARGIN
        ):
            return True

        return False

    def _find_next_pipe(self, pipes, bird_x):
        """Find the next pipe ahead of the bird."""
        for pipe in pipes:
            if pipe.x + pipe.width > bird_x:
                return pipe
        return None
