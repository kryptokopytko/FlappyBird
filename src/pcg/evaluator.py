import numpy as np
from typing import Dict, List, Tuple
from utils.config import PCG_CONFIG

INSTANT_DEATH_THRESHOLD = 50  # Distance below which is considered instant death
EXPECTED_LEVEL_LENGTH = 1000
PROGRESSION_BINS = [
    0,
    200,
    400,
    600,
    800,
    1000,
]  # Distance bins for progression analysis

EPSILON = 1e-6

IDEAL_CONTROL_CV = 0.4


class LevelEvaluator:
    """
    Quality dimensions:
    - Playability: Is the level completable and fair?
    - Balance: Do different bot strategies perform similarly?
    - Progression: Does difficulty increase smoothly?
    """

    def __init__(self):
        self.config = PCG_CONFIG["quality"]

    def evaluate_level(self, test_results: Dict[str, List[Dict]]) -> Tuple[float, Dict]:
        """
        Args:
            test_results: Dict mapping bot_name -> list of run results
                         Each run result contains: {score, distance, coins, survived, death_reason}

        Returns:
            (quality_score, metrics_dict): Overall quality and detailed metrics
        """
        metrics = {}

        playability = self._compute_playability(test_results)
        metrics["playability"] = playability

        balance = self._compute_balance(test_results)
        metrics["balance"] = balance

        progression = self._compute_progression(test_results)
        metrics["progression"] = progression

        control = self._compute_control(test_results)
        metrics["control"] = control

        quality = (
            self.config["playability_weight"] * playability
            + self.config["balance_weight"] * balance
            + self.config["progression_weight"] * progression
        )

        if control < self.config["control_threshold"]:
            quality *= 0.5  # penalty

        metrics["quality"] = quality

        return quality, metrics

    def _compute_playability(self, test_results: Dict[str, List[Dict]]) -> float:
        """
        Compute playability score based on survival rate and completion.

        Good levels should:
        - Have ~50% survival rate (not too easy, not impossible)
        - Be completable by at least some bots
        - Not have instant-death situations
        """
        all_runs = [run for runs in test_results.values() for run in runs]

        if not all_runs:
            return 0.0

        survival_rate = sum(1 for r in all_runs if r["survived"]) / len(all_runs)

        # Distance from target survival rate
        target = self.config["target_survival_rate"]
        survival_score = 1.0 - abs(survival_rate - target) / target

        # Average progress (normalized distance)
        avg_distance = np.mean([r["distance"] for r in all_runs])
        progress_score = min(1.0, avg_distance / EXPECTED_LEVEL_LENGTH)

        # Check for instant deaths (died very early)
        instant_deaths = sum(
            1 for r in all_runs if r["distance"] < INSTANT_DEATH_THRESHOLD
        ) / len(all_runs)
        instant_death_penalty = max(0, 1.0 - instant_deaths * 2)

        playability = (
            0.5 * survival_score + 0.3 * progress_score + 0.2 * instant_death_penalty
        )

        return max(0.0, min(1.0, playability))

    def _compute_balance(self, test_results: Dict[str, List[Dict]]) -> float:
        """
        Compute balance score based on performance variance between bots.

        Good levels should challenge all bot types relatively equally.
        """
        bot_avg_scores = {}

        for bot_name, runs in test_results.items():
            if runs:
                bot_avg_scores[bot_name] = np.mean([r["score"] for r in runs])

        if len(bot_avg_scores) < 2:
            return 1.0

        scores = list(bot_avg_scores.values())

        # Coefficient of variation (std / mean)
        if np.mean(scores) > 0:
            cv = np.std(scores) / np.mean(scores)
            # Lower CV = better balance
            # Map CV [0, 1] -> balance [1, 0]
            balance = max(0.0, 1.0 - cv)
        else:
            balance = 0.0

        return balance

    def _compute_progression(self, test_results: Dict[str, List[Dict]]) -> float:
        """
        Compute progression score based on difficulty curve smoothness.

        Examines score growth over distance to ensure smooth difficulty increase.
        """
        all_runs = [run for runs in test_results.values() for run in runs]

        if not all_runs:
            return 0.0

        # Group runs by distance bins
        bin_scores = [[] for _ in range(len(PROGRESSION_BINS) - 1)]

        for run in all_runs:
            dist = run["distance"]
            for i in range(len(PROGRESSION_BINS) - 1):
                if PROGRESSION_BINS[i] <= dist < PROGRESSION_BINS[i + 1]:
                    bin_scores[i].append(run["score"])
                    break

        # Compute average score per bin
        avg_scores = []
        for scores in bin_scores:
            if scores:
                avg_scores.append(np.mean(scores))

        if len(avg_scores) < 2:
            return 0.5  # Not enough data

        # Check if scores generally increase
        increases = sum(
            1 for i in range(len(avg_scores) - 1) if avg_scores[i + 1] >= avg_scores[i]
        )
        monotonicity = increases / (len(avg_scores) - 1)

        # Check smoothness (no huge jumps)
        diffs = [
            abs(avg_scores[i + 1] - avg_scores[i]) for i in range(len(avg_scores) - 1)
        ]
        max_diff = max(diffs) if diffs else 0
        avg_diff = np.mean(diffs) if diffs else 0
        smoothness = 1.0 - min(1.0, (max_diff / (avg_diff + EPSILON)) / 10)

        progression = 0.6 * monotonicity + 0.4 * smoothness

        return max(0.0, min(1.0, progression))

    def _compute_control(self, test_results: Dict[str, List[Dict]]) -> float:
        """
        Compute control score - does player skill affect outcome?

        Good levels have variance in outcomes (skill matters).
        Poor levels have all runs die at same place (unavoidable death).
        """
        all_runs = [run for runs in test_results.values() for run in runs]

        if not all_runs:
            return 0.0

        distances = [r["distance"] for r in all_runs]

        # Check variance in distances
        if len(distances) > 1:
            std = np.std(distances)
            mean = np.mean(distances)

            # Coefficient of variation
            if mean > 0:
                cv = std / mean
                # Good: CV around 0.3-0.5 (some variance, not chaos)
                # Map to [0, 1] with peak at IDEAL_CONTROL_CV
                control = 1.0 - abs(cv - IDEAL_CONTROL_CV) / IDEAL_CONTROL_CV
                control = max(0.0, min(1.0, control))
            else:
                control = 0.0
        else:
            control = 0.5  # Not enough data

        return control

    def compute_behavior_features(
        self, test_results: Dict[str, List[Dict]], genome=None
    ) -> Tuple[float, float]:
        """
        Compute behavior characterization for MAP-Elites.

        Args:
            test_results: Bot test results
            genome: LevelGenome instance (optional, for genome-based features)

        Returns:
            (gap_tightness, item_richness): Two features for 2D behavior space

            - Gap_tightness: How tight are gaps? (0=large gaps, 1=small gaps)
            - Item_richness: How many items spawn? (0=sparse items, 1=rich items)
        """
        all_runs = [run for runs in test_results.values() for run in runs]

        if not all_runs:
            return (0.5, 0.5)

        if genome is not None:
            gap_size = genome.get("gap_size")
            # Normalize gap_size from [7, 14] to [1, 0] (tight to loose)
            # gap_tightness = 1 means tight (gap=7), = 0 means loose (gap=14)
            gap_tightness = (14 - gap_size) / (14 - 7)
            gap_tightness = max(0.0, min(1.0, gap_tightness))

            # Item richness: Based on coin + powerup spawn rates from genome
            # Higher rates = more items = richer level
            coin_rate = genome.get("coin_spawn_rate")
            powerup_rate = genome.get("powerup_spawn_rate")

            # Average of coin and powerup rates (both in [0.0, 1.0] range roughly)
            # Coin rate: [0.2, 0.8], Powerup rate: [0.0, 0.4]
            # Normalize to [0, 1]
            coin_normalized = (coin_rate - 0.2) / (0.8 - 0.2)
            powerup_normalized = powerup_rate / 0.4

            # Weighted average: coins matter more than powerups
            item_richness = 0.7 * coin_normalized + 0.3 * powerup_normalized
            item_richness = max(0.0, min(1.0, item_richness))
        else:
            # Fallback if genome not provided
            gap_tightness = 0.5
            item_richness = 0.5

        return (max(0.0, min(1.0, gap_tightness)), max(0.0, min(1.0, item_richness)))
