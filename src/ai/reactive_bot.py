"""Reactive bot that responds to current position without prediction."""


class ReactiveBot:
    """A simple reactive bot that doesn't predict - just reacts."""

    def __init__(self, game):
        self.game = game
        self.target_y = 12  # Middle of screen

    def decide_action(self):
        """
        Decide whether to jump - reactive strategy (no prediction).

        Returns:
            True if should jump, False otherwise
        """
        bird = self.game.bird
        pipes = self.game.pipes

        # Only jump when falling (allow minor corrections)
        if bird.velocity < -3:
            return False

        if not pipes:
            # No pipes - simple middle logic
            return bird.y > self.target_y

        # Find the next pipe ahead of the bird
        next_pipe = None
        for pipe in pipes:
            if pipe.x + pipe.width > bird.x:
                next_pipe = pipe
                break

        if not next_pipe:
            # No pipe ahead - simple middle logic
            return bird.y > self.target_y

        # Calculate the middle of the gap
        gap_middle = (next_pipe.y_top + next_pipe.y_bottom) / 2

        # Reactive strategy: simple comparison, NO prediction
        # Just ask: "Am I below the gap middle?"
        if bird.y >= gap_middle:
            return True

        # Small safety margin: jump if falling fast and close to middle
        if bird.velocity > 3 and bird.y > gap_middle - 0.5:
            return True

        return False
