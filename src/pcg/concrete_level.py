"""Concrete level representation with specific pipe and item positions."""

import random
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Pipe:
    x: float
    gap_center: float
    gap_size: float

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "gap_center": self.gap_center, "gap_size": self.gap_size}

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "Pipe":
        return cls(x=data["x"], gap_center=data["gap_center"], gap_size=data["gap_size"])


@dataclass
class Item:
    x: float
    y: float
    type: str  # 'coin', 'powerup', 'debuff'
    is_gold: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {"x": self.x, "y": self.y, "type": self.type, "is_gold": self.is_gold}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        return cls(
            x=data["x"],
            y=data["y"],
            type=data["type"],
            is_gold=data.get("is_gold", False),
        )


@dataclass
class ConcreteLevel:
    pipes: List[Pipe] = field(default_factory=list)
    items: List[Item] = field(default_factory=list)
    length: float = 300.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "length": self.length,
            "pipes": [p.to_dict() for p in self.pipes],
            "items": [i.to_dict() for i in self.items],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConcreteLevel":
        return cls(
            length=data.get("length", 300.0),
            pipes=[Pipe.from_dict(p) for p in data.get("pipes", [])],
            items=[Item.from_dict(i) for i in data.get("items", [])],
        )

    @classmethod
    def generate_from_params(cls, params: Dict[str, float], length: float = 900.0) -> "ConcreteLevel":
        """
        Generate a concrete level from procedural parameters.

        This converts the old parametric representation to concrete pipes/items.
        """
        pipes = []
        items = []

        pipe_spacing = params.get("pipe_spacing", 40.0)
        gap_size = params.get("gap_size", 8.0)
        max_height_change = params.get("max_height_change", 6.0)
        gap_center_variance = params.get("gap_center_variance", 5.0)

        coin_spawn_rate = params.get("coin_spawn_rate", 0.3)
        powerup_spawn_rate = params.get("powerup_spawn_rate", 0.1)
        debuff_spawn_rate = params.get("debuff_spawn_rate", 0.05)
        gold_coin_probability = params.get("gold_coin_probability", 0.15)

        # Generate pipes
        current_x = pipe_spacing
        current_gap_center = 12.0  # Middle of screen (height=24)

        while current_x < length:
            # Vary gap size slightly
            this_gap_size = gap_size + random.uniform(-0.3, 0.3)
            this_gap_size = max(7.5, min(10.5, this_gap_size))

            # Vary gap center
            delta = random.uniform(-max_height_change, max_height_change)
            current_gap_center += delta
            current_gap_center = max(
                this_gap_size / 2 + 2,
                min(24 - this_gap_size / 2 - 2, current_gap_center),
            )

            # Add some random variance
            gap_center_with_variance = current_gap_center + random.uniform(
                -gap_center_variance / 2, gap_center_variance / 2
            )
            gap_center_with_variance = max(
                this_gap_size / 2 + 2,
                min(24 - this_gap_size / 2 - 2, gap_center_with_variance),
            )

            pipes.append(
                Pipe(
                    x=current_x,
                    gap_center=gap_center_with_variance,
                    gap_size=this_gap_size,
                )
            )

            # Add items BETWEEN pipes (in safe zone, not near the pipe)
            safe_zone_start = current_x + 15  # At least 15 units after pipe
            # Account for spacing variance (0.8x to 1.2x) - use minimum to ensure safety
            safe_zone_end = current_x + pipe_spacing * 0.8 - 15  # 15 units before next pipe minimum

            if random.random() < coin_spawn_rate and safe_zone_end > safe_zone_start:
                coin_x = random.uniform(safe_zone_start, safe_zone_end)
                # Place coin in the safe middle area of the gap
                coin_y = gap_center_with_variance + random.uniform(-this_gap_size / 4, this_gap_size / 4)
                coin_y = max(2, min(22, coin_y))
                is_gold = random.random() < gold_coin_probability

                items.append(Item(x=coin_x, y=coin_y, type="coin", is_gold=is_gold))

            if random.random() < powerup_spawn_rate and safe_zone_end > safe_zone_start:
                powerup_x = random.uniform(safe_zone_start, safe_zone_end)
                powerup_y = gap_center_with_variance + random.uniform(-this_gap_size / 4, this_gap_size / 4)
                powerup_y = max(2, min(22, powerup_y))

                items.append(Item(x=powerup_x, y=powerup_y, type="powerup"))

            if random.random() < debuff_spawn_rate and safe_zone_end > safe_zone_start:
                debuff_x = random.uniform(safe_zone_start, safe_zone_end)
                debuff_y = gap_center_with_variance + random.uniform(-this_gap_size / 4, this_gap_size / 4)
                debuff_y = max(2, min(22, debuff_y))

                items.append(Item(x=debuff_x, y=debuff_y, type="debuff"))

            # Next pipe
            spacing_variance = pipe_spacing * 0.2
            current_x += pipe_spacing + random.uniform(-spacing_variance, spacing_variance)

        return cls(pipes=pipes, items=items, length=length)

    def get_pipes_in_range(self, x_start: float, x_end: float) -> List[Pipe]:
        return [p for p in self.pipes if x_start <= p.x <= x_end]

    def get_items_in_range(self, x_start: float, x_end: float) -> List[Item]:
        return [i for i in self.items if x_start <= i.x <= x_end]

    def compute_features(self) -> Dict[str, float]:
        """Compute behavioral features for MAP-Elites."""
        if not self.pipes:
            return {"gap_tightness": 0.5, "item_richness": 0.5}

        # Gap tightness: average gap size (smaller = tighter)
        avg_gap = sum(p.gap_size for p in self.pipes) / len(self.pipes)
        gap_tightness = (11.0 - avg_gap) / (11.0 - 6.0)  # Normalize to [0, 1]
        gap_tightness = max(0.0, min(1.0, gap_tightness))

        # Item richness: items per pipe
        coins = [i for i in self.items if i.type == "coin"]
        powerups = [i for i in self.items if i.type == "powerup"]

        items_per_pipe = (len(coins) + len(powerups)) / max(1, len(self.pipes))
        item_richness = min(1.0, items_per_pipe / 2.0)  # 2 items per pipe = max

        return {"gap_tightness": gap_tightness, "item_richness": item_richness}
