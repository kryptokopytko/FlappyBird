import json
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

from pcg.level_genome import LevelGenome


@dataclass
class NoveltyIndividual:
    genome: LevelGenome
    behavior: Tuple[float, ...]
    novelty_score: float
    age: int
    quality: float = 0.0


def euclidean_distance(b1: Tuple[float, ...], b2: Tuple[float, ...]) -> float:
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(b1, b2)))


class NoveltyArchive:
    def __init__(self, max_size: int = 1000, config: Optional[Dict[str, Any]] = None):
        self.max_size = max_size
        self.individuals: List[NoveltyIndividual] = []
        self.config = config or {}

    def compute_novelty(self, behavior: Tuple[float, ...], k: int = 15) -> float:
        if len(self.individuals) < k:
            return float('inf')

        distances = [euclidean_distance(behavior, ind.behavior) for ind in self.individuals]
        k_nearest = sorted(distances)[:k]
        return sum(k_nearest) / k

    def add(self, genome: LevelGenome, behavior: Tuple[float, ...],
            novelty_score: float, age: int, quality: float = 0.0) -> bool:
        if len(self.individuals) < self.max_size:
            self.individuals.append(NoveltyIndividual(genome, behavior, novelty_score, age, quality))
            return True

        min_novelty_individual = min(self.individuals, key=lambda x: x.novelty_score)
        if novelty_score > min_novelty_individual.novelty_score:
            self.individuals.remove(min_novelty_individual)
            self.individuals.append(NoveltyIndividual(genome, behavior, novelty_score, age, quality))
            return True

        return False

    def get_random_individual(self) -> Optional[NoveltyIndividual]:
        if not self.individuals:
            return None
        return self.individuals[np.random.randint(len(self.individuals))]

    def get_all_individuals(self) -> List[NoveltyIndividual]:
        return self.individuals.copy()

    def get_statistics(self) -> Dict[str, Any]:
        if not self.individuals:
            return {
                "size": 0,
                "avg_novelty": 0.0,
                "max_novelty": 0.0,
                "min_novelty": 0.0,
                "avg_quality": 0.0
            }

        novelties = [ind.novelty_score for ind in self.individuals]
        qualities = [ind.quality for ind in self.individuals]

        return {
            "size": len(self.individuals),
            "avg_novelty": np.mean(novelties),
            "max_novelty": np.max(novelties),
            "min_novelty": np.min(novelties),
            "avg_quality": np.mean(qualities),
            "max_quality": np.max(qualities)
        }

    def save(self, filepath: str):
        data = {
            "algorithm": "novelty_search",
            "config": self.config,
            "individuals": []
        }

        for ind in self.individuals:
            data["individuals"].append({
                "genome": ind.genome.to_dict(),
                "behavior": list(ind.behavior),
                "novelty_score": ind.novelty_score,
                "age": ind.age,
                "quality": ind.quality
            })

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "NoveltyArchive":
        with open(filepath, "r") as f:
            data = json.load(f)

        archive = cls(config=data.get("config", {}))

        for ind_data in data["individuals"]:
            genome = LevelGenome.from_dict(ind_data["genome"])
            behavior = tuple(ind_data["behavior"])
            novelty_score = ind_data["novelty_score"]
            age = ind_data["age"]
            quality = ind_data.get("quality", 0.0)

            archive.individuals.append(
                NoveltyIndividual(genome, behavior, novelty_score, age, quality)
            )

        return archive
