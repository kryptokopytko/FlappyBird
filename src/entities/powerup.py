POWERUP_SHIELD = "shield"
POWERUP_SLOW_MOTION = "slow_motion"
POWERUP_SMALL = "small"

DEBUFF_SPEED_UP = "speed_up"
DEBUFF_LARGE = "large"

POWERUP_WIDTH = 5
POWERUP_HEIGHT = 3

DEBUFF_TYPES = {DEBUFF_SPEED_UP, DEBUFF_LARGE}

POWERUPS = [POWERUP_SHIELD, POWERUP_SLOW_MOTION, POWERUP_SMALL, DEBUFF_SPEED_UP, DEBUFF_LARGE]

class PowerUp:
    """Collectible powerup or debuff item."""

    def __init__(self, x: float, y: float, powerup_type: str):
        """
        Args:
            x: X position
            y: Y position
            powerup_type: Type of effect (shield, small, speed_up, large, etc.)
        """
        self.x = x
        self.y = y
        self.type = powerup_type
        self.width = POWERUP_WIDTH
        self.height = POWERUP_HEIGHT
        self.collected = False
        self.is_debuff = powerup_type in DEBUFF_TYPES

    def update(self, scroll_speed: float, dt: float) -> None:
        """Update powerup position.

        Args:
            scroll_speed: Horizontal scroll speed
            dt: Delta time in seconds
        """
        self.x -= scroll_speed * dt

    def is_offscreen(self) -> bool:
        return self.x + self.width < 0

    def get_hitbox(self) -> dict:
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}
