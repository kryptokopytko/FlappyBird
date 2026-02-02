#!/usr/bin/env python3
"""Test top 3 levels with all bots and show detailed performance - VISUAL MODE."""

import json
import os
import sys
import time
import pygame

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.level_genome import LevelGenome
from rendering.game_graphical import Game
from tests.concrete_level_generator import ConcreteLevelGenerator


def load_top_levels(n=3):
    """Load top N levels from saved files."""
    level_dir = "data/map_elites/pcg_levels"

    # Find all level files
    level_files = []
    for filename in os.listdir(level_dir):
        if filename.startswith("level_top") and filename.endswith(".json"):
            # Extract quality from filename
            quality_str = filename.split("_q")[1].replace(".json", "")
            quality = float(quality_str)
            level_files.append((quality, os.path.join(level_dir, filename)))

    # Sort by quality descending
    level_files.sort(reverse=True, key=lambda x: x[0])

    # Load top N
    levels = []
    for i, (quality, filepath) in enumerate(level_files[:n]):
        with open(filepath, 'r') as f:
            data = json.load(f)
            genome = LevelGenome.from_dict(data["genome"])
            levels.append({
                "rank": i + 1,
                "quality": quality,
                "genome": genome,
                "cell": data.get("cell", [0, 0]),
                "filepath": filepath
            })

    return levels


def run_visual_test(genome, bot_type, level_info):
    """Run a single bot on a level visually."""
    print(f"\n  Starting {bot_type.upper()}...")

    # Create game in visual mode
    game = Game(headless=False)
    game.level_generator = ConcreteLevelGenerator.from_genome(genome)
    game.bot_type = bot_type
    game.start_game(bot_mode=True)

    # Get level length for display
    level_length = genome.level.length

    # Run game loop
    test_duration = 30.0
    sim_time = 0
    dt = 1.0 / 60.0

    while game.running and game.state == "playing":
        # Handle pygame events (including window close)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False
                elif event.key == pygame.K_SPACE:
                    # Skip to next bot
                    game.state = "game_over"

        # Update game
        game.update(dt)

        # Render
        game.render()
        if game.clock:
            game.clock.tick(60)  # 60 FPS

        sim_time += dt
        if sim_time >= test_duration:
            break

    # Get results
    survived = game.state in ["playing", "victory"]
    result = {
        "bot": bot_type,
        "survived": survived,
        "distance": game.scroll_offset,
        "score": game.score,
        "coins": game.coins,
        "time": sim_time
    }

    # Show result on screen for a moment
    if game.renderer and game.running:
        time.sleep(1)

    return result


def test_level_with_bots(genome, level_info):
    """Test a level with all available bots - VISUAL MODE."""
    print(f"\n{'='*80}")
    print(f"Level #{level_info['rank']} | Quality: {level_info['quality']:.3f} | Cell: {level_info['cell']}")
    print(f"{'='*80}")

    # Level statistics
    level = genome.level
    print(f"\n📊 Level Statistics:")
    print(f"  • Total pipes: {len(level.pipes)}")
    print(f"  • Total items: {len(level.items)} ({len([i for i in level.items if i.type == 'coin'])} coins)")
    print(f"  • Length: {level.length:.1f} units")

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

    # Test with all bots
    print(f"\n🤖 Bot Performance (Visual Mode):")
    print(f"  Press SPACE to skip to next bot, ESC to quit")

    # bot_types = ["coin_collector"]
    bot_types = ["aggressive", "reactive", "coin_collector", "flat"]
    bot_stats = []

    for bot_type in bot_types:
        result = run_visual_test(genome, bot_type, level_info)

        if result is None:
            # User quit
            print("\n  User quit testing.")
            return bot_stats

        bot_stats.append(result)

        # Display result
        survived = "✓" if result["survived"] else "✗"
        distance_pct = (result["distance"] / level.length) * 100

        print(f"\n  {bot_type.upper():15} | {survived}")
        print(f"    Score: {result['score']:6.0f} | Distance: {result['distance']:6.1f} ({distance_pct:5.1f}%)")
        print(f"    Coins: {result['coins']:3} | Time: {result['time']:5.2f}s")

    # Summary
    if bot_stats:
        survival_count = sum(1 for s in bot_stats if s["survived"])
        avg_distance = sum(s["distance"] for s in bot_stats) / len(bot_stats)
        avg_distance_pct = (avg_distance / level.length) * 100

        print(f"\n  📈 Summary:")
        print(f"    Survival rate: {survival_count}/{len(bot_stats)} bots ({survival_count/len(bot_stats)*100:.0f}%)")
        print(f"    Avg distance: {avg_distance:.1f} units ({avg_distance_pct:.1f}%)")

    return bot_stats


def main():
    print("="*80)
    print("Testing Top 3 Levels with All Bots - VISUAL MODE")
    print("="*80)
    print("\nControls:")
    print("  SPACE - Skip to next bot")
    print("  ESC   - Quit testing")

    # Initialize pygame
    pygame.init()

    try:
        # Load top 3 levels
        print("\nLoading top 3 levels...")
        levels = load_top_levels(n=3)

        print(f"Found {len(levels)} levels to test\n")

        # Test each level
        all_results = []
        for level_info in levels:
            print(f"\n{'='*80}")
            print(f"Press any key to start testing Level #{level_info['rank']}...")
            print(f"{'='*80}")

            # Wait for user to be ready
            input("Press ENTER to continue...")

            stats = test_level_with_bots(level_info["genome"], level_info)

            if not stats:
                # User quit
                break

            all_results.append({
                "level": level_info,
                "stats": stats
            })

        # Overall summary
        if all_results:
            print(f"\n{'='*80}")
            print("Overall Summary")
            print(f"{'='*80}")

            for i, result in enumerate(all_results):
                level = result["level"]
                stats = result["stats"]
                if stats:
                    survival = sum(1 for s in stats if s["survived"])
                    avg_dist = sum(s["distance"] for s in stats) / len(stats)

                    print(f"\nLevel {i+1} (Q={level['quality']:.3f}): {survival}/{len(stats)} survived, avg dist={avg_dist:.1f}")

            print(f"\n{'='*80}")

    finally:
        # Cleanup
        pygame.quit()
        print("\nTesting complete!")


if __name__ == "__main__":
    main()
