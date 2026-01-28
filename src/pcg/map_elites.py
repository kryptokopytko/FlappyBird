import json
import numpy as np
from typing import Dict, Tuple, Optional, List

from pcg.level_genome import LevelGenome
from utils.config import PCG_CONFIG


class MAPElitesArchive:
    """
    Stores elite solutions in a 2D grid based on behavior characteristics:
    - Dimension 1: Gap Tightness (0=large gaps, 1=small gaps)
    - Dimension 2: Item Richness (0=sparse items, 1=rich items)
    """

    def __init__(self, dims: Optional[Tuple[int, int]] = None):
        """
        Args:
            dims: (rows, cols) dimensions of the behavior grid. If None, uses config.
        """
        if dims is None:
            dims = PCG_CONFIG["map_elites"]["archive_dims"]
        self.dims = dims
        self.archive = np.empty(dims, dtype=object)  # Stores (genome, quality) tuples
        self.num_elites = 0

    def get_cell_index(self, behavior: Tuple[float, float]) -> Tuple[int, int]:
        """
        Convert continuous behavior features to discrete grid cell.

        Args:
            behavior: (gap_tightness, item_richness) in [0, 1] range

        Returns:
            (row, col) grid indices
        """
        gap_tightness, item_richness = behavior

        row = min(self.dims[0] - 1, int(gap_tightness * self.dims[0]))
        col = min(self.dims[1] - 1, int(item_richness * self.dims[1]))

        return (row, col)

    def add(
        self, genome: LevelGenome, quality: float, behavior: Tuple[float, float]
    ) -> bool:
        """
        Try to add a genome to the archive.

        Args:
            genome: LevelGenome to add
            quality: Quality score of the genome
            behavior: (gap_tightness, item_richness) behavior features

        Returns:
            True if genome was added (new cell or better quality), False otherwise
        """
        cell = self.get_cell_index(behavior)
        row, col = cell

        current = self.archive[row, col]

        # If cell is empty or new genome has better quality, add it
        if current is None or quality > current[1]:
            self.archive[row, col] = (genome, quality)
            if current is None:
                self.num_elites += 1
            return True

        return False

    def get_random_elite(self) -> Optional[LevelGenome]:
        """
        Get a random elite genome from the archive.

        Returns:
            Random LevelGenome, or None if archive is empty
        """
        if self.num_elites == 0:
            return None

        # Get all non-empty cells
        non_empty = []
        for i in range(self.dims[0]):
            for j in range(self.dims[1]):
                if self.archive[i, j] is not None:
                    non_empty.append((i, j))

        # Select random cell
        if non_empty:
            idx = np.random.randint(len(non_empty))
            row, col = non_empty[idx]
            genome, _ = self.archive[row, col]
            return genome

        return None

    def get_all_elites(self) -> List[Tuple[LevelGenome, float, Tuple[int, int]]]:
        """
        Get all elite genomes with their quality and cell position.

        Returns:
            List of (genome, quality, (row, col)) tuples
        """
        elites = []
        for i in range(self.dims[0]):
            for j in range(self.dims[1]):
                if self.archive[i, j] is not None:
                    genome, quality = self.archive[i, j]
                    elites.append((genome, quality, (i, j)))
        return elites

    def get_coverage(self) -> float:
        """
        Get archive coverage (percentage of filled cells).

        Returns:
            Coverage in [0, 1]
        """
        total_cells = self.dims[0] * self.dims[1]
        return self.num_elites / total_cells

    def get_statistics(self) -> Dict:
        """
        Returns:
            Dict with coverage, num_elites, avg_quality, max_quality
        """
        elites = self.get_all_elites()

        if not elites:
            return {
                "coverage": 0.0,
                "num_elites": 0,
                "avg_quality": 0.0,
                "max_quality": 0.0,
                "min_quality": 0.0,
            }

        qualities = [q for _, q, _ in elites]

        return {
            "coverage": self.get_coverage(),
            "num_elites": self.num_elites,
            "avg_quality": np.mean(qualities),
            "max_quality": np.max(qualities),
            "min_quality": np.min(qualities),
        }

    def get_heatmap(self) -> np.ndarray:
        """
        Get a heatmap of quality values in the archive.

        Returns:
            2D numpy array with quality values (NaN for empty cells)
        """
        heatmap = np.full(self.dims, np.nan)

        for i in range(self.dims[0]):
            for j in range(self.dims[1]):
                if self.archive[i, j] is not None:
                    _, quality = self.archive[i, j]
                    heatmap[i, j] = quality

        return heatmap

    def save(self, filepath: str):
        data = {"dims": self.dims, "elites": []}

        for i in range(self.dims[0]):
            for j in range(self.dims[1]):
                if self.archive[i, j] is not None:
                    genome, quality = self.archive[i, j]
                    data["elites"].append(
                        {"cell": (i, j), "genome": genome.to_dict(), "quality": quality}
                    )

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "MAPElitesArchive":
        with open(filepath, "r") as f:
            data = json.load(f)

        archive = cls(dims=tuple(data["dims"]))

        for elite in data["elites"]:
            i, j = elite["cell"]
            genome = LevelGenome.from_dict(elite["genome"])
            quality = elite["quality"]
            archive.archive[i, j] = (genome, quality)
            archive.num_elites += 1

        return archive
