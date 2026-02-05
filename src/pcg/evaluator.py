import numpy as np
from typing import Dict, List, Tuple
from core.config import PCG_CONFIG

INSTANT_DEATH_THRESHOLD = 50
EXPECTED_LEVEL_LENGTH = 900
PROGRESSION_BINS = [0, 150, 300, 450, 600, 750, 900]
EPSILON = 1e-6
IDEAL_CONTROL_CV = 0.4


class LevelEvaluator:
    def __init__(self):
        self.config = PCG_CONFIG["quality"]

    def evaluate_level(self, test_results: Dict[str, List[Dict]], genome=None) -> Tuple[float, Dict]:
        metrics = {}

        playability = self._compute_playability(test_results)
        metrics["playability"] = playability

        hardness = self._compute_hardness(genome)
        metrics["hardness"] = hardness

        progression = self._compute_progression(test_results)
        metrics["progression"] = progression

        control = self._compute_control(test_results)
        metrics["control"] = control

        item_richness = self._compute_item_richness(genome)
        metrics["item_richness"] = item_richness

        flat_bot_penalty = self._compute_flat_bot_penalty(test_results)
        metrics["flat_bot_penalty"] = flat_bot_penalty

        vertical_penalty = self._compute_vertical_variance_penalty(genome)
        metrics["vertical_penalty"] = vertical_penalty

        quality = (
            self.config["playability_weight"] * playability
            + self.config["hardness_weight"] * hardness
            + self.config["progression_weight"] * progression
            + self.config["item_richness_weight"] * item_richness
            - flat_bot_penalty
            - vertical_penalty
        )

        metrics["quality"] = quality
        return quality, metrics

    def _compute_playability(self, test_results: Dict[str, List[Dict]]) -> float:
        all_runs = [run for runs in test_results.values() for run in runs]
        if not all_runs:
            return 0.0

        survival_rate = sum(1 for r in all_runs if r["survived"]) / len(all_runs)
        target = self.config["target_survival_rate"]
        survival_score = 1.0 - abs(survival_rate - target) / target

        avg_distance = np.mean([r["distance"] for r in all_runs])
        progress_score = min(1.0, avg_distance / EXPECTED_LEVEL_LENGTH)

        instant_deaths = sum(1 for r in all_runs if r["distance"] < INSTANT_DEATH_THRESHOLD) / len(all_runs)
        instant_death_penalty = max(0, 1.0 - instant_deaths * 2)

        playability = 0.5 * survival_score + 0.3 * progress_score + 0.2 * instant_death_penalty
        return max(0.0, min(1.0, playability))

    def _compute_hardness(self, genome) -> float:
        if genome is None:
            return 0.5

        features = genome.level.compute_features()
        gap_tightness = features.get("gap_tightness", 0.5)
        spacing_density = features.get("spacing_density", 0.5)
        hardness = 0.5 * gap_tightness + 0.5 * spacing_density
        return max(0.0, min(1.0, hardness))

    def _compute_progression(self, test_results: Dict[str, List[Dict]]) -> float:
        all_runs = [run for runs in test_results.values() for run in runs]
        if not all_runs:
            return 0.0

        bin_scores = [[] for _ in range(len(PROGRESSION_BINS) - 1)]
        for run in all_runs:
            dist = run["distance"]
            for i in range(len(PROGRESSION_BINS) - 1):
                if PROGRESSION_BINS[i] <= dist < PROGRESSION_BINS[i + 1]:
                    bin_scores[i].append(run["score"])
                    break

        avg_scores = [np.mean(scores) for scores in bin_scores if scores]
        if len(avg_scores) < 2:
            return 0.5

        increases = sum(1 for i in range(len(avg_scores) - 1) if avg_scores[i + 1] >= avg_scores[i])
        monotonicity = increases / (len(avg_scores) - 1)

        diffs = [abs(avg_scores[i + 1] - avg_scores[i]) for i in range(len(avg_scores) - 1)]
        max_diff = max(diffs) if diffs else 0
        avg_diff = np.mean(diffs) if diffs else 0
        smoothness = 1.0 - min(1.0, (max_diff / (avg_diff + EPSILON)) / 10)

        progression = 0.6 * monotonicity + 0.4 * smoothness
        return max(0.0, min(1.0, progression))

    def _compute_control(self, test_results: Dict[str, List[Dict]]) -> float:
        all_runs = [run for runs in test_results.values() for run in runs]
        if not all_runs:
            return 0.0

        distances = [r["distance"] for r in all_runs]
        if len(distances) > 1:
            std = np.std(distances)
            mean = np.mean(distances)
            if mean > 0:
                cv = std / mean
                control = 1.0 - abs(cv - IDEAL_CONTROL_CV) / IDEAL_CONTROL_CV
                return max(0.0, min(1.0, control))
            return 0.0
        return 0.5

    def _compute_flat_bot_penalty(self, test_results: Dict[str, List[Dict]]) -> float:
        if "flat" not in test_results:
            return 0.0

        flat_runs = test_results["flat"]
        if not flat_runs:
            return 0.0

        avg_distance = sum(r["distance"] for r in flat_runs) / len(flat_runs)
        survival_rate = sum(1 for r in flat_runs if r["survived"]) / len(flat_runs)

        distance_penalty = 0.0
        if avg_distance > 600:
            distance_penalty = 0.8
        elif avg_distance > 300:
            distance_penalty = 0.5
        elif avg_distance > 100:
            distance_penalty = 0.2

        survival_penalty = survival_rate * 0.5
        return min(1.5, distance_penalty + survival_penalty)

    def _compute_vertical_variance_penalty(self, genome) -> float:
        if genome is None:
            return 0.0

        features = genome.level.compute_features()
        vertical_variance = features.get("vertical_variance", 0.5)

        if vertical_variance < 0.2:
            return 1.0
        elif vertical_variance < 0.3:
            return 0.6
        elif vertical_variance < 0.4:
            return 0.3
        return 0.0

    def _compute_item_richness(self, genome) -> float:
        """
        Compute item richness based on coins, buffs, and debuffs in the level.
        Higher values mean more interesting item distribution.

        Returns:
            Float in [0, 1] where 1 is optimal item richness
        """
        if genome is None or genome.level is None:
            return 0.0

        items = genome.level.items
        if not items:
            return 0.0

        # Count different item types
        coins = sum(1 for item in items if item.type == "coin")
        buffs = sum(1 for item in items if item.type in ["small", "shield"] and item.type != "coin")
        # Note: In concrete_level.py, debuffs are also spawned as "small" or "shield"
        # For now, we'll treat all powerups as buffs and handle debuffs separately if needed

        # Calculate items per pipe (normalize by level length)
        num_pipes = len(genome.level.pipes) if genome.level.pipes else 1
        coins_per_pipe = coins / num_pipes
        buffs_per_pipe = buffs / num_pipes

        # Ideal ratios (tunable)
        ideal_coins_per_pipe = 0.4  # ~40% of pipes have coins nearby
        ideal_buffs_per_pipe = 0.15  # ~15% of pipes have buffs nearby

        # Score based on how close we are to ideal
        coin_score = 1.0 - min(1.0, abs(coins_per_pipe - ideal_coins_per_pipe) / ideal_coins_per_pipe)
        buff_score = 1.0 - min(1.0, abs(buffs_per_pipe - ideal_buffs_per_pipe) / ideal_buffs_per_pipe)

        # Bonus for having variety (both coins and buffs present)
        variety_bonus = 0.0
        if coins > 0 and buffs > 0:
            variety_bonus = 0.2

        # Weighted combination
        item_richness = 0.5 * coin_score + 0.3 * buff_score + variety_bonus

        return max(0.0, min(1.0, item_richness))

    def compute_behavior_features(self, test_results: Dict[str, List[Dict]], genome=None) -> Tuple[float, float]:
        all_runs = [run for runs in test_results.values() for run in runs]
        if not all_runs:
            return (0.5, 0.5)

        if genome is not None:
            features = genome.level.compute_features()
            gap_tightness = features.get("gap_tightness", 0.5)
            spacing_density = features.get("spacing_density", 0.5)
        else:
            gap_tightness = 0.5
            spacing_density = 0.5

        return (max(0.0, min(1.0, gap_tightness)), max(0.0, min(1.0, spacing_density)))
