"""Bird entity with physics."""

from utils.config import GAME_CONFIG


class Bird:
    """Represents the player's bird."""

    def __init__(self):
        self.x = GAME_CONFIG['bird']['start_x']
        self.y = float(GAME_CONFIG['bird']['start_y'])
        self.velocity = 0.0
        self.gravity = GAME_CONFIG['bird']['gravity']
        self.jump_force = GAME_CONFIG['bird']['jump_force']
        self.terminal_velocity = GAME_CONFIG['bird']['terminal_velocity']
        self.width = 5
        self.height = 3
        self.size = 'normal'
        self.has_shield = False
        self.lives = 3
        self.animation_frame = 0
        self.animation_timer = 0.0

    def update(self, dt):
        """Update bird physics."""
        self.velocity += self.gravity
        self.velocity = min(self.velocity, self.terminal_velocity)
        self.y += self.velocity * dt
        self.animation_timer += dt
        if self.animation_timer > 0.1:
            self.animation_frame = (self.animation_frame + 1) % 3
            self.animation_timer = 0.0

    def jump(self):
        """Make the bird jump (only if falling or stationary)."""
        if self.velocity >= 0:
            self.velocity = self.jump_force
            return True
        return False

    def get_hitbox(self):
        """Return the bird's hitbox for collision detection."""
        # Use square hitbox (3x3) for better match with circular rendering
        # Centered on bird position
        hitbox_size = 3
        offset_x = (self.width - hitbox_size) / 2

        # Clamp hitbox to valid screen bounds
        # This prevents hitbox from going off-screen when bird is dying
        hitbox_y = round(self.y)
        hitbox_y = max(0, hitbox_y)  # Don't go above ceiling
        hitbox_y = min(20, hitbox_y)  # Don't extend below ground (20 + 3 = 23)

        return {
            'x': self.x + offset_x,
            'y': hitbox_y,
            'width': hitbox_size,
            'height': hitbox_size
        }

    def is_out_of_bounds(self, screen_height):
        """Check if bird is outside screen bounds."""
        ground_level = screen_height - 1
        # Use round() to match hitbox positioning
        rounded_y = round(self.y)
        return rounded_y <= 0 or rounded_y + self.height > ground_level

    def apply_powerup(self, powerup_type):
        """Apply a power-up effect."""
        if powerup_type == 'shield':
            self.has_shield = True
        elif powerup_type == 'small':
            self.size = 'small'
            self.height = 2
            self.width = 4

    def apply_debuff(self, debuff_type):
        """Apply a debuff effect."""
        if debuff_type == 'large':
            self.size = 'large'
            self.height = 4
            self.width = 6
        elif debuff_type == 'speed':
            self.gravity *= 1.5

    def reset(self):
        """Reset bird to starting state."""
        self.y = float(GAME_CONFIG['bird']['start_y'])
        self.velocity = 0.0
        self.size = 'normal'
        self.has_shield = False
        self.width = 5
        self.height = 3
        self.gravity = GAME_CONFIG['bird']['gravity']
