import random
from typing import Tuple, Optional

from pcg.mcts_builder import MCTSBuilder
from pcg.mcts_archive import MCTSArchive
from pcg.level_tester import LevelTester


class MCTSQDRunner:
    def __init__(
        self,
        level_tester: LevelTester,
        exploration_constant: float = 1.414,
        archive_dims: Tuple[int, int] = (6, 6)
    ):
        self.builder = MCTSBuilder(level_tester, exploration_constant)
        self.archive_dims = archive_dims
        self.archive: Optional[MCTSArchive] = None

    def run(
        self,
        num_iterations: int,
        simulations_per_level: int,
        target_pipes: int = 17,
        target_pipes_variance: int = 2,
        verbose: bool = True
    ) -> MCTSArchive:
        config = {
            "num_iterations": num_iterations,
            "simulations_per_level": simulations_per_level,
            "exploration_constant": self.builder.exploration_constant,
            "target_pipes": target_pipes
        }
        self.archive = MCTSArchive(dims=self.archive_dims, config=config)

        strategic_phase = int(num_iterations * 0.25)

        for iteration in range(num_iterations):
            if verbose:
                print(f"Iteration {iteration + 1}/{num_iterations}")

            pipes_for_this_level = random.randint(
                target_pipes - target_pipes_variance,
                target_pipes + target_pipes_variance
            )
            genome, quality, behavior = self.builder.search(simulations_per_level, pipes_for_this_level)

            added = self.archive.add(genome, quality, behavior)

            if verbose:
                status = "ADDED" if added else "rejected"
                cell = self.archive.get_cell_index(behavior)
                print(f"  Quality: {quality:.4f}, Behavior: ({behavior[0]:.2f}, {behavior[1]:.2f}), "
                      f"Cell: {cell}, Status: {status}")

            if verbose and (iteration + 1) % 5 == 0:
                stats = self.archive.get_statistics()
                print(f"  Archive stats: coverage={stats['coverage']:.2%}, "
                      f"avg_quality={stats['avg_quality']:.4f}, "
                      f"max_quality={stats['max_quality']:.4f}")

        if verbose:
            print("\nFinal archive statistics:")
            stats = self.archive.get_statistics()
            print(f"  Coverage: {stats['coverage']:.2%} ({stats['num_elites']}/{self.archive_dims[0] * self.archive_dims[1]} cells)")
            print(f"  Quality: avg={stats['avg_quality']:.4f}, max={stats['max_quality']:.4f}, min={stats['min_quality']:.4f}")

        return self.archive

    def save_archive(self, filepath: str):
        if self.archive is None:
            raise ValueError("No archive to save. Run the algorithm first.")
        self.archive.save(filepath)

    def load_archive(self, filepath: str):
        self.archive = MCTSArchive.load(filepath)
