import time
from typing import Dict, List, Optional
import numpy as np

from pcg.level_genome import LevelGenome
from pcg.map_elites import MAPElitesArchive
from pcg.evaluator import LevelEvaluator
from utils.config import PCG_CONFIG


class MAPElitesRunner:
    def __init__(self, level_tester=None, verbose=True):
        self.config = PCG_CONFIG["map_elites"]
        self.eval_config = PCG_CONFIG["evaluation"]

        self.archive = MAPElitesArchive(dims=self.config["archive_dims"])
        self.evaluator = LevelEvaluator()
        self.level_tester = level_tester
        self.verbose = verbose

        self.iteration = 0
        self.total_evaluations = 0

    def run(self, num_iterations: Optional[int] = None) -> MAPElitesArchive:
        if num_iterations is None:
            num_iterations = self.config["num_iterations"]

        if self.verbose:
            print(f"Starting MAP-Elites with {num_iterations} iterations")
            print(f"Archive dimensions: {self.config['archive_dims']}")

        start_time = time.time()

        self._initialize_archive()

        for i in range(num_iterations):
            self.iteration = i + 1

            parent = self.archive.get_random_elite()

            if parent is None:
                parent = LevelGenome()

            offspring = parent.mutate(
                mutation_rate=self.config["mutation_rate"],
                mutation_sigma=self.config["mutation_sigma"],
            )

            quality, behavior = self._evaluate_genome(offspring)

            added = self.archive.add(offspring, quality, behavior)

            if self.verbose and (i + 1) % 50 == 0:
                self._print_progress(i + 1, num_iterations, start_time)

        if self.verbose:
            self._print_final_stats(time.time() - start_time)

        return self.archive

    def _initialize_archive(self):
        """Initialize archive with random genomes."""
        num_samples = self.config["initial_samples"]

        if self.verbose:
            print(f"\nInitializing archive with {num_samples} random genomes...")

        for i in range(num_samples):
            genome = LevelGenome()  # Random initialization
            quality, behavior = self._evaluate_genome(genome)
            self.archive.add(genome, quality, behavior)

            if self.verbose and (i + 1) % 10 == 0:
                print(
                    f"  Initialized {i + 1}/{num_samples} genomes "
                    f"(coverage: {self.archive.get_coverage():.1%})"
                )

    def _evaluate_genome(self, genome: LevelGenome) -> tuple:
        """
        Evaluate a genome by testing it with bots.

        Args:
            genome: LevelGenome to evaluate

        Returns:
            (quality, behavior) tuple
        """
        self.total_evaluations += 1

        if self.level_tester is None:
            import random

            quality = random.random()
            behavior = (random.random(), random.random())
            return quality, behavior

        test_results = self.level_tester.test_genome(genome)

        quality, _ = self.evaluator.evaluate_level(test_results)

        behavior = self.evaluator.compute_behavior_features(test_results, genome)

        return quality, behavior

    def _print_progress(self, iteration: int, total: int, start_time: float):
        stats = self.archive.get_statistics()
        elapsed = time.time() - start_time
        iter_per_sec = iteration / elapsed if elapsed > 0 else 0

        print(f"\nIteration {iteration}/{total} ({iteration/total:.1%})")
        print(f"  Coverage: {stats['coverage']:.1%} ({stats['num_elites']} elites)")
        print(
            f"  Quality: avg={stats['avg_quality']:.3f}, "
            f"max={stats['max_quality']:.3f}, min={stats['min_quality']:.3f}"
        )
        print(
            f"  Speed: {iter_per_sec:.1f} iter/s, "
            f"Elapsed: {elapsed:.1f}s, ETA: {(total-iteration)/iter_per_sec:.1f}s"
        )

    def _print_final_stats(self, elapsed_time: float):
        stats = self.archive.get_statistics()

        print(f"\n{'='*60}")
        print("MAP-Elites Complete!")
        print(f"{'='*60}")
        print(f"Total iterations: {self.iteration}")
        print(f"Total evaluations: {self.total_evaluations}")
        print(f"Time elapsed: {elapsed_time:.1f}s")
        print(f"\nArchive Statistics:")
        print(f"  Coverage: {stats['coverage']:.1%} ({stats['num_elites']} elites)")
        print(
            f"  Quality: avg={stats['avg_quality']:.3f}, "
            f"max={stats['max_quality']:.3f}, min={stats['min_quality']:.3f}"
        )
        print(f"{'='*60}\n")

    def get_best_genome(self) -> Optional[LevelGenome]:
        elites = self.archive.get_all_elites()
        if not elites:
            return None

        best = max(elites, key=lambda x: x[1])
        return best[0]

    def get_diverse_genomes(self, n: int = 10) -> List[LevelGenome]:
        """
        Get n diverse genomes from different parts of behavior space.

        Args:
            n: Number of genomes to retrieve

        Returns:
            List of LevelGenome instances
        """
        elites = self.archive.get_all_elites()

        if not elites:
            return []

        if len(elites) <= n:
            return [g for g, _, _ in elites]

        # Select genomes that are spread across behavior space
        # Use k-means-like selection on cell positions
        selected = []
        remaining = elites.copy()

        # Start with random elite
        idx = np.random.randint(len(remaining))
        selected.append(remaining.pop(idx))

        # Greedily select furthest genomes
        while len(selected) < n and remaining:
            # Find genome furthest from all selected
            max_dist = -1
            best_idx = 0

            for i, (_, _, pos) in enumerate(remaining):
                # Min distance to any selected genome
                min_dist = min(
                    np.linalg.norm(np.array(pos) - np.array(sel_pos))
                    for _, _, sel_pos in selected
                )
                if min_dist > max_dist:
                    max_dist = min_dist
                    best_idx = i

            selected.append(remaining.pop(best_idx))

        return [g for g, _, _ in selected]

    def save_archive(self, filepath: str):
        self.archive.save(filepath)
        if self.verbose:
            print(f"Archive saved to {filepath}")

    def load_archive(self, filepath: str):
        self.archive = MAPElitesArchive.load(filepath)
        if self.verbose:
            stats = self.archive.get_statistics()
            print(f"Archive loaded from {filepath}")
            print(
                f"  Loaded {stats['num_elites']} elites "
                f"(coverage: {stats['coverage']:.1%})"
            )
