"""Aggressive bot that minimizes jumps."""


class AggressiveBot:
    """An aggressive bot that aims low and jumps minimally."""

    def __init__(self, game):
        self.game = game
        self.target_y = 14  # Prefer staying low

    def decide_action(self):
        """
        Decide whether to jump - aggressive strategy.

        Returns:
            True if should jump, False otherwise
        """
        bird = self.game.bird
        pipes = self.game.pipes

        # Only jump when falling significantly (not while rising)
        if bird.velocity < -2:
            return False

        if not pipes:
            # No pipes yet, stay relatively low
            if bird.y > self.target_y:
                return True
            return False

        # Find the next pipe ahead of the bird
        next_pipe = None
        for pipe in pipes:
            if pipe.x + pipe.width > bird.x:
                next_pipe = pipe
                break

        if not next_pipe:
            # No pipe ahead, stay low
            if bird.y > self.target_y:
                return True
            return False

        # Calculate the middle of the gap
        gap_middle = (next_pipe.y_top + next_pipe.y_bottom) / 2

        # Aggressive strategy: aim LOW (1.5 pixels below middle)
        risky_target = gap_middle + 1.5

        # Only jump when really low
        if bird.y > risky_target:
            return True

        # Emergency jump if velocity is very high and close to target
        if bird.velocity > 4 and bird.y > risky_target - 1:
            return True

        return False
