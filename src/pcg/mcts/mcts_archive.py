import json
from typing import Optional, Tuple, Dict, Any

from pcg.map_elites.map_elites import MAPElitesArchive


class MCTSArchive(MAPElitesArchive):
    def __init__(self, dims: Optional[Tuple[int, int]] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(dims)
        self.config = config or {}

    def save(self, filepath: str):
        data = {
            "dims": self.dims,
            "algorithm": "mcts-qd",
            "config": self.config,
            "elites": []
        }

        for i in range(self.dims[0]):
            for j in range(self.dims[1]):
                if self.archive[i, j] is not None:
                    genome, quality = self.archive[i, j]
                    data["elites"].append({
                        "cell": (i, j),
                        "genome": genome.to_dict(),
                        "quality": quality
                    })

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "MCTSArchive":
        with open(filepath, "r") as f:
            data = json.load(f)

        from core.level_genome import LevelGenome

        archive = cls(dims=tuple(data["dims"]), config=data.get("config", {}))

        for elite in data["elites"]:
            i, j = elite["cell"]
            genome = LevelGenome.from_dict(elite["genome"])
            quality = elite["quality"]
            archive.archive[i, j] = (genome, quality)
            archive.num_elites += 1

        return archive
