"""Simple flat bot that only works on levels with consistent gap heights.

This bot uses a very basic strategy:
- Maintains a fixed target height
- Does NOT adapt to changing gap positions
- Performs well on flat/easy levels (same height gaps)
- Dies quickly on levels with varying gap heights
"""

FIXED_TARGET_Y = 11.5  # Fixed height - doesn't adapt
RISING_VELOCITY_THRESHOLD = -2
MIN_JUMP_INTERVAL = 5  # Minimum frames between jumps


class FlatBot:
    """A stupid bot that assumes all gaps are at the same height.

    Strategy: Stays at a fixed height without adapting to gaps.
    - Works well when gaps are consistent (flat levels)
    - Dies immediately when gaps vary in height (hard levels)
    """

    def __init__(self, game):
        self.game = game
        self.target_y = FIXED_TARGET_Y
        self.frames_since_jump = 0

    def decide_action(self):
        """
        True if should jump, False otherwise

        Uses the simplest possible strategy - maintain fixed height.
        """
        bird = self.game.bird
        self.frames_since_jump += 1

        # Don't jump if still rising
        if bird.velocity < RISING_VELOCITY_THRESHOLD:
            return False

        # Prevent rapid consecutive jumps
        if self.frames_since_jump < MIN_JUMP_INTERVAL:
            return False

        # Simple: jump if below target height
        if bird.y > self.target_y:
            self.frames_since_jump = 0
            return True

        return False
