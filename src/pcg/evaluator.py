"""Level evaluation system for PCG quality assessment."""
import numpy as np
from typing import Dict, List, Tuple
from utils.config import PCG_CONFIG


class LevelEvaluator:
    """
    Evaluates level quality based on bot performance and playability metrics.

    Quality dimensions:
    - Playability: Is the level completable and fair?
    - Balance: Do different bot strategies perform similarly?
    - Progression: Does difficulty increase smoothly?
    """

    def __init__(self):
        self.config = PCG_CONFIG['quality']

    def evaluate_level(self, test_results: Dict[str, List[Dict]]) -> Tuple[float, Dict]:
        """
        Evaluate level quality from bot test results.

        Args:
            test_results: Dict mapping bot_name -> list of run results
                         Each run result contains: {score, distance, coins, survived, death_reason}

        Returns:
            (quality_score, metrics_dict): Overall quality and detailed metrics
        """
        metrics = {}

        # 1. Playability score
        playability = self._compute_playability(test_results)
        metrics['playability'] = playability

        # 2. Balance score (variance between bot performances)
        balance = self._compute_balance(test_results)
        metrics['balance'] = balance

        # 3. Progression score (smooth difficulty curve)
        progression = self._compute_progression(test_results)
        metrics['progression'] = progression

        # 4. Control score (player has meaningful control)
        control = self._compute_control(test_results)
        metrics['control'] = control

        # Compute weighted quality score
        quality = (
            self.config['playability_weight'] * playability +
            self.config['balance_weight'] * balance +
            self.config['progression_weight'] * progression
        )

        # Reject levels with poor control
        if control < self.config['control_threshold']:
            quality *= 0.5  # Heavy penalty

        metrics['quality'] = quality

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

        # Survival rate
        survival_rate = sum(1 for r in all_runs if r['survived']) / len(all_runs)

        # Distance from target survival rate
        target = self.config['target_survival_rate']
        survival_score = 1.0 - abs(survival_rate - target) / target

        # Average progress (normalized distance)
        avg_distance = np.mean([r['distance'] for r in all_runs])
        # Assume level length is ~1000 units
        progress_score = min(1.0, avg_distance / 1000)

        # Check for instant deaths (died very early)
        instant_deaths = sum(1 for r in all_runs if r['distance'] < 50) / len(all_runs)
        instant_death_penalty = max(0, 1.0 - instant_deaths * 2)

        playability = (
            0.5 * survival_score +
            0.3 * progress_score +
            0.2 * instant_death_penalty
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
                bot_avg_scores[bot_name] = np.mean([r['score'] for r in runs])

        if len(bot_avg_scores) < 2:
            return 1.0  # Can't measure balance with < 2 bots

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
        distance_bins = [0, 200, 400, 600, 800, 1000]
        bin_scores = [[] for _ in range(len(distance_bins) - 1)]

        for run in all_runs:
            dist = run['distance']
            for i in range(len(distance_bins) - 1):
                if distance_bins[i] <= dist < distance_bins[i + 1]:
                    bin_scores[i].append(run['score'])
                    break

        # Compute average score per bin
        avg_scores = []
        for scores in bin_scores:
            if scores:
                avg_scores.append(np.mean(scores))

        if len(avg_scores) < 2:
            return 0.5  # Not enough data

        # Check if scores generally increase
        increases = sum(1 for i in range(len(avg_scores) - 1)
                       if avg_scores[i + 1] >= avg_scores[i])
        monotonicity = increases / (len(avg_scores) - 1)

        # Check smoothness (no huge jumps)
        diffs = [abs(avg_scores[i + 1] - avg_scores[i])
                for i in range(len(avg_scores) - 1)]
        max_diff = max(diffs) if diffs else 0
        avg_diff = np.mean(diffs) if diffs else 0
        smoothness = 1.0 - min(1.0, (max_diff / (avg_diff + 1e-6)) / 10)

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

        distances = [r['distance'] for r in all_runs]

        # Check variance in distances
        if len(distances) > 1:
            std = np.std(distances)
            mean = np.mean(distances)

            # Coefficient of variation
            if mean > 0:
                cv = std / mean
                # Good: CV around 0.3-0.5 (some variance, not chaos)
                # Map to [0, 1] with peak at cv=0.4
                control = 1.0 - abs(cv - 0.4) / 0.4
                control = max(0.0, min(1.0, control))
            else:
                control = 0.0
        else:
            control = 0.5  # Not enough data

        return control

    def compute_behavior_features(self, test_results: Dict[str, List[Dict]]) -> Tuple[float, float]:
        """
        Compute behavior characterization for MAP-Elites.

        Returns:
            (difficulty, accessibility): Two features for 2D behavior space

            - Difficulty: How hard is the level? (0=easy, 1=hard)
            - Accessibility: How accessible are items/coins? (0=hard to collect, 1=easy)
        """
        all_runs = [run for runs in test_results.values() for run in runs]

        if not all_runs:
            return (0.5, 0.5)

        # Difficulty: Based on survival rate and average distance
        survival_rate = sum(1 for r in all_runs if r['survived']) / len(all_runs)
        avg_distance = np.mean([r['distance'] for r in all_runs])

        # Lower survival + lower distance = harder
        difficulty = 1.0 - (survival_rate * 0.7 + min(1.0, avg_distance / 1000) * 0.3)

        # Accessibility: Based on coins collected vs distance traveled
        avg_coins_per_distance = np.mean([r['coins'] / max(1, r['distance'])
                                          for r in all_runs])

        # Normalize (assume ~0.05 coins per unit is average)
        accessibility = min(1.0, avg_coins_per_distance / 0.05)

        return (
            max(0.0, min(1.0, difficulty)),
            max(0.0, min(1.0, accessibility))
        )
