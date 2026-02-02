"""Level generation for procedural pipe and item placement."""

import random

from entities.coin import Coin
from entities.pipe import Pipe
from entities.powerup import (
    PowerUp,
    POWERUP_SHIELD,
    POWERUP_SLOW_MOTION,
    POWERUP_SMALL,
    DEBUFF_SPEED_UP,
    DEBUFF_LARGE
)
from core.config import GAME_CONFIG

# Pipe generation constants
INITIAL_PIPE_X = 120
RESET_PIPE_X = 80
DEFAULT_MAX_HEIGHT_CHANGE = 6
MIN_GAP_CENTER = 5
MAX_GAP_CENTER = 18

# Item placement constants
GAP_ITEM_MARGIN = 2
DEFAULT_MIN_ITEM_DISTANCE = 5
COIN_MIN_DISTANCE = 4
POWERUP_MIN_DISTANCE = 6
PLACEMENT_MAX_ATTEMPTS = 5

# Coin generation
MIN_COINS_PER_PIPE = 1
MAX_COINS_PER_PIPE = 3
COIN_OFFSET_MIN = 8
COIN_OFFSET_MAX = 18

# Powerup/Debuff placement
POWERUP_OFFSET_MIN = 10
POWERUP_OFFSET_MAX = 20


class LevelGenerator:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.pipe_spacing = GAME_CONFIG['level']['pipe_spacing']
        self.base_gap_size = GAME_CONFIG['level']['gap_size']

        self.difficulty_settings = {
            'easy': {'gap_size': 10, 'spacing': 45},
            'medium': {'gap_size': 8, 'spacing': 40},
            'hard': {'gap_size': 6, 'spacing': 35}
        }

        settings = self.difficulty_settings.get(difficulty, self.difficulty_settings['medium'])
        self.gap_size = settings['gap_size']
        self.pipe_spacing = settings['spacing']

        self.next_pipe_x = INITIAL_PIPE_X

        self.coin_spawn_rate = GAME_CONFIG['items']['coin_spawn_rate']
        self.powerup_spawn_rate = GAME_CONFIG['items']['powerup_spawn_rate']
        self.debuff_spawn_rate = GAME_CONFIG['items']['debuff_spawn_rate']

        self.last_gap_center = None
        self.max_height_change = DEFAULT_MAX_HEIGHT_CHANGE

    def generate_pipe(self):
        if self.last_gap_center is None:
            gap_center = random.randint(MIN_GAP_CENTER, MAX_GAP_CENTER)
        else:
            min_center = max(MIN_GAP_CENTER, self.last_gap_center - self.max_height_change)
            max_center = min(MAX_GAP_CENTER, self.last_gap_center + self.max_height_change)
            gap_center = random.randint(min_center, max_center)

        self.last_gap_center = gap_center

        y_top = gap_center - self.gap_size // 2
        y_bottom = gap_center + self.gap_size // 2

        pipe = Pipe(self.next_pipe_x, y_top, y_bottom, self.gap_size)
        self.next_pipe_x += self.pipe_spacing

        return pipe

    def should_generate_pipe(self, current_pipes):
        if not current_pipes:
            return True

        rightmost = max(current_pipes, key=lambda p: p.x)
        return rightmost.x < self.next_pipe_x - self.pipe_spacing

    def generate_items_for_pipe(self, pipe):
        items = []

        gap_start = pipe.y_top + GAP_ITEM_MARGIN
        gap_end = pipe.y_bottom - GAP_ITEM_MARGIN

        def is_too_close(x, y, min_dist=DEFAULT_MIN_ITEM_DISTANCE):
            for item in items:
                dx = abs(item.x - x)
                dy = abs(item.y - y)
                if dx < min_dist and dy < min_dist:
                    return True
            return False

        if random.random() < self.coin_spawn_rate:
            num_coins = random.randint(MIN_COINS_PER_PIPE, MAX_COINS_PER_PIPE)
            for _ in range(num_coins):
                for attempt in range(PLACEMENT_MAX_ATTEMPTS):
                    coin_x = pipe.x + random.randint(COIN_OFFSET_MIN, COIN_OFFSET_MAX)
                    coin_y = random.randint(gap_start, gap_end)

                    if not is_too_close(coin_x, coin_y, min_dist=COIN_MIN_DISTANCE):
                        items.append(Coin(coin_x, coin_y))
                        break

        if random.random() < self.powerup_spawn_rate:
            powerup_types = [POWERUP_SHIELD, POWERUP_SLOW_MOTION, POWERUP_SMALL]
            powerup_type = random.choice(powerup_types)

            for attempt in range(PLACEMENT_MAX_ATTEMPTS):
                powerup_x = pipe.x + random.randint(POWERUP_OFFSET_MIN, POWERUP_OFFSET_MAX)
                powerup_y = random.randint(gap_start, gap_end)

                if not is_too_close(powerup_x, powerup_y, min_dist=POWERUP_MIN_DISTANCE):
                    items.append(PowerUp(powerup_x, powerup_y, powerup_type))
                    break

        if random.random() < self.debuff_spawn_rate:
            debuff_types = [DEBUFF_SPEED_UP, DEBUFF_LARGE]
            debuff_type = random.choice(debuff_types)

            for attempt in range(PLACEMENT_MAX_ATTEMPTS):
                debuff_x = pipe.x + random.randint(POWERUP_OFFSET_MIN, POWERUP_OFFSET_MAX)
                debuff_y = random.randint(gap_start, gap_end)

                if not is_too_close(debuff_x, debuff_y, min_dist=POWERUP_MIN_DISTANCE):
                    items.append(PowerUp(debuff_x, debuff_y, debuff_type))
                    break

        return items

    def reset(self):
        self.next_pipe_x = RESET_PIPE_X
        self.last_gap_center = None

    @classmethod
    def from_genome(cls, genome):
        from core.level_genome import LevelGenome

        generator = cls(difficulty='custom')

        generator.pipe_spacing = int(genome.get('pipe_spacing'))
        generator.gap_size = int(genome.get('gap_size'))
        generator.max_height_change = int(genome.get('max_height_change'))

        generator.coin_spawn_rate = genome.get('coin_spawn_rate')
        generator.powerup_spawn_rate = genome.get('powerup_spawn_rate')
        generator.debuff_spawn_rate = genome.get('debuff_spawn_rate')

        generator._genome_params = {
            'coin_offset_min': int(genome.get('coin_offset_min')),
            'coin_offset_max': int(genome.get('coin_offset_max')),
            'item_spacing': int(genome.get('item_spacing')),
            'gap_center_variance': genome.get('gap_center_variance')
        }

        return generator
