import math
from typing import Optional, Dict, List

from pcg.mcts_state import MCTSState, MCTSAction


class MCTSNode:
    def __init__(
        self,
        state: MCTSState,
        parent: Optional["MCTSNode"] = None,
        action: Optional[MCTSAction] = None,
        available_actions: Optional[List[MCTSAction]] = None
    ):
        self.state = state
        self.parent = parent
        self.action = action
        self.children: Dict[MCTSAction, MCTSNode] = {}
        self.visits = 0
        self.total_reward = 0.0
        self.untried_actions = available_actions.copy() if available_actions else []

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0

    def is_terminal(self) -> bool:
        return self.state.is_complete()

    def uct_value(self, exploration: float = 1.414) -> float:
        if self.visits == 0:
            return float('inf')

        if self.parent is None or self.parent.visits == 0:
            return self.total_reward / self.visits

        exploitation = self.total_reward / self.visits
        exploration_term = exploration * math.sqrt(math.log(self.parent.visits) / self.visits)

        return exploitation + exploration_term

    def select_child(self, exploration: float = 1.414) -> "MCTSNode":
        best_child = None
        best_value = -float('inf')

        for child in self.children.values():
            value = child.uct_value(exploration)
            if value > best_value:
                best_value = value
                best_child = child

        return best_child

    def expand(self, action: MCTSAction, new_state: MCTSState, available_actions: List[MCTSAction]) -> "MCTSNode":
        child_node = MCTSNode(new_state, parent=self, action=action, available_actions=available_actions)
        self.children[action] = child_node
        return child_node

    def update(self, reward: float):
        self.visits += 1
        self.total_reward += reward

    def best_action(self) -> Optional[MCTSAction]:
        if not self.children:
            return None

        best_child = None
        best_visits = -1

        for action, child in self.children.items():
            if child.visits > best_visits:
                best_visits = child.visits
                best_child = action

        return best_child

    def __repr__(self):
        return f"MCTSNode(visits={self.visits}, reward={self.total_reward:.3f}, children={len(self.children)})"
