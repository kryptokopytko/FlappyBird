"""Coin collectible entity."""


class Coin:
    """Represents a collectible coin."""

    def __init__(self, x, y, value=5):
        """
        Create a coin.

        Args:
            x: Horizontal position
            y: Vertical position
            value: Points value (5 for normal, 15 for gold)
        """
        self.x = x
        self.y = y
        self.value = value
        self.width = 3
        self.height = 3
        self.collected = False
        self.is_gold = value > 5

    def update(self, scroll_speed, dt):
        """Update coin position (scrolling)."""
        self.x -= scroll_speed * dt

    def is_offscreen(self):
        """Check if coin is off the left side of screen."""
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
        """Return ASCII art for the coin."""
        if self.is_gold:
            return [
                "╔══╗",
                "║$$║",
                "╚══╝"
            ]
        else:
            return [
                "╔═╗",
                "║$║",
                "╚═╝"
            ]
