from core.config import GAME_CONFIG

PIPE_WIDTH = 6
PIPE_HITBOX_INSET = 1
PIPE_TOP_MARGIN = 1
PIPE_BOTTOM_OFFSET = 2
PIPE_TOP_OFFSET = 3


class Pipe:
    """Vertical pipe obstacle with a gap for the bird to pass through."""

    def __init__(self, x: float, y_top: float, y_bottom: float, gap_size: float):
        self.x = x
        self.y_top = y_top
        self.y_bottom = y_bottom
        self.gap_size = gap_size
        self.width = PIPE_WIDTH
        self.passed = False

    def update(self, scroll_speed: float, dt: float) -> None:
        self.x -= scroll_speed * dt

    def is_offscreen(self) -> bool:
        return self.x + self.width < 0

    def get_top_hitbox(self) -> dict:
        return {
            "x": self.x + PIPE_HITBOX_INSET,
            "y": PIPE_TOP_MARGIN,
            "width": self.width - 2 * PIPE_HITBOX_INSET,
            "height": max(0, self.y_top - PIPE_TOP_OFFSET),
        }

    def get_bottom_hitbox(self) -> dict:
        screen_height = GAME_CONFIG["screen"]["height"]
        return {
            "x": self.x + PIPE_HITBOX_INSET,
            "y": self.y_bottom + PIPE_BOTTOM_OFFSET,
            "width": self.width - 2 * PIPE_HITBOX_INSET,
            "height": max(0, screen_height - (self.y_bottom + PIPE_TOP_OFFSET)),
        }

    def bird_in_gap(self, bird_y: float) -> bool:
        return self.y_top < bird_y < self.y_bottom
