COIN_SIZE = 3
REGULAR_COIN_VALUE = 5
GOLD_COIN_VALUE = 10


class Coin:
    """Collectible coin that awards points."""

    def __init__(self, x: float, y: float, value: int = REGULAR_COIN_VALUE):
        """
        Args:
            x: X position
            y: Y position
            value: Point value (default 5, gold coins are 10)
        """
        self.x = x
        self.y = y
        self.value = value
        self.width = COIN_SIZE
        self.height = COIN_SIZE
        self.collected = False
        self.is_gold = value > REGULAR_COIN_VALUE

    def update(self, scroll_speed: float, dt: float) -> None:
        """Update coin position.

        Args:
            scroll_speed: Horizontal scroll speed
            dt: Delta time in seconds
        """
        self.x -= scroll_speed * dt

    def is_offscreen(self) -> bool:
        """Check if coin is off the left side of screen.

        Returns:
            True if offscreen
        """
        return self.x + self.width < 0

    def get_hitbox(self) -> dict:
        """Get coin's collision hitbox.

        Returns:
            Dictionary with x, y, width, height
        """
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}
