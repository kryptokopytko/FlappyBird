COIN_SIZE = 3

class Coin:
    """Collectible coin that awards points."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = COIN_SIZE
        self.height = COIN_SIZE
        self.collected = False

    def update(self, scroll_speed: float, dt: float) -> None:
        """Update coin position.

        Args:
            scroll_speed: Horizontal scroll speed
            dt: Delta time in seconds
        """
        self.x -= scroll_speed * dt

    def is_offscreen(self) -> bool:
        """Check if coin is off the left side of screen.
        """
        return self.x + self.width < 0

    def get_hitbox(self) -> dict:
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}

    def coins_to_points(nr_of_coins: int):
        if nr_of_coins == 0:
            return 0
        
        base = 1 + nr_of_coins / 3
        reward = base ** 1.5
        reward = max(1, reward)
        reward = min(reward, 130)

        return int(reward)