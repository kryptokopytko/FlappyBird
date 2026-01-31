#!/usr/bin/env python3
"""Test the new concrete level system."""

import sys
sys.path.insert(0, "src")

from pcg.level_genome import LevelGenome
from pcg.level_tester import LevelTester


def test_concrete_level_creation():
    """Test creating a concrete level genome."""
    print("Creating random concrete level genome...")
    genome = LevelGenome()

    print(f"  {genome}")
    print(f"  Pipes: {len(genome.level.pipes)}")
    print(f"  Items: {len(genome.level.items)}")
    print(f"  Length: {genome.level.length}")

    # Check first few pipes
    print("\nFirst 3 pipes:")
    for i, pipe in enumerate(genome.level.pipes[:3]):
        print(f"  Pipe {i+1}: x={pipe.x:.1f}, gap_center={pipe.gap_center:.1f}, gap_size={pipe.gap_size:.1f}")

    # Check features
    features = genome.level.compute_features()
    print(f"\nBehavioral features:")
    print(f"  gap_tightness: {features['gap_tightness']:.3f}")
    print(f"  item_richness: {features['item_richness']:.3f}")

    return genome


def test_mutation(genome):
    """Test mutating a genome."""
    print("\nMutating genome...")
    mutated = genome.mutate(mutation_rate=0.5, mutation_sigma=0.2)

    print(f"  Original: {genome}")
    print(f"  Mutated:  {mutated}")

    # Compare first pipe
    if genome.level.pipes and mutated.level.pipes:
        orig_pipe = genome.level.pipes[0]
        mut_pipe = mutated.level.pipes[0]
        print(f"\nFirst pipe comparison:")
        print(f"  Original: x={orig_pipe.x:.1f}, gap_center={orig_pipe.gap_center:.1f}, gap_size={orig_pipe.gap_size:.1f}")
        print(f"  Mutated:  x={mut_pipe.x:.1f}, gap_center={mut_pipe.gap_center:.1f}, gap_size={mut_pipe.gap_size:.1f}")

    return mutated


def test_level_testing(genome):
    """Test running level test."""
    print("\nTesting level with bots...")
    tester = LevelTester()
    results = tester.test_genome(genome)

    for bot_name, runs in results.items():
        for run in runs:
            print(f"  {bot_name}: distance={run['distance']:.1f}, score={run['score']}, survived={run['survived']}")

    return results


def test_serialization(genome):
    """Test saving and loading."""
    print("\nTesting serialization...")

    # Save
    data = genome.to_dict()
    print(f"  Serialized keys: {list(data.keys())}")
    print(f"  Pipes in dict: {len(data['pipes'])}")
    print(f"  Items in dict: {len(data['items'])}")

    # Load
    loaded = LevelGenome.from_dict(data)
    print(f"  Loaded: {loaded}")
    print(f"  Pipes match: {len(loaded.level.pipes) == len(genome.level.pipes)}")
    print(f"  Items match: {len(loaded.level.items) == len(genome.level.items)}")

    return loaded


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Concrete Level System")
    print("=" * 60)

    genome1 = test_concrete_level_creation()
    genome2 = test_mutation(genome1)
    results = test_level_testing(genome1)
    loaded = test_serialization(genome1)

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
