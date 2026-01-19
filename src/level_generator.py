"""Procedural level generator."""

import random
from entities.pipe import Pipe
from entities.coin import Coin
from entities.powerup import PowerUp
from utils.config import GAME_CONFIG


class LevelGenerator:
    """Generates pipes and obstacles procedurally."""

    def __init__(self, difficulty='medium'):
        """
        Initialize the level generator.

        Args:
            difficulty: 'easy', 'medium', or 'hard'
        """
        self.difficulty = difficulty
        self.pipe_spacing = GAME_CONFIG['level']['pipe_spacing']
        self.base_gap_size = GAME_CONFIG['level']['gap_size']

        # Difficulty modifiers
        self.difficulty_settings = {
            'easy': {'gap_size': 10, 'spacing': 45},
            'medium': {'gap_size': 8, 'spacing': 40},
            'hard': {'gap_size': 6, 'spacing': 35}
        }

        settings = self.difficulty_settings.get(difficulty, self.difficulty_settings['medium'])
        self.gap_size = settings['gap_size']
        self.pipe_spacing = settings['spacing']

        self.next_pipe_x = 120  # Start pipes off-screen (increased for bot warmup)

        # Item spawn rates
        self.coin_spawn_rate = GAME_CONFIG['items']['coin_spawn_rate']
        self.powerup_spawn_rate = GAME_CONFIG['items']['powerup_spawn_rate']
        self.debuff_spawn_rate = GAME_CONFIG['items']['debuff_spawn_rate']

        # Track last gap center for smoother transitions
        self.last_gap_center = None
        self.max_height_change = 6  # Maximum change in gap height between pipes

    def generate_pipe(self):
        """
        Generate a single pipe pair with smooth height transitions.

        Returns:
            Pipe object
        """
        # Screen bounds (account for UI and ground)
        min_gap_center = 5
        max_gap_center = 18  # 24 - 3 (ground) - 3 (safety margin)

        # Random gap center position with smooth transitions
        if self.last_gap_center is None:
            gap_center = random.randint(min_gap_center, max_gap_center)
        else:
            # Limit change from last pipe
            min_center = max(min_gap_center, self.last_gap_center - self.max_height_change)
            max_center = min(max_gap_center, self.last_gap_center + self.max_height_change)
            gap_center = random.randint(min_center, max_center)

        self.last_gap_center = gap_center

        # Calculate top and bottom pipe positions
        y_top = gap_center - self.gap_size // 2
        y_bottom = gap_center + self.gap_size // 2

        pipe = Pipe(self.next_pipe_x, y_top, y_bottom, self.gap_size)
        self.next_pipe_x += self.pipe_spacing

        return pipe

    def should_generate_pipe(self, current_pipes):
        """
        Check if a new pipe should be generated.

        Args:
            current_pipes: List of currently active pipes

        Returns:
            True if new pipe should be generated
        """
        if not current_pipes:
            return True

        # Get the rightmost pipe
        rightmost = max(current_pipes, key=lambda p: p.x)

        # Generate when the rightmost pipe is far enough left
        return rightmost.x < self.next_pipe_x - self.pipe_spacing

    def generate_items_for_pipe(self, pipe):
        """
        Generate coins and power-ups around a pipe.

        Args:
            pipe: The pipe to generate items around

        Returns:
            List of items (coins, powerups)
        """
        items = []

        # Calculate safe zone (in the gap, with margin from pipe edges)
        gap_start = pipe.y_top + 2  # +2 instead of +1 for more safety
        gap_end = pipe.y_bottom - 2  # -2 instead of -1 for more safety

        # Helper function to check if position is too close to existing items
        def is_too_close(x, y, min_dist=5):
            for item in items:
                dx = abs(item.x - x)
                dy = abs(item.y - y)
                if dx < min_dist and dy < min_dist:
                    return True
            return False

        # Coins - place away from pipe edges
        if random.random() < self.coin_spawn_rate:
            num_coins = random.randint(1, 3)
            for _ in range(num_coins):
                # Try up to 5 times to find non-overlapping position
                for attempt in range(5):
                    coin_x = pipe.x + random.randint(8, 18)  # Further from pipe (was 0-10)
                    coin_y = random.randint(gap_start, gap_end)

                    if not is_too_close(coin_x, coin_y, min_dist=4):
                        # 10% chance for gold coin
                        value = 15 if random.random() < 0.1 else 5
                        items.append(Coin(coin_x, coin_y, value))
                        break

        # Power-ups - less frequent, well-spaced
        if random.random() < self.powerup_spawn_rate:
            powerup_types = [PowerUp.SHIELD, PowerUp.SLOW_MOTION, PowerUp.SMALL]
            powerup_type = random.choice(powerup_types)

            for attempt in range(5):
                powerup_x = pipe.x + random.randint(10, 20)  # Wider range, further from pipe
                powerup_y = random.randint(gap_start, gap_end)

                if not is_too_close(powerup_x, powerup_y, min_dist=6):
                    items.append(PowerUp(powerup_x, powerup_y, powerup_type))
                    break

        # Debuffs - rare, well-separated
        if random.random() < self.debuff_spawn_rate:
            debuff_types = [PowerUp.SPEED_UP, PowerUp.LARGE]
            debuff_type = random.choice(debuff_types)

            for attempt in range(5):
                debuff_x = pipe.x + random.randint(10, 20)  # Same as powerups
                debuff_y = random.randint(gap_start, gap_end)

                if not is_too_close(debuff_x, debuff_y, min_dist=6):
                    items.append(PowerUp(debuff_x, debuff_y, debuff_type))
                    break

        return items

    def reset(self):
        """Reset the generator state."""
        self.next_pipe_x = 80
        self.last_gap_center = None

    @classmethod
    def from_genome(cls, genome):
        """
        Create a LevelGenerator from a LevelGenome.

        Args:
            genome: LevelGenome instance with parameters

        Returns:
            LevelGenerator configured with genome parameters
        """
        # Import here to avoid circular dependency
        from pcg.level_genome import LevelGenome

        generator = cls(difficulty='custom')

        # Apply genome parameters
        generator.pipe_spacing = int(genome.get('pipe_spacing'))
        generator.gap_size = int(genome.get('gap_size'))
        generator.max_height_change = int(genome.get('max_height_change'))

        # Item spawn rates
        generator.coin_spawn_rate = genome.get('coin_spawn_rate')
        generator.powerup_spawn_rate = genome.get('powerup_spawn_rate')
        generator.debuff_spawn_rate = genome.get('debuff_spawn_rate')

        # Store genome parameters for item generation
        generator._genome_params = {
            'coin_offset_min': int(genome.get('coin_offset_min')),
            'coin_offset_max': int(genome.get('coin_offset_max')),
            'item_spacing': int(genome.get('item_spacing')),
            'gold_coin_probability': genome.get('gold_coin_probability'),
            'gap_center_variance': genome.get('gap_center_variance')
        }

        return generator
