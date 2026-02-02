import numpy as np
from typing import Dict, List, Tuple
from core.config import PCG_CONFIG

INSTANT_DEATH_THRESHOLD = 50
EXPECTED_LEVEL_LENGTH = 900
PROGRESSION_BINS = [0, 150, 300, 450, 600, 750, 900]

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

    def evaluate_level(self, test_results: Dict[str, List[Dict]], genome=None) -> Tuple[float, Dict]:
        """
        Args:
            test_results: Dict mapping bot_name -> list of run results
                         Each run result contains: {score, distance, coins, survived, death_reason}
            genome: Optional LevelGenome for computing structural penalties

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

        # Difficulty check: penalize if flat_bot performs too well
        flat_bot_penalty = self._compute_flat_bot_penalty(test_results)
        metrics["flat_bot_penalty"] = flat_bot_penalty

        # Vertical variance penalty: penalize flat/boring levels
        vertical_penalty = self._compute_vertical_variance_penalty(genome)
        metrics["vertical_penalty"] = vertical_penalty

        quality = (
            self.config["playability_weight"] * playability
            + self.config["balance_weight"] * balance
            + self.config["progression_weight"] * progression
            - flat_bot_penalty  # Subtract penalty for easy levels
            - vertical_penalty  # Subtract penalty for flat/boring levels
        )

        # Control penalty removed - it was penalizing 95% of levels due to bot capability differences
        # instead of measuring actual player skill variance

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
        Compute balance score based on relative bot performance.

        Uses distance-based ratio instead of CV to handle bot capability differences.
        Bots have different strengths (coin_collector always finishes, others may fail),
        so we measure relative performance ratio rather than absolute variance.
        """
        bot_avg_distances = {}

        for bot_name, runs in test_results.items():
            if runs:
                bot_avg_distances[bot_name] = np.mean([r["distance"] for r in runs])

        if len(bot_avg_distances) < 2:
            return 1.0

        distances = list(bot_avg_distances.values())
        max_dist = max(distances)
        mean_dist = np.mean(distances)

        if mean_dist > 0:
            # Ratio of max to mean (ideal: 1.0-1.2x)
            ratio = max_dist / mean_dist

            # Saturation: don't penalize if max is only 1.2x mean
            # Reduced from 1.5 to decrease saturation (60% → less saturation)
            if ratio <= 1.2:
                balance = 1.0
            else:
                # Logarithmic penalty for higher ratios
                # ratio=1.5 → balance=0.77, ratio=2.0 → balance=0.56
                balance = 1.0 / (1.0 + (ratio - 1.2))
        else:
            balance = 0.0

        return min(1.0, max(0.0, balance))

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

    def _compute_flat_bot_penalty(self, test_results: Dict[str, List[Dict]]) -> float:
        """
        Compute penalty if flat_bot performs too well.

        Flat_bot is a stupid bot that only works on flat/easy levels.
        If it survives or travels far, the level is too easy and should be penalized.

        Returns:
            Penalty score (0 to 1+, higher = worse)
        """
        if "flat" not in test_results:
            return 0.0

        flat_runs = test_results["flat"]
        if not flat_runs:
            return 0.0

        # Average distance traveled by flat_bot
        avg_distance = sum(r["distance"] for r in flat_runs) / len(flat_runs)
        survival_rate = sum(1 for r in flat_runs if r["survived"]) / len(flat_runs)

        # Penalize based on how far flat_bot traveled
        # 0-100: no penalty (good, died early)
        # 100-300: small penalty (getting too far)
        # 300-600: medium penalty (way too easy)
        # 600+: large penalty (trivially easy)
        distance_penalty = 0.0
        if avg_distance > 600:
            distance_penalty = 0.8
        elif avg_distance > 300:
            distance_penalty = 0.5
        elif avg_distance > 100:
            distance_penalty = 0.2

        # Additional penalty if flat_bot survives
        survival_penalty = survival_rate * 0.5

        total_penalty = distance_penalty + survival_penalty

        return min(1.5, total_penalty)  # Cap at 1.5

    def _compute_vertical_variance_penalty(self, genome) -> float:
        """
        Compute penalty for low vertical variance (flat/boring levels).

        Levels should have variety in pipe heights to be interesting.
        Low vertical_variance means pipes are at similar heights = boring.

        Returns:
            Penalty score (0 to 1, higher = worse)
        """
        if genome is None:
            return 0.0

        features = genome.level.compute_features()
        vertical_variance = features.get("vertical_variance", 0.5)

        # Penalize low vertical variance
        # vertical_variance < 0.2 → high penalty (very flat)
        # vertical_variance < 0.3 → medium penalty
        # vertical_variance < 0.4 → small penalty
        # vertical_variance >= 0.4 → no penalty (good variety)

        if vertical_variance < 0.2:
            return 1.0  # Very flat - strong penalty
        elif vertical_variance < 0.3:
            return 0.6  # Somewhat flat - medium penalty
        elif vertical_variance < 0.4:
            return 0.3  # Slightly flat - small penalty
        else:
            return 0.0  # Good variety - no penalty

    def compute_behavior_features(
        self, test_results: Dict[str, List[Dict]], genome=None
    ) -> Tuple[float, float]:
        """
        Compute behavior characterization for MAP-Elites.

        Uses level structure features that are independent of quality metrics.

        Args:
            test_results: Bot test results
            genome: LevelGenome instance (optional, for genome-based features)

        Returns:
            (gap_tightness, spacing_density): Two features for 2D behavior space

            - Gap_tightness: How tight are gaps? (0=large gaps, 1=small gaps)
            - Spacing_density: How densely packed are pipes? (0=sparse, 1=dense)
        """
        all_runs = [run for runs in test_results.values() for run in runs]

        if not all_runs:
            return (0.5, 0.5)

        if genome is not None:
            # Use concrete level features instead of abstract parameters
            features = genome.level.compute_features()
            gap_tightness = features.get("gap_tightness", 0.5)
            spacing_density = features.get("spacing_density", 0.5)
        else:
            # Fallback if genome not provided
            gap_tightness = 0.5
            spacing_density = 0.5

        return (max(0.0, min(1.0, gap_tightness)), max(0.0, min(1.0, spacing_density)))
