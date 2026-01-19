"""Level genome representation for procedural content generation."""
import random
from utils.config import PCG_CONFIG


class LevelGenome:
    """
    Represents a level's parameters as a genome for evolution.

    11-dimensional parameter space:
    - Pipe parameters (4): spacing, gap_size, max_height_change, gap_variance
    - Item spawn rates (3): coin, powerup, debuff
    - Item placement (4): coin_offset_min/max, item_spacing, gold_probability
    """

    PARAM_NAMES = [
        'pipe_spacing', 'gap_size', 'max_height_change', 'gap_center_variance',
        'coin_spawn_rate', 'powerup_spawn_rate', 'debuff_spawn_rate',
        'coin_offset_min', 'coin_offset_max', 'item_spacing', 'gold_coin_probability'
    ]

    def __init__(self, params=None):
        """
        Initialize genome.

        Args:
            params: Optional dict of parameter values. If None, creates random genome.
        """
        bounds = PCG_CONFIG['genome_bounds']

        if params is None:
            # Generate random genome within bounds
            self.params = {
                name: random.uniform(bounds[name][0], bounds[name][1])
                for name in self.PARAM_NAMES
            }
        else:
            # Use provided params (clipped to bounds)
            self.params = {
                name: self._clip(params.get(name, 0), bounds[name])
                for name in self.PARAM_NAMES
            }

    @staticmethod
    def _clip(value, bounds):
        """Clip value to be within bounds."""
        return max(bounds[0], min(bounds[1], value))

    def to_vector(self):
        """Convert genome to parameter vector (for distance calculations)."""
        return [self.params[name] for name in self.PARAM_NAMES]

    @classmethod
    def from_vector(cls, vector):
        """Create genome from parameter vector."""
        params = {name: value for name, value in zip(cls.PARAM_NAMES, vector)}
        return cls(params)

    def copy(self):
        """Create a deep copy of this genome."""
        return LevelGenome(self.params.copy())

    def get(self, param_name):
        """Get a parameter value by name."""
        return self.params.get(param_name)

    def __repr__(self):
        """String representation for debugging."""
        return f"LevelGenome({self.params})"

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return self.params.copy()

    @classmethod
    def from_dict(cls, data):
        """Create genome from dictionary."""
        return cls(data)

    def mutate(self, mutation_rate=0.15, mutation_sigma=0.1):
        """
        Mutate genome parameters with Gaussian noise.

        Args:
            mutation_rate: Probability of mutating each parameter
            mutation_sigma: Standard deviation of Gaussian noise (as fraction of param range)

        Returns:
            New mutated LevelGenome instance
        """
        bounds = PCG_CONFIG['genome_bounds']
        mutated_params = {}

        for name in self.PARAM_NAMES:
            if random.random() < mutation_rate:
                # Apply Gaussian mutation
                param_range = bounds[name][1] - bounds[name][0]
                noise = random.gauss(0, mutation_sigma * param_range)
                mutated_value = self.params[name] + noise
                # Clip to bounds
                mutated_params[name] = self._clip(mutated_value, bounds[name])
            else:
                # Keep original value
                mutated_params[name] = self.params[name]

        return LevelGenome(mutated_params)
