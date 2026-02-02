"""Generator that replays concrete pre-generated levels."""

from typing import List
from entities.pipe import Pipe as GamePipe
from entities.coin import Coin
from entities.powerup import PowerUp
from core.concrete_level import ConcreteLevel


class ConcreteLevelGenerator:
    def __init__(self, concrete_level: ConcreteLevel):
        self.concrete_level = concrete_level
        self.generated_pipes = set()
        self.generated_items = set()

    def should_generate_pipe(self, current_pipes) -> bool:
        # Find the rightmost current pipe
        if current_pipes:
            rightmost_x = max(p.x for p in current_pipes)
        else:
            rightmost_x = 0

        # Check if there are any ungenerated pipes that should be visible
        for i, pipe_data in enumerate(self.concrete_level.pipes):
            if i not in self.generated_pipes and pipe_data.x <= rightmost_x + 100:
                return True

        return False

    def generate_pipe(self) -> GamePipe:
        # Find next ungenerated pipe
        for i, pipe_data in enumerate(self.concrete_level.pipes):
            if i not in self.generated_pipes:
                # Convert gap_center to y_top and y_bottom
                y_top = pipe_data.gap_center - pipe_data.gap_size / 2
                y_bottom = pipe_data.gap_center + pipe_data.gap_size / 2

                game_pipe = GamePipe(
                    x=pipe_data.x,
                    y_top=y_top,
                    y_bottom=y_bottom,
                    gap_size=pipe_data.gap_size,
                )
                self.generated_pipes.add(i)
                return game_pipe

        # No more pipes, return a default one far away
        y_top = 12 - 8 / 2
        y_bottom = 12 + 8 / 2
        return GamePipe(x=10000, y_top=y_top, y_bottom=y_bottom, gap_size=8)

    def generate_items_for_pipe(self, pipe: GamePipe) -> List:
        items = []

        # Find items near this pipe (within +/- 20 units)
        for i, item_data in enumerate(self.concrete_level.items):
            if i not in self.generated_items:
                if abs(item_data.x - pipe.x) < 20:
                    # Create appropriate game entity
                    if item_data.type == "coin":
                        item = Coin(x=item_data.x, y=item_data.y)
                    else:
                        item = PowerUp(x=item_data.x, y=item_data.y, powerup_type=item_data.type)

                    items.append(item)
                    self.generated_items.add(i)

        return items

    def generate_pipes(self, scroll_offset: float) -> List[GamePipe]:
        new_pipes = []
        view_start = scroll_offset
        view_end = scroll_offset + 100  # Look ahead window

        for i, pipe_data in enumerate(self.concrete_level.pipes):
            # Check if pipe is in view and not yet generated
            if view_start <= pipe_data.x <= view_end and i not in self.generated_pipes:
                # Create game pipe from concrete pipe data
                game_pipe = GamePipe(
                    x=pipe_data.x,
                    gap_center=pipe_data.gap_center,
                    gap_size=pipe_data.gap_size,
                )
                new_pipes.append(game_pipe)
                self.generated_pipes.add(i)

        return new_pipes

    def generate_items(self, scroll_offset: float) -> List:
        new_items = []
        view_start = scroll_offset
        view_end = scroll_offset + 100  # Look ahead window

        for i, item_data in enumerate(self.concrete_level.items):
            # Check if item is in view and not yet generated
            if view_start <= item_data.x <= view_end and i not in self.generated_items:
                # Create appropriate game entity
                if item_data.type == "coin":
                    item = Coin(x=item_data.x, y=item_data.y)
                else:
                    item = PowerUp(x=item_data.x, y=item_data.y, powerup_type=item_data.type)

                new_items.append(item)
                self.generated_items.add(i)

        return new_items

    def reset(self):
        """Reset generator state for a new game."""
        self.generated_pipes.clear()
        self.generated_items.clear()

    @classmethod
    def from_genome(cls, genome):
        """
        Create generator from a LevelGenome.

        Args:
            genome: LevelGenome instance with concrete level

        Returns:
            ConcreteLevelGenerator instance
        """
        return cls(genome.level)
