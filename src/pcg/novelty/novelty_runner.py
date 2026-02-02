from novelty_archive import NoveltyArchive
from core.level_genome import LevelGenome
from pcg.evaluator import LevelEvaluator
from tests.level_tester import LevelTester


class NoveltySearchRunner:
    def __init__(self, level_tester: LevelTester, max_archive_size: int = 1000):
        self.level_tester = level_tester
        self.evaluator = LevelEvaluator()
        self.max_archive_size = max_archive_size
        self.archive = None

    def run(
        self,
        num_iterations: int,
        k_neighbors: int = 15,
        initial_samples: int = 200,
        mutation_rate: float = 0.45,
        mutation_sigma: float = 0.25,
        verbose: bool = True
    ) -> NoveltyArchive:
        config = {
            "num_iterations": num_iterations,
            "k_neighbors": k_neighbors,
            "initial_samples": initial_samples,
            "max_archive_size": self.max_archive_size,
            "mutation_rate": mutation_rate,
            "mutation_sigma": mutation_sigma
        }

        self.archive = NoveltyArchive(max_size=self.max_archive_size, config=config)

        if verbose:
            print(f"Initializing archive with {initial_samples} random genomes...")

        self._initialize_archive(initial_samples, k_neighbors, verbose)

        if verbose:
            print(f"\nRunning {num_iterations} iterations...")

        for iteration in range(num_iterations):
            if verbose:
                print(f"Iteration {iteration + 1}/{num_iterations}")

            parent = self.archive.get_random_individual()
            if parent is None:
                parent_genome = LevelGenome()
            else:
                parent_genome = parent.genome

            offspring = parent_genome.mutate(mutation_rate, mutation_sigma)

            test_results = self.level_tester.test_genome(offspring)
            behavior = self.evaluator.compute_behavior_features(test_results, offspring)
            quality, _ = self.evaluator.evaluate_level(test_results, offspring)

            novelty_score = self.archive.compute_novelty(behavior, k_neighbors)

            added = self.archive.add(offspring, behavior, novelty_score, iteration, quality)

            if verbose:
                status = "ADDED" if added else "rejected"
                print(f"  Novelty: {novelty_score:.4f}, Quality: {quality:.4f}, "
                      f"Behavior: ({behavior[0]:.2f}, {behavior[1]:.2f}), Status: {status}")

            if verbose and (iteration + 1) % 100 == 0:
                stats = self.archive.get_statistics()
                print(f"  Archive stats: size={stats['size']}, "
                      f"avg_novelty={stats['avg_novelty']:.4f}, "
                      f"avg_quality={stats['avg_quality']:.4f}")

        if verbose:
            print("\nFinal archive statistics:")
            stats = self.archive.get_statistics()
            print(f"  Size: {stats['size']}/{self.max_archive_size}")
            print(f"  Novelty: avg={stats['avg_novelty']:.4f}, "
                  f"max={stats['max_novelty']:.4f}, min={stats['min_novelty']:.4f}")
            print(f"  Quality: avg={stats['avg_quality']:.4f}, max={stats['max_quality']:.4f}")

        return self.archive

    def _initialize_archive(self, initial_samples: int, k_neighbors: int, verbose: bool):
        for i in range(initial_samples):
            if verbose and (i + 1) % 50 == 0:
                print(f"  Generated {i + 1}/{initial_samples} initial genomes")

            genome = LevelGenome()

            test_results = self.level_tester.test_genome(genome)
            behavior = self.evaluator.compute_behavior_features(test_results, genome)
            quality, _ = self.evaluator.evaluate_level(test_results, genome)

            novelty_score = self.archive.compute_novelty(behavior, k_neighbors)

            self.archive.add(genome, behavior, novelty_score, age=0, quality=quality)

    def save_archive(self, filepath: str):
        if self.archive is None:
            raise ValueError("No archive to save. Run the algorithm first.")
        self.archive.save(filepath)

    def load_archive(self, filepath: str):
        self.archive = NoveltyArchive.load(filepath)
