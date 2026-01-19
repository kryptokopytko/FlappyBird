"""Effect management system for power-ups and debuffs."""


class Effect:
    """Base class for timed effects."""

    def __init__(self, duration, effect_type, icon):
        """
        Create an effect.

        Args:
            duration: Duration in seconds
            effect_type: Type identifier
            icon: Icon character for UI display
        """
        self.duration = duration
        self.type = effect_type
        self.icon = icon
        self.timer = 0.0
        self.active = True

    def update(self, dt):
        """
        Update the effect timer.

        Returns:
            True if effect is still active, False if expired
        """
        self.timer += dt
        if self.timer >= self.duration:
            self.active = False
        return self.active

    def get_remaining_time(self):
        """Get remaining time in seconds."""
        return max(0, self.duration - self.timer)

    def apply(self, game):
        """Apply the effect (override in subclasses)."""
        pass

    def remove(self, game):
        """Remove the effect (override in subclasses)."""
        pass


class ShieldEffect(Effect):
    """Shield effect - protects from one collision."""

    def __init__(self, duration=10.0):
        super().__init__(duration, 'shield', '◘')

    def apply(self, game):
        game.bird.has_shield = True

    def remove(self, game):
        game.bird.has_shield = False


class SlowMotionEffect(Effect):
    """Slow motion effect - reduces scroll speed."""

    def __init__(self, duration=8.0):
        super().__init__(duration, 'slow_motion', '⏱')
        self.original_speed = None

    def apply(self, game):
        self.original_speed = game.scroll_speed
        game.scroll_speed *= 0.5

    def remove(self, game):
        if self.original_speed:
            game.scroll_speed = self.original_speed


class SmallSizeEffect(Effect):
    """Small size effect - reduces bird hitbox."""

    def __init__(self, duration=12.0):
        super().__init__(duration, 'small', '↓')
        self.original_size = None

    def apply(self, game):
        self.original_size = (game.bird.width, game.bird.height)
        game.bird.width = 4
        game.bird.height = 2
        game.bird.size = 'small'

    def remove(self, game):
        if self.original_size:
            game.bird.width, game.bird.height = self.original_size
            game.bird.size = 'normal'


class SpeedUpEffect(Effect):
    """Speed up debuff - increases scroll speed."""

    def __init__(self, duration=10.0):
        super().__init__(duration, 'speed_up', '⚡')
        self.original_speed = None

    def apply(self, game):
        self.original_speed = game.scroll_speed
        game.scroll_speed *= 1.5

    def remove(self, game):
        if self.original_speed:
            game.scroll_speed = self.original_speed


class LargeSizeEffect(Effect):
    """Large size debuff - increases bird hitbox."""

    def __init__(self, duration=10.0):
        super().__init__(duration, 'large', '↑')
        self.original_size = None

    def apply(self, game):
        self.original_size = (game.bird.width, game.bird.height)
        game.bird.width = 6
        game.bird.height = 4
        game.bird.size = 'large'

    def remove(self, game):
        if self.original_size:
            game.bird.width, game.bird.height = self.original_size
            game.bird.size = 'normal'


class EffectManager:
    """Manages all active effects."""

    EFFECT_MAP = {
        'shield': ShieldEffect,
        'slow_motion': SlowMotionEffect,
        'small': SmallSizeEffect,
        'speed_up': SpeedUpEffect,
        'large': LargeSizeEffect
    }

    def __init__(self, game):
        self.game = game
        self.active_effects = []

    def add_effect(self, effect_type):
        """
        Add a new effect.

        Args:
            effect_type: Type of effect to add
        """
        effect_class = self.EFFECT_MAP.get(effect_type)
        if not effect_class:
            return

        # Remove existing effect of the same type
        self.remove_effect_by_type(effect_type)

        # Create and apply new effect
        effect = effect_class()
        effect.apply(self.game)
        self.active_effects.append(effect)

    def update(self, dt):
        """Update all active effects."""
        for effect in self.active_effects[:]:
            if not effect.update(dt):
                effect.remove(self.game)
                self.active_effects.remove(effect)

    def remove_effect_by_type(self, effect_type):
        """Remove an effect by its type."""
        for effect in self.active_effects[:]:
            if effect.type == effect_type:
                effect.remove(self.game)
                self.active_effects.remove(effect)

    def get_active_icons(self):
        """Get list of icons for active effects."""
        return [effect.icon for effect in self.active_effects]

    def clear_all(self):
        """Clear all active effects."""
        for effect in self.active_effects[:]:
            effect.remove(self.game)
        self.active_effects.clear()
