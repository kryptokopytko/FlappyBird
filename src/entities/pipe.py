"""Pipe obstacle entity."""


class Pipe:
    """Represents a pipe obstacle."""

    def __init__(self, x, y_top, y_bottom, gap_size):
        """
        Create a pipe pair.

        Args:
            x: Horizontal position
            y_top: Bottom of the top pipe
            y_bottom: Top of the bottom pipe
            gap_size: Size of the gap between pipes
        """
        self.x = x
        self.y_top = y_top
        self.y_bottom = y_bottom
        self.gap_size = gap_size
        self.width = 6
        self.passed = False  # Track if bird passed this pipe

    def update(self, scroll_speed, dt):
        """Update pipe position (scrolling)."""
        self.x -= scroll_speed * dt

    def is_offscreen(self):
        """Check if pipe is off the left side of screen."""
        return self.x + self.width < 0

    def get_top_hitbox(self):
        """Get hitbox for the top pipe (excluding the decorative cap)."""
        # Exclude the decorative cap (2 lines) for more forgiving collision
        return {
            'x': self.x + 1,  # Shrink horizontally by 1 pixel on each side
            'y': 1,  # Start 1 line below the ceiling
            'width': self.width - 2,
            'height': max(0, self.y_top - 3)
        }

    def get_bottom_hitbox(self):
        """Get hitbox for the bottom pipe (excluding the decorative cap)."""
        # Exclude the decorative cap (2 lines) for more forgiving collision
        return {
            'x': self.x + 1,  # Shrink horizontally by 1 pixel on each side
            'y': self.y_bottom + 2,
            'width': self.width - 2,
            'height': max(0, 24 - (self.y_bottom + 3))
        }

    def bird_in_gap(self, bird_y):
        """Check if bird Y position is in the gap."""
        return self.y_top < bird_y < self.y_bottom

    def render_ascii(self):
        """Return ASCII art for the pipe."""
        # Top pipe segment
        top_pipe = [
            "║████║",
            "║████║",
            "╚════╝"
        ]

        # Bottom pipe segment
        bottom_pipe = [
            "╔════╗",
            "║████║",
            "║████║"
        ]

        return {
            'top': top_pipe,
            'bottom': bottom_pipe
        }
