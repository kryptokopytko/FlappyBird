"""Level genome storing concrete pipe and item positions."""

import random
from typing import Dict, Any
from core.config import PCG_CONFIG
from core.concrete_level import ConcreteLevel, Pipe, Item


class LevelGenome:
    """Genome storing concrete level with specific pipe and item positions."""

    def __init__(self, level: ConcreteLevel = None):
        if level is None:
            params = self._generate_random_params()
            self.level = ConcreteLevel.generate_from_params(params, length=900.0)
        else:
            self.level = level

    @staticmethod
    def _generate_random_params() -> Dict[str, float]:
        bounds = PCG_CONFIG["genome_bounds"]
        return {
            name: random.uniform(bounds[name][0], bounds[name][1])
            for name in [
                "pipe_spacing",
                "gap_size",
                "max_height_change",
                "gap_center_variance",
                "coin_spawn_rate",
                "powerup_spawn_rate",
                "debuff_spawn_rate",
                "coin_offset_min",
                "coin_offset_max",
                "item_spacing",
            ]
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.level.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LevelGenome":
        level = ConcreteLevel.from_dict(data)
        return cls(level)

    def copy(self) -> "LevelGenome":
        new_pipes = [Pipe(p.x, p.gap_center, p.gap_size) for p in self.level.pipes]
        new_items = [Item(i.x, i.y, i.type) for i in self.level.items]
        new_level = ConcreteLevel(new_pipes, new_items, self.level.length)
        return LevelGenome(new_level)

    def get(self, param_name: str) -> float:
        """Get computed level features like average gap_size, pipe_spacing, etc."""
        if param_name == "gap_size":
            if not self.level.pipes:
                return 8.0
            return sum(p.gap_size for p in self.level.pipes) / len(self.level.pipes)

        elif param_name == "pipe_spacing":
            if len(self.level.pipes) < 2:
                return 40.0
            spacings = [
                self.level.pipes[i + 1].x - self.level.pipes[i].x
                for i in range(len(self.level.pipes) - 1)
            ]
            return sum(spacings) / len(spacings)

        elif param_name == "coin_spawn_rate":
            coins = [i for i in self.level.items if i.type == "coin"]
            if not self.level.pipes:
                return 0.3
            return len(coins) / len(self.level.pipes)

        elif param_name == "powerup_spawn_rate":
            powerups = [i for i in self.level.items if i.type == "powerup"]
            if not self.level.pipes:
                return 0.1
            return len(powerups) / len(self.level.pipes)

        else:
            # Default values for other params
            return 0.0

    def mutate(self, mutation_rate=0.25, mutation_sigma=0.15) -> "LevelGenome":
        """
        Mutate concrete level by adjusting pipe positions, gaps, and items.

        Args:
            mutation_rate: Probability of mutating each element
            mutation_sigma: Magnitude of mutations (as fraction of valid range)

        Returns:
            New mutated LevelGenome instance
        """
        mutated = self.copy()

        # Mutate pipes
        for pipe in mutated.level.pipes:
            if random.random() < mutation_rate:
                # Mutate gap_size
                if random.random() < 0.4:
                    delta = random.gauss(0, mutation_sigma * 3.0)  # 3.0 = gap range (10.5-7.5)
                    pipe.gap_size = max(7.5, min(10.5, pipe.gap_size + delta))

                # Mutate gap_center
                if random.random() < 0.4:
                    delta = random.gauss(0, mutation_sigma * 12.0)  # 12 = half screen
                    pipe.gap_center = max(
                        pipe.gap_size / 2 + 2,
                        min(24 - pipe.gap_size / 2 - 2, pipe.gap_center + delta),
                    )

                # Mutate x position slightly
                if random.random() < 0.2:
                    delta = random.gauss(0, mutation_sigma * 10.0)
                    pipe.x = max(30, min(870, pipe.x + delta))

        # Sort pipes by x
        mutated.level.pipes.sort(key=lambda p: p.x)

        # Maybe add a pipe (increased from 0.3 to 0.6 for better structural diversity)
        if random.random() < mutation_rate * 0.6 and len(mutated.level.pipes) < 12:
            # Find a gap between pipes
            if len(mutated.level.pipes) >= 2:
                spacings = [
                    (mutated.level.pipes[i + 1].x - mutated.level.pipes[i].x, i)
                    for i in range(len(mutated.level.pipes) - 1)
                ]
                spacings.sort(reverse=True)

                # Insert in largest gap
                if spacings[0][0] > 50:
                    i = spacings[0][1]
                    new_x = (mutated.level.pipes[i].x + mutated.level.pipes[i + 1].x) / 2
                    new_gap_center = (mutated.level.pipes[i].gap_center + mutated.level.pipes[i + 1].gap_center) / 2
                    new_gap_size = (mutated.level.pipes[i].gap_size + mutated.level.pipes[i + 1].gap_size) / 2

                    mutated.level.pipes.append(Pipe(new_x, new_gap_center, new_gap_size))
                    mutated.level.pipes.sort(key=lambda p: p.x)

        # Maybe remove a pipe (increased from 0.2 to 0.5 for better exploration)
        if random.random() < mutation_rate * 0.5 and len(mutated.level.pipes) > 5:
            mutated.level.pipes.pop(random.randint(0, len(mutated.level.pipes) - 1))

        # Mutate items
        for item in mutated.level.items:
            if random.random() < mutation_rate:
                # Mutate position
                if random.random() < 0.5:
                    item.x += random.gauss(0, mutation_sigma * 20.0)
                    item.x = max(0, min(900, item.x))

                if random.random() < 0.5:
                    item.y += random.gauss(0, mutation_sigma * 10.0)
                    item.y = max(2, min(22, item.y))

        # Fix any items that are too close to pipes after mutation
        for item in mutated.level.items:
            # Find closest pipe
            min_dist = float('inf')
            closest_pipe_idx = -1
            for i, pipe in enumerate(mutated.level.pipes):
                dist = abs(item.x - pipe.x)
                if dist < min_dist:
                    min_dist = dist
                    closest_pipe_idx = i

            # If too close to a pipe, move to safe zone between pipes
            if min_dist < 15 and closest_pipe_idx >= 0:
                pipe = mutated.level.pipes[closest_pipe_idx]
                # Try to move between this pipe and the next one
                if closest_pipe_idx < len(mutated.level.pipes) - 1:
                    next_pipe = mutated.level.pipes[closest_pipe_idx + 1]
                    gap_size = next_pipe.x - pipe.x
                    # Only place in middle if gap is large enough
                    if gap_size > 30:
                        item.x = pipe.x + gap_size * 0.5
                    else:
                        # Gap too small, place after next pipe
                        item.x = next_pipe.x + 15
                elif closest_pipe_idx > 0:
                    prev_pipe = mutated.level.pipes[closest_pipe_idx - 1]
                    gap_size = pipe.x - prev_pipe.x
                    if gap_size > 30:
                        item.x = prev_pipe.x + gap_size * 0.5
                    else:
                        item.x = pipe.x + 15
                else:
                    # Move to safe distance after pipe
                    item.x = pipe.x + 20

        # Maybe add an item (ensure it's in a safe zone)
        if random.random() < mutation_rate * 0.4 and len(mutated.level.items) < 90:
            # Pick a random gap between pipes
            if len(mutated.level.pipes) >= 2:
                pipe_idx = random.randint(0, len(mutated.level.pipes) - 2)
                pipe1 = mutated.level.pipes[pipe_idx]
                pipe2 = mutated.level.pipes[pipe_idx + 1]

                # Place in safe zone between pipes (at least 15 units from each)
                gap_size = pipe2.x - pipe1.x
                if gap_size > 30:  # Only add if gap is large enough
                    x = random.uniform(pipe1.x + 15, pipe2.x - 15)
                    y = random.uniform(6, 18)
                    item_type = random.choice(["coin", "coin", "coin", "shield", "large", "small"])
                    # item_type = random.choice(["coin", "coin", "coin", "powerup", "debuff"])

                    mutated.level.items.append(Item(x, y, item_type))

        # Maybe remove an item
        if random.random() < mutation_rate * 0.3 and len(mutated.level.items) > 3:
            mutated.level.items.pop(random.randint(0, len(mutated.level.items) - 1))

        return mutated

    def __repr__(self):
        return f"LevelGenome(pipes={len(self.level.pipes)}, items={len(self.level.items)})"
