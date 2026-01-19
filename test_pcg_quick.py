#!/usr/bin/env python3
"""Quick test of PCG system without running full MAP-Elites."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pcg.level_genome import LevelGenome
from pcg.map_elites import MAPElitesArchive
from pcg.evaluator import LevelEvaluator


def test_genome_creation():
    """Test creating and mutating genomes."""
    print("="*80)
    print("Test 1: Genome Creation and Mutation")
    print("="*80)

    # Create random genome
    genome1 = LevelGenome()
    print("\nRandom genome created:")
    print(f"  Pipe spacing: {genome1.get('pipe_spacing'):.1f}")
    print(f"  Gap size: {genome1.get('gap_size'):.1f}")
    print(f"  Coin spawn rate: {genome1.get('coin_spawn_rate'):.2f}")

    # Mutate genome
    genome2 = genome1.mutate(mutation_rate=0.5, mutation_sigma=0.2)
    print("\nMutated genome (50% mutation rate):")
    print(f"  Pipe spacing: {genome2.get('pipe_spacing'):.1f} "
          f"(diff: {genome2.get('pipe_spacing') - genome1.get('pipe_spacing'):+.1f})")
    print(f"  Gap size: {genome2.get('gap_size'):.1f} "
          f"(diff: {genome2.get('gap_size') - genome1.get('gap_size'):+.1f})")
    print(f"  Coin spawn rate: {genome2.get('coin_spawn_rate'):.2f} "
          f"(diff: {genome2.get('coin_spawn_rate') - genome1.get('coin_spawn_rate'):+.2f})")

    print("\n✓ Genome creation and mutation works!")


def test_archive():
    """Test MAP-Elites archive."""
    print("\n" + "="*80)
    print("Test 2: MAP-Elites Archive")
    print("="*80)

    archive = MAPElitesArchive(dims=(5, 5))
    print(f"\nCreated archive with dimensions: {archive.dims}")

    # Add some test genomes
    for i in range(10):
        genome = LevelGenome()
        quality = 0.5 + i * 0.05  # Increasing quality
        behavior = (i / 10.0, (10 - i) / 10.0)  # Different behaviors

        added = archive.add(genome, quality, behavior)
        if added:
            cell = archive.get_cell_index(behavior)
            print(f"  Added genome {i+1}: quality={quality:.2f}, "
                  f"behavior=({behavior[0]:.2f}, {behavior[1]:.2f}), cell={cell}")

    stats = archive.get_statistics()
    print(f"\nArchive statistics:")
    print(f"  Coverage: {stats['coverage']:.1%}")
    print(f"  Num elites: {stats['num_elites']}")
    print(f"  Avg quality: {stats['avg_quality']:.3f}")
    print(f"  Max quality: {stats['max_quality']:.3f}")

    print("\n✓ Archive operations work!")


def test_evaluator():
    """Test level evaluator with mock data."""
    print("\n" + "="*80)
    print("Test 3: Level Evaluator")
    print("="*80)

    evaluator = LevelEvaluator()

    # Create mock test results
    test_results = {
        'aggressive': [
            {'score': 100, 'distance': 500, 'coins': 10, 'survived': True, 'death_reason': 'survived'},
            {'score': 80, 'distance': 400, 'coins': 8, 'survived': False, 'death_reason': 'collision'},
            {'score': 120, 'distance': 600, 'coins': 12, 'survived': True, 'death_reason': 'survived'},
        ],
        'reactive': [
            {'score': 90, 'distance': 450, 'coins': 9, 'survived': True, 'death_reason': 'survived'},
            {'score': 70, 'distance': 350, 'coins': 7, 'survived': False, 'death_reason': 'collision'},
            {'score': 110, 'distance': 550, 'coins': 11, 'survived': True, 'death_reason': 'survived'},
        ],
        'coin_collector': [
            {'score': 150, 'distance': 500, 'coins': 20, 'survived': True, 'death_reason': 'survived'},
            {'score': 130, 'distance': 450, 'coins': 18, 'survived': False, 'death_reason': 'collision'},
            {'score': 140, 'distance': 480, 'coins': 19, 'survived': True, 'death_reason': 'survived'},
        ],
    }

    print("\nEvaluating mock test results...")
    quality, metrics = evaluator.evaluate_level(test_results)

    print(f"\nQuality score: {quality:.3f}")
    print(f"Metrics:")
    print(f"  Playability: {metrics['playability']:.3f}")
    print(f"  Balance: {metrics['balance']:.3f}")
    print(f"  Progression: {metrics['progression']:.3f}")
    print(f"  Control: {metrics['control']:.3f}")

    # Test behavior features
    difficulty, accessibility = evaluator.compute_behavior_features(test_results)
    print(f"\nBehavior features:")
    print(f"  Difficulty: {difficulty:.3f}")
    print(f"  Accessibility: {accessibility:.3f}")

    print("\n✓ Evaluator works!")


def test_level_generator():
    """Test creating level generator from genome."""
    print("\n" + "="*80)
    print("Test 4: Level Generator from Genome")
    print("="*80)

    from level_generator import LevelGenerator

    # Create genome with specific parameters
    genome = LevelGenome()
    print(f"\nGenome parameters:")
    print(f"  Pipe spacing: {genome.get('pipe_spacing'):.1f}")
    print(f"  Gap size: {genome.get('gap_size'):.1f}")

    # Create level generator from genome
    generator = LevelGenerator.from_genome(genome)
    print(f"\nLevel generator created:")
    print(f"  Pipe spacing: {generator.pipe_spacing}")
    print(f"  Gap size: {generator.gap_size}")
    print(f"  Coin spawn rate: {generator.coin_spawn_rate:.2f}")

    print("\n✓ Level generator from genome works!")


def main():
    """Run all quick tests."""
    print("\n" + "="*80)
    print("PCG System Quick Test Suite")
    print("="*80)

    try:
        test_genome_creation()
        test_archive()
        test_evaluator()
        test_level_generator()

        print("\n" + "="*80)
        print("✓ All tests passed!")
        print("="*80)
        print("\nPCG system is ready to use!")
        print("Run full MAP-Elites with: python src/pcg/run_map_elites.py")
        print("\n")

    except Exception as e:
        print(f"\n✗ Test failed with error:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
