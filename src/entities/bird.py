"""Bird entity with physics and powerup management."""

from core.config import GAME_CONFIG

BIRD_SIZES = {
    "small": {"width": 4, "height": 2},
    "normal": {"width": 5, "height": 3},
    "large": {"width": 6, "height": 4},
}

HITBOX_SCALE = 0.8
SPEED_DEBUFF_MULTIPLIER = 1.5


class Bird:
    def __init__(self):
        self.x = GAME_CONFIG["bird"]["start_x"]
        self.y = float(GAME_CONFIG["bird"]["start_y"])
        self.velocity = 0.0
        self.gravity = GAME_CONFIG["bird"]["gravity"]
        self.jump_force = GAME_CONFIG["bird"]["jump_force"]
        self.terminal_velocity = GAME_CONFIG["bird"]["terminal_velocity"]

        self.size = "normal"
        self.width = BIRD_SIZES["normal"]["width"]
        self.height = BIRD_SIZES["normal"]["height"]
        self.has_shield = False

    def update(self, dt: float) -> None:
        """
        Args:
            dt: Delta time in seconds
        """
        self.velocity += self.gravity
        self.velocity = min(self.velocity, self.terminal_velocity)
        self.y += self.velocity * dt

    def jump(self) -> bool:
        """
        True if jump was executed, False otherwise
        """
        if self.velocity >= 0:
            self.velocity = self.jump_force
            return True
        return False

    def get_hitbox(self) -> dict:
        """
        Dictionary with x, y, width, height of hitbox
        """
        hitbox_w = self.width * HITBOX_SCALE
        hitbox_h = self.height * HITBOX_SCALE

        offset_x = (self.width - hitbox_w) / 2
        offset_y = (self.height - hitbox_h) / 2

        hitbox_y = round(self.y + offset_y)
        hitbox_y = max(
            0, min(hitbox_y, GAME_CONFIG["screen"]["height"] - int(hitbox_h))
        )

        return {
            "x": self.x + offset_x,
            "y": hitbox_y,
            "width": hitbox_w,
            "height": hitbox_h,
        }

    def is_out_of_bounds(self, screen_height: int) -> bool:
        rounded_y = round(self.y)
        return rounded_y <= 0 or rounded_y + self.height >= screen_height

    def apply_powerup(self, powerup_type: str) -> None:
        if powerup_type == "shield":
            self.has_shield = True
        elif powerup_type == "small":
            self._set_size("small")

    def apply_debuff(self, debuff_type: str) -> None:
        if debuff_type == "large":
            self._set_size("large")
        elif debuff_type == "speed":
            self.gravity *= SPEED_DEBUFF_MULTIPLIER

    def _set_size(self, size: str) -> None:
        if size in BIRD_SIZES:
            self.size = size
            self.width = BIRD_SIZES[size]["width"]
            self.height = BIRD_SIZES[size]["height"]

    def reset(self) -> None:
        self.y = float(GAME_CONFIG["bird"]["start_y"])
        self.velocity = 0.0
        self.has_shield = False
        self.gravity = GAME_CONFIG["bird"]["gravity"]
        self._set_size("normal")
