#!/usr/bin/env python3
"""Play the best MAP-Elites level with aggressive bot."""

import sys
import json

sys.path.insert(0, "src")

from game_graphical import Game
from level_generator import LevelGenerator
from pcg.level_genome import LevelGenome


def play_level(level_file, bot_type="aggressive"):
    """Play a saved MAP-Elites level with visualization."""
    # Load the level
    with open(level_file, "r") as f:
        data = json.load(f)

    genome = LevelGenome.from_dict(data["genome"])
    quality = data["quality"]
    cell = data["cell"]

    print("=" * 60)
    print(f"Loading level: {level_file}")
    print(f"Quality: {quality:.3f}")
    print(f"Cell: {cell} (gap_tightness={cell[0]}, item_richness={cell[1]})")
    print("=" * 60)
    print("\nGenome parameters:")
    print(f"  Pipe spacing: {genome.get('pipe_spacing'):.1f}")
    print(f"  Gap size: {genome.get('gap_size'):.1f}")
    print(f"  Max height change: {genome.get('max_height_change'):.1f}")
    print(f"  Coin spawn rate: {genome.get('coin_spawn_rate'):.2f}")
    print(f"  Powerup spawn rate: {genome.get('powerup_spawn_rate'):.2f}")
    print(f"  Gold coin probability: {genome.get('gold_coin_probability'):.2f}")
    print("=" * 60)
    print(f"\nStarting game with {bot_type} bot...")
    print("Press ESC to quit\n")

    # Create game with custom level
    game = Game(headless=False)
    game.level_generator = LevelGenerator.from_genome(genome)
    game.bot_type = bot_type
    game.start_game(bot_mode=True)

    # Run game loop
    game.run()

    print("\n" + "=" * 60)
    print("Game ended!")
    print(f"Final score: {game.score}")
    print(f"Final distance: {game.scroll_offset:.1f}")
    print(f"Coins collected: {game.coins}")
    print("=" * 60)


if __name__ == "__main__":
    # Play the best level
    play_level("data/pcg_levels/level_top1_q0.822.json", bot_type="aggressive")
