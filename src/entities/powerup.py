"""Power-up and debuff entities."""


class PowerUp:
    """Represents a power-up or debuff."""

    # Power-up types
    SHIELD = 'shield'
    SLOW_MOTION = 'slow_motion'
    SMALL = 'small'

    # Debuff types
    SPEED_UP = 'speed_up'
    LARGE = 'large'

    def __init__(self, x, y, powerup_type):
        """
        Create a power-up.

        Args:
            x: Horizontal position
            y: Vertical position
            powerup_type: Type of power-up (see class constants)
        """
        self.x = x
        self.y = y
        self.type = powerup_type
        self.width = 5
        self.height = 3
        self.collected = False
        self.duration = 10.0  # Duration in seconds
        self.is_debuff = powerup_type in [self.SPEED_UP, self.LARGE]

    def update(self, scroll_speed, dt):
        """Update power-up position (scrolling)."""
        self.x -= scroll_speed * dt

    def is_offscreen(self):
        """Check if power-up is off the left side of screen."""
        return self.x + self.width < 0

    def get_hitbox(self):
        """Get hitbox for collision detection."""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }

    def render_ascii(self):
        """Return ASCII art for the power-up."""
        sprites = {
            self.SHIELD: [
                "╔═══╗",
                "║ ◘ ║",
                "╚═══╝"
            ],
            self.SLOW_MOTION: [
                "╔═══╗",
                "║ ⏱ ║",
                "╚═══╝"
            ],
            self.SMALL: [
                "╔═══╗",
                "║ ↓ ║",
                "╚═══╝"
            ],
            self.SPEED_UP: [
                "╔═══╗",
                "║ ⚡ ║",
                "╚═══╝"
            ],
            self.LARGE: [
                "╔═══╗",
                "║ ↑ ║",
                "╚═══╝"
            ]
        }
        return sprites.get(self.type, ["[?]"])

    def get_icon(self):
        """Get single character icon for UI display."""
        icons = {
            self.SHIELD: '◘',
            self.SLOW_MOTION: '⏱',
            self.SMALL: '↓',
            self.SPEED_UP: '⚡',
            self.LARGE: '↑'
        }
        return icons.get(self.type, '?')
