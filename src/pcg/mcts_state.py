import random
import hashlib
from typing import List, Tuple
from dataclasses import dataclass, field

from pcg.concrete_level import ConcreteLevel, Pipe, Item
from pcg.level_genome import LevelGenome


@dataclass(frozen=True)
class MCTSAction:
    gap_size: float
    gap_center_type: str
    spacing_offset: float
    item_config: str

    def __hash__(self):
        return hash((self.gap_size, self.gap_center_type, self.spacing_offset, self.item_config))


@dataclass
class MCTSState:
    pipes: List[Pipe] = field(default_factory=list)
    items: List[Item] = field(default_factory=list)
    current_x: float = 30.0
    target_num_pipes: int = 12
    last_gap_center: float = 12.0

    def is_complete(self) -> bool:
        return len(self.pipes) >= self.target_num_pipes

    def copy(self) -> "MCTSState":
        return MCTSState(
            pipes=[Pipe(p.x, p.gap_center, p.gap_size) for p in self.pipes],
            items=[Item(i.x, i.y, i.type, i.is_gold) for i in self.items],
            current_x=self.current_x,
            target_num_pipes=self.target_num_pipes,
            last_gap_center=self.last_gap_center
        )

    def to_level_genome(self) -> LevelGenome:
        level = ConcreteLevel(
            pipes=self.pipes.copy(),
            items=self.items.copy(),
            length=900.0
        )
        return LevelGenome(level)

    def compute_hash(self) -> str:
        state_str = f"{len(self.pipes)}_{self.current_x:.1f}"
        if self.pipes:
            last_pipe = self.pipes[-1]
            state_str += f"_{last_pipe.gap_size:.1f}_{last_pipe.gap_center:.1f}"
        return hashlib.md5(state_str.encode()).hexdigest()


def map_gap_center_type(gap_center_type: str, gap_size: float, last_gap_center: float) -> float:
    min_center = gap_size / 2 + 2
    max_center = 24 - gap_size / 2 - 2
    range_size = max_center - min_center

    if gap_center_type == 'low':
        target = min_center + range_size * 0.2
    elif gap_center_type == 'mid-low':
        target = min_center + range_size * 0.4
    elif gap_center_type == 'mid':
        target = min_center + range_size * 0.5
    elif gap_center_type == 'mid-high':
        target = min_center + range_size * 0.6
    elif gap_center_type == 'high':
        target = min_center + range_size * 0.8
    else:
        target = last_gap_center

    return max(min_center, min(max_center, target))


def generate_all_actions() -> List[MCTSAction]:
    actions = []
    gap_sizes = [6.0, 7.0, 8.0, 9.0, 10.0, 11.0]
    gap_center_types = ['low', 'mid-low', 'mid', 'mid-high', 'high']
    spacing_offsets = [-10.0, -5.0, 0.0, 5.0, 10.0]
    item_configs = ['none', 'coin', 'powerup', 'coin+powerup']

    for gap_size in gap_sizes:
        for gap_center_type in gap_center_types:
            for spacing_offset in spacing_offsets:
                for item_config in item_configs:
                    actions.append(MCTSAction(gap_size, gap_center_type, spacing_offset, item_config))

    return actions


def apply_action(state: MCTSState, action: MCTSAction) -> MCTSState:
    new_state = state.copy()

    gap_center = map_gap_center_type(action.gap_center_type, action.gap_size, state.last_gap_center)

    pipes_remaining = state.target_num_pipes - len(state.pipes)
    distance_remaining = 900.0 - state.current_x
    base_spacing = distance_remaining / (pipes_remaining + 0.5) if pipes_remaining > 0 else 40.0
    base_spacing = max(30.0, min(60.0, base_spacing))
    spacing = base_spacing + action.spacing_offset

    new_x = state.current_x + spacing
    new_state.pipes.append(Pipe(new_x, gap_center, action.gap_size))
    new_state.current_x = new_x
    new_state.last_gap_center = gap_center

    if 'coin' in action.item_config:
        coin_x = state.current_x + spacing * 0.5
        coin_y = gap_center + random.uniform(-action.gap_size * 0.25, action.gap_size * 0.25)
        coin_y = max(2, min(22, coin_y))
        is_gold = random.random() < 0.15
        new_state.items.append(Item(coin_x, coin_y, 'coin', is_gold))

    if 'powerup' in action.item_config:
        powerup_x = state.current_x + spacing * 0.6
        powerup_y = gap_center + random.uniform(-action.gap_size * 0.25, action.gap_size * 0.25)
        powerup_y = max(2, min(22, powerup_y))
        new_state.items.append(Item(powerup_x, powerup_y, 'powerup'))

    return new_state
