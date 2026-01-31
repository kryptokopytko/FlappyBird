"""Aggressive bot that minimizes jumps."""

# Strategy constants
DEFAULT_TARGET_Y = 14
RISING_VELOCITY_THRESHOLD = -2
GAP_OFFSET_BELOW_MIDDLE = 1.2  # Reduced from 1.5 for better gap navigation
EMERGENCY_VELOCITY_THRESHOLD = 4
EMERGENCY_MARGIN = 1.5  # Increased margin for safety
LOOKAHEAD_DISTANCE = 50  # Look ahead for early jump planning
PREDICTION_STEPS = 8  # Simulate future position


class AggressiveBot:
    """aims low and jumps minimally, only jumps when absolutely necessary."""

    def __init__(self, game):
        self.game = game
        self.target_y = DEFAULT_TARGET_Y

    def decide_action(self):
        """True if should jump, False otherwise"""
        bird = self.game.bird
        pipes = self.game.pipes

        # Don't jump if still rising
        if bird.velocity < RISING_VELOCITY_THRESHOLD:
            return False

        if not pipes:
            return bird.y > self.target_y

        next_pipe = self._find_next_pipe(pipes, bird.x)
        if not next_pipe:
            return bird.y > self.target_y

        # Calculate target position (below gap middle)
        gap_middle = (next_pipe.y_top + next_pipe.y_bottom) / 2
        risky_target = gap_middle + GAP_OFFSET_BELOW_MIDDLE

        # Predict future position to avoid late jumps
        distance_to_pipe = next_pipe.x - bird.x

        # If pipe is close, use tighter control
        if distance_to_pipe < LOOKAHEAD_DISTANCE:
            predicted_y = self._predict_position(bird.y, bird.velocity, PREDICTION_STEPS)

            # Jump if predicted position would be too low
            if predicted_y > risky_target + 1:
                return True

            # Emergency jump if falling fast and getting close to target
            if (
                bird.velocity > EMERGENCY_VELOCITY_THRESHOLD
                and bird.y > risky_target - EMERGENCY_MARGIN
            ):
                return True
        else:
            # For distant pipes, maintain safe cruising altitude
            if bird.y > risky_target:
                return True

        return False

    def _predict_position(self, y, velocity, steps):
        """Predict future Y position after given steps."""
        predicted_y = y
        predicted_v = velocity
        gravity = self.game.bird.gravity

        for _ in range(steps):
            predicted_v += gravity
            predicted_y += predicted_v * (1.0 / 60)

        return predicted_y

    def _find_next_pipe(self, pipes, bird_x):
        """Find the next pipe ahead of the bird."""
        for pipe in pipes:
            if pipe.x + pipe.width > bird_x:
                return pipe
        return None
