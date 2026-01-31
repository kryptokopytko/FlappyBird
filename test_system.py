#!/usr/bin/env python3
"""Comprehensive tests for PCG system."""

import sys
sys.path.insert(0, "src")

from pcg.level_genome import LevelGenome
from pcg.concrete_level import ConcreteLevel, Pipe, Item
from game_graphical import Game
from concrete_level_generator import ConcreteLevelGenerator
from utils.config import PCG_CONFIG


def test_level_generation():
    """Test that level generation respects bounds."""
    print("=" * 70)
    print("TEST 1: Level Generation Bounds")
    print("=" * 70)

    failures = []
    bounds = PCG_CONFIG["genome_bounds"]

    for i in range(10):
        genome = LevelGenome()

        # Check gap sizes
        for pipe in genome.level.pipes:
            if pipe.gap_size < bounds["gap_size"][0] or pipe.gap_size > bounds["gap_size"][1]:
                failures.append(f"Gap size {pipe.gap_size:.2f} out of bounds {bounds['gap_size']}")

        # Check pipe spacing
        if len(genome.level.pipes) > 1:
            for j in range(len(genome.level.pipes) - 1):
                spacing = genome.level.pipes[j+1].x - genome.level.pipes[j].x
                if spacing < bounds["pipe_spacing"][0] * 0.8:  # Allow some variance
                    failures.append(f"Spacing {spacing:.1f} too small (min {bounds['pipe_spacing'][0]})")

    if failures:
        print(f"❌ FAILED: {len(failures)} issues")
        for f in failures[:5]:
            print(f"  - {f}")
    else:
        print("✅ PASS: All levels respect bounds")

    return len(failures) == 0


def test_coin_safety():
    """Test that coins are placed safely away from pipes."""
    print("\n" + "=" * 70)
    print("TEST 2: Coin Safety")
    print("=" * 70)

    unsafe_coins = 0
    total_coins = 0

    for i in range(10):
        genome = LevelGenome()

        for item in genome.level.items:
            if item.type == "coin":
                total_coins += 1
                # Find closest pipe
                min_dist = float('inf')
                for pipe in genome.level.pipes:
                    dist = abs(item.x - pipe.x)
                    if dist < min_dist:
                        min_dist = dist

                if min_dist < 10:
                    unsafe_coins += 1

    print(f"Total coins tested: {total_coins}")
    print(f"Unsafe coins (< 10 units from pipe): {unsafe_coins}")

    if unsafe_coins == 0:
        print("✅ PASS: All coins are safely placed")
        return True
    else:
        print(f"❌ FAILED: {unsafe_coins}/{total_coins} coins unsafe ({unsafe_coins/total_coins*100:.1f}%)")
        return False


def test_mutation_safety():
    """Test that mutations preserve coin safety."""
    print("\n" + "=" * 70)
    print("TEST 3: Mutation Safety")
    print("=" * 70)

    unsafe_after_mutation = 0
    total_mutations = 20

    for i in range(total_mutations):
        original = LevelGenome()
        mutated = original.mutate(mutation_rate=0.5, mutation_sigma=0.3)

        # Check if any coins are unsafe after mutation
        for item in mutated.level.items:
            if item.type == "coin":
                min_dist = min(abs(item.x - p.x) for p in mutated.level.pipes)
                if min_dist < 10:
                    unsafe_after_mutation += 1
                    break

    print(f"Levels with unsafe coins after mutation: {unsafe_after_mutation}/{total_mutations}")

    if unsafe_after_mutation == 0:
        print("✅ PASS: Mutations preserve coin safety")
        return True
    else:
        print(f"❌ FAILED: {unsafe_after_mutation} levels have unsafe coins after mutation")
        return False


def test_bot_performance():
    """Test bot performance on generated levels."""
    print("\n" + "=" * 70)
    print("TEST 4: Bot Performance")
    print("=" * 70)

    completions = []

    for i in range(5):
        genome = LevelGenome()

        game = Game(headless=True)
        game.level_generator = ConcreteLevelGenerator.from_genome(genome)
        game.bot_type = 'coin_collector'
        game.start_game(bot_mode=True)
        game.run()

        completion = game.scroll_offset / genome.level.length
        completions.append(completion)

    avg_completion = sum(completions) * 100 / len(completions)
    victories = sum(1 for c in completions if c >= 0.99)

    print(f"Avg completion: {avg_completion:.1f}%")
    print(f"Victories: {victories}/5")

    if avg_completion >= 50:
        print("✅ PASS: Bot completes at least 50% on average")
        return True
    else:
        print(f"❌ FAILED: Bot only completes {avg_completion:.1f}% on average")
        return False


def test_level_determinism():
    """Test that levels are deterministic (same result every time)."""
    print("\n" + "=" * 70)
    print("TEST 5: Level Determinism")
    print("=" * 70)

    # Generate one level
    genome = LevelGenome()

    # Test it 3 times with same bot
    distances = []
    scores = []

    for run in range(3):
        game = Game(headless=True)
        game.level_generator = ConcreteLevelGenerator.from_genome(genome)
        game.bot_type = 'coin_collector'
        game.start_game(bot_mode=True)
        game.run()

        distances.append(game.scroll_offset)
        scores.append(game.score)

    # Check if all runs are identical
    distance_variance = max(distances) - min(distances)
    score_variance = max(scores) - min(scores)

    print(f"Distances: {distances}")
    print(f"Scores: {scores}")
    print(f"Distance variance: {distance_variance:.2f}")
    print(f"Score variance: {score_variance}")

    if distance_variance < 0.01 and score_variance == 0:
        print("✅ PASS: Levels are 100% deterministic")
        return True
    else:
        print("❌ FAILED: Levels show variance between runs")
        return False


def test_level_structure():
    """Test that generated levels have reasonable structure."""
    print("\n" + "=" * 70)
    print("TEST 6: Level Structure")
    print("=" * 70)

    failures = []

    for i in range(10):
        genome = LevelGenome()

        # Check level has pipes
        if len(genome.level.pipes) < 5:
            failures.append(f"Level has only {len(genome.level.pipes)} pipes (too few)")

        # Check level has reasonable length
        if genome.level.length < 800 or genome.level.length > 1000:
            failures.append(f"Level length {genome.level.length} out of expected range")

        # Check pipes are sorted by x
        for j in range(len(genome.level.pipes) - 1):
            if genome.level.pipes[j].x >= genome.level.pipes[j+1].x:
                failures.append("Pipes not sorted by x position")
                break

    if failures:
        print(f"❌ FAILED: {len(failures)} issues")
        for f in failures[:5]:
            print(f"  - {f}")
        return False
    else:
        print("✅ PASS: All levels have valid structure")
        return True


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 70)
    print("RUNNING COMPREHENSIVE SYSTEM TESTS")
    print("=" * 70)
    print()

    tests = [
        ("Level Generation Bounds", test_level_generation),
        ("Coin Safety", test_coin_safety),
        ("Mutation Safety", test_mutation_safety),
        ("Bot Performance", test_bot_performance),
        ("Level Determinism", test_level_determinism),
        ("Level Structure", test_level_structure),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for name, p in results:
        status = "✅ PASS" if p else "❌ FAIL"
        print(f"{status}: {name}")

    print("=" * 70)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is working correctly.")
    elif passed >= total * 0.8:
        print(f"\n⚠️  Most tests passed, but {total-passed} tests failed.")
    else:
        print(f"\n❌ CRITICAL: Only {passed}/{total} tests passed!")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
