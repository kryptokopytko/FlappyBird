#!/usr/bin/env python3

import json
import os
import sys
import time
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pcg.level_genome import LevelGenome
from pcg.novelty_archive import NoveltyArchive
from game_graphical import Game
from concrete_level_generator import ConcreteLevelGenerator


def load_novelty_levels(archive_path, top_n=3):
    archive = NoveltyArchive.load(archive_path)

    individuals = archive.get_all_individuals()
    individuals.sort(key=lambda x: x.quality, reverse=True)

    levels = []
    for i, ind in enumerate(individuals[:top_n]):
        levels.append({
            "rank": i + 1,
            "quality": ind.quality,
            "novelty": ind.novelty_score,
            "genome": ind.genome,
            "behavior": ind.behavior,
            "age": ind.age
        })

    return levels, archive.config


def run_visual_test(genome, bot_type, level_info):
    print(f"\n  Starting {bot_type.upper()}...")

    game = Game(headless=False)
    game.level_generator = ConcreteLevelGenerator.from_genome(genome)
    game.bot_type = bot_type
    game.start_game(bot_mode=True)

    test_duration = 30.0
    sim_time = 0
    dt = 1.0 / 60.0

    while game.running and game.state == "playing":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False
                elif event.key == pygame.K_SPACE:
                    game.state = "game_over"

        game.update(dt)
        game.render()
        if game.clock:
            game.clock.tick(60)

        sim_time += dt
        if sim_time >= test_duration:
            break

    survived = game.state in ["playing", "victory"]
    result = {
        "bot": bot_type,
        "survived": survived,
        "distance": game.scroll_offset,
        "score": game.score,
        "coins": game.coins,
        "time": sim_time
    }

    if game.renderer and game.running:
        time.sleep(1)

    return result


def test_level(genome, level_info):
    print(f"\n{'='*80}")
    print(f"Novelty Level #{level_info['rank']} | Quality: {level_info['quality']:.3f} | "
          f"Novelty: {level_info['novelty']:.3f}")
    print(f"{'='*80}")

    level = genome.level
    print(f"\n📊 Level Statistics:")
    print(f"  • Total pipes: {len(level.pipes)}")
    print(f"  • Total items: {len(level.items)} ({len([i for i in level.items if i.type == 'coin'])} coins)")
    print(f"  • Length: {level.length:.1f} units")
    print(f"  • Behavior: gap_tightness={level_info['behavior'][0]:.2f}, "
          f"spacing_density={level_info['behavior'][1]:.2f}")
    print(f"  • Age: {level_info['age']} iterations")

    if level.pipes:
        avg_gap = sum(p.gap_size for p in level.pipes) / len(level.pipes)
        gaps = [p.gap_size for p in level.pipes]
        min_gap = min(gaps)
        max_gap = max(gaps)

        gap_centers = [p.gap_center for p in level.pipes]
        min_height = min(gap_centers)
        max_height = max(gap_centers)

        spacings = [level.pipes[i+1].x - level.pipes[i].x for i in range(len(level.pipes)-1)]
        avg_spacing = sum(spacings) / len(spacings) if spacings else 0

        print(f"  • Gap sizes: avg={avg_gap:.1f}, min={min_gap:.1f}, max={max_gap:.1f}")
        print(f"  • Gap heights: min={min_height:.1f}, max={max_height:.1f}")
        print(f"  • Pipe spacing: avg={avg_spacing:.1f}")

    print(f"\n🤖 Bot Performance (COIN_COLLECTOR - best bot):")
    print(f"  Press SPACE to skip, ESC to quit")

    result = run_visual_test(genome, "coin_collector", level_info)

    if result is None:
        print("\n  User quit testing.")
        return None

    survived = "✓" if result["survived"] else "✗"
    distance_pct = (result["distance"] / level.length) * 100

    print(f"\n  COIN_COLLECTOR  | {survived}")
    print(f"    Score: {result['score']:6.0f} | Distance: {result['distance']:6.1f} ({distance_pct:5.1f}%)")
    print(f"    Coins: {result['coins']:3} | Time: {result['time']:5.2f}s")

    return result


def main():
    archive_path = "data/test_novelty.json"

    if not os.path.exists(archive_path):
        print(f"Error: Archive not found at {archive_path}")
        print("Run: PYTHONPATH=src python3 src/pcg/run_novelty_search.py first")
        sys.exit(1)

    print("="*80)
    print("Testing Top 3 Novelty Search Levels - VISUAL MODE")
    print("="*80)
    print("\nControls:")
    print("  SPACE - Skip to next level")
    print("  ESC   - Quit testing")

    pygame.init()

    try:
        print(f"\nLoading Novelty archive from {archive_path}...")
        levels, config = load_novelty_levels(archive_path, top_n=3)

        print(f"\nNovelty Search Configuration:")
        print(f"  Iterations: {config.get('num_iterations', 'N/A')}")
        print(f"  k-neighbors: {config.get('k_neighbors', 'N/A')}")
        print(f"  Max archive size: {config.get('max_archive_size', 'N/A')}")

        print(f"\nFound {len(levels)} levels to test (sorted by quality)\n")

        for level_info in levels:
            print(f"\n{'='*80}")
            print(f"Testing Level #{level_info['rank']}...")
            print(f"{'='*80}")

            result = test_level(level_info["genome"], level_info)

            if not result:
                break

    finally:
        pygame.quit()
        print("\nTesting complete!")


if __name__ == "__main__":
    main()
