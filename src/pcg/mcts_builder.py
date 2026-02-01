import random
from typing import Tuple, Dict, Optional

from pcg.mcts_state import MCTSState, MCTSAction, generate_all_actions, apply_action
from pcg.mcts_node import MCTSNode
from pcg.level_genome import LevelGenome
from pcg.evaluator import LevelEvaluator
from pcg.level_tester import LevelTester


class MCTSBuilder:
    def __init__(
        self,
        level_tester: LevelTester,
        exploration_constant: float = 1.414,
        use_cache: bool = True
    ):
        self.level_tester = level_tester
        self.evaluator = LevelEvaluator()
        self.exploration_constant = exploration_constant
        self.use_cache = use_cache
        self.evaluation_cache: Dict[str, Tuple[float, Tuple[float, float]]] = {}
        self.all_actions = generate_all_actions()

    def search(
        self,
        num_simulations: int,
        target_pipes: int = 12,
        initial_state: Optional[MCTSState] = None
    ) -> Tuple[LevelGenome, float, Tuple[float, float]]:
        if initial_state is None:
            initial_state = MCTSState(target_num_pipes=target_pipes)

        root = MCTSNode(initial_state, available_actions=self.all_actions)

        for sim in range(num_simulations):
            node = self._select(root)

            if not node.is_terminal() and not node.is_fully_expanded():
                node = self._expand(node)

            quality, behavior = self._simulate(node.state)

            self._backpropagate(node, quality)

        best_genome = self._get_best_genome(root)

        test_results = self.level_tester.test_genome(best_genome)
        final_quality, _ = self.evaluator.evaluate_level(test_results, best_genome)
        final_behavior = self.evaluator.compute_behavior_features(test_results, best_genome)

        return best_genome, final_quality, final_behavior

    def _select(self, node: MCTSNode) -> MCTSNode:
        while not node.is_terminal() and node.is_fully_expanded():
            if not node.children:
                break
            node = node.select_child(self.exploration_constant)
        return node

    def _expand(self, node: MCTSNode) -> MCTSNode:
        if node.is_terminal():
            return node

        if not node.untried_actions:
            return node

        action = node.untried_actions.pop(random.randint(0, len(node.untried_actions) - 1))

        new_state = apply_action(node.state, action)

        child = node.expand(action, new_state, self.all_actions)

        return child

    def _simulate(self, state: MCTSState) -> Tuple[float, Tuple[float, float]]:
        state_hash = state.compute_hash()
        if self.use_cache and state_hash in self.evaluation_cache:
            return self.evaluation_cache[state_hash]

        rollout_state = state.copy()

        while not rollout_state.is_complete():
            action = random.choice(self.all_actions)
            rollout_state = apply_action(rollout_state, action)

        genome = rollout_state.to_level_genome()

        test_results = self.level_tester.test_genome(genome)
        quality, _ = self.evaluator.evaluate_level(test_results, genome)
        behavior = self.evaluator.compute_behavior_features(test_results, genome)

        if self.use_cache:
            self.evaluation_cache[state_hash] = (quality, behavior)

        return quality, behavior

    def _backpropagate(self, node: MCTSNode, reward: float):
        while node is not None:
            node.update(reward)
            node = node.parent

    def _get_best_genome(self, root: MCTSNode) -> LevelGenome:
        state = root.state.copy()

        current_node = root
        while not current_node.is_terminal():
            best_action = current_node.best_action()
            if best_action is None:
                break

            state = apply_action(state, best_action)

            if best_action in current_node.children:
                current_node = current_node.children[best_action]
            else:
                break

        while not state.is_complete():
            action = random.choice(self.all_actions)
            state = apply_action(state, action)

        return state.to_level_genome()
