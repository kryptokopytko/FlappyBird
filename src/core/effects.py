"""Temporary effect system for powerups and debuffs."""

from typing import Optional

SHIELD_DURATION = 10.0
SLOW_MOTION_DURATION = 8.0
SMALL_SIZE_DURATION = 12.0
SPEED_UP_DURATION = 10.0
LARGE_SIZE_DURATION = 10.0

SLOW_MOTION_MULTIPLIER = 0.5
SPEED_UP_MULTIPLIER = 1.5


class Effect:
    """Base class for temporary game effects."""

    def __init__(self, duration: float, effect_type: str):
        """Initialize effect.

        Args:
            duration: How long effect lasts in seconds
            effect_type: Type identifier string
        """
        self.duration = duration
        self.type = effect_type
        self.timer = 0.0
        self.active = True

    def update(self, dt: float) -> bool:
        """Update effect timer.

        Args:
            dt: Delta time in seconds

        Returns:
            True if effect is still active
        """
        self.timer += dt
        if self.timer >= self.duration:
            self.active = False
        return self.active

    def get_remaining_time(self) -> float:
        return max(0, self.duration - self.timer)

    def extend_duration(self, additional_duration: float) -> None:
        """Extend the effect duration by adding time.

        Args:
            additional_duration: Time to add in seconds
        """
        self.duration += additional_duration

    def apply(self, game) -> None:
        """Apply effect to game state. Override in subclasses."""
        pass

    def remove(self, game) -> None:
        """Remove effect from game state. Override in subclasses."""
        pass

    def schedule_remove(self, game) -> None:
        """Remove effect with potential delay. Override in subclasses."""
        self.remove(game)



class ShieldEffect(Effect):
    """Grants temporary invulnerability to bird."""
    DELAY_ON_USE = 0.02
    
    def __init__(self, duration: float = SHIELD_DURATION):
        super().__init__(duration, "shield")
        self.delayed_remove_timer: float = 0.0
        self.remove_scheduled: bool = False

    def apply(self, game) -> None:
        game.bird.has_shield = True
        self._game = game

    def remove(self, game) -> None:
        game.bird.has_shield = False

    def schedule_remove(self):
        self.remove_scheduled = True
        self.delayed_remove_timer = self.DELAY_ON_USE

    def update(self, dt):
        if self.remove_scheduled:
            self.delayed_remove_timer -= dt
            if self.delayed_remove_timer <= 0:
                self.remove(self._game)
                self.remove_scheduled = False
                self.active = False
                return False

        return super().update(dt)


class SlowMotionEffect(Effect):
    """Slows down game scroll speed."""

    def __init__(self, duration: float = SLOW_MOTION_DURATION):
        super().__init__(duration, "slow_motion")

    def apply(self, game) -> None:
        # Don't modify if already active - handled by extend_duration
        game.scroll_speed *= SLOW_MOTION_MULTIPLIER

    def remove(self, game) -> None:
        # Restore by dividing by multiplier
        game.scroll_speed /= SLOW_MOTION_MULTIPLIER


class SmallSizeEffect(Effect):
    """Shrinks bird size for easier navigation."""

    def __init__(self, duration: float = SMALL_SIZE_DURATION):
        super().__init__(duration, "small")
        self.original_size: Optional[tuple] = None

    def apply(self, game) -> None:
        game.bird.apply_powerup("small")

    def remove(self, game) -> None:
        game.bird._set_size("normal")


class SpeedUpEffect(Effect):
    """Increases game scroll speed (debuff)."""

    def __init__(self, duration: float = SPEED_UP_DURATION):
        super().__init__(duration, "speed_up")

    def apply(self, game) -> None:
        # Don't modify if already active - handled by extend_duration
        game.scroll_speed *= SPEED_UP_MULTIPLIER

    def remove(self, game) -> None:
        # Restore by dividing by multiplier
        game.scroll_speed /= SPEED_UP_MULTIPLIER


class LargeSizeEffect(Effect):
    """Increases bird size, making it harder to navigate (debuff)."""

    def __init__(self, duration: float = LARGE_SIZE_DURATION):
        super().__init__(duration, "large")
        self.original_size: Optional[tuple] = None

    def apply(self, game) -> None:
        game.bird.apply_debuff("large")

    def remove(self, game) -> None:
        game.bird._set_size("normal")


class EffectManager:
    """Manages active temporary effects on the game."""

    EFFECT_MAP = {
        "shield": ShieldEffect,
        "slow_motion": SlowMotionEffect,
        "small": SmallSizeEffect,
        "speed_up": SpeedUpEffect,
        "large": LargeSizeEffect,
    }

    def __init__(self, game):
        """Initialize effect manager.

        Args:
            game: Game instance to apply effects to
        """
        self.game = game
        self.active_effects = []

    def add_effect(self, effect_type: str) -> None:
        """Add a new effect or extend existing effect of same type.

        If effect already exists, extends its duration.
        If not, creates new effect.

        Args:
            effect_type: Type of effect to add
        """
        effect_class = self.EFFECT_MAP.get(effect_type)
        if not effect_class:
            return

        # Check if effect already exists
        existing_effect = None
        for effect in self.active_effects:
            if effect.type == effect_type:
                existing_effect = effect
                break

        if existing_effect:
            # Extend duration of existing effect
            new_effect = effect_class()
            existing_effect.extend_duration(new_effect.duration)
        else:
            # Create new effect
            effect = effect_class()
            effect.apply(self.game)
            self.active_effects.append(effect)

    def update(self, dt: float) -> None:
        """Update all active effects.

        Args:
            dt: Delta time in seconds
        """
        for effect in self.active_effects[:]:
            if not effect.update(dt):
                effect.remove(self.game)
                self.active_effects.remove(effect)

    def remove_effect_by_type(self, effect_type: str) -> None:
        """Remove all effects of specified type.

        Args:
            effect_type: Type of effect to remove
        """
        for effect in self.active_effects[:]:
            if effect.type == effect_type:
                effect.schedule_remove()
                # self.active_effects.remove(effect)

    def clear_all(self) -> None:
        """Remove all active effects."""
        for effect in self.active_effects[:]:
            effect.remove(self.game)
        self.active_effects.clear()
