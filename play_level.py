#!/usr/bin/env python3
"""Play a specific level file with a bot."""

import sys
import json
import argparse

sys.path.insert(0, "src")

from game_graphical import Game
from concrete_level_generator import ConcreteLevelGenerator
from pcg.level_genome import LevelGenome


def play_level(level_file: str, bot_type: str = "coin_collector", headless: bool = False):
    with open(level_file, "r") as f:
        data = json.load(f)

    genome = LevelGenome.from_dict(data["genome"])
    quality = data.get("quality", 0.0)

    print(f"Loading level: {level_file}")
    print(f"Quality: {quality:.3f}")
    print(f"Pipes: {len(genome.level.pipes)}")
    print(f"Items: {len(genome.level.items)}")
    print(f"Length: {genome.level.length} units")
    print(f"Bot: {bot_type}")
    print()

    game = Game(headless=headless)
    game.level_generator = ConcreteLevelGenerator.from_genome(genome)
    game.bot_type = bot_type
    game.start_game(bot_mode=True)
    game.run()

    print(f"\nResult: {game.state}")
    print(f"Distance: {game.scroll_offset:.1f}/{genome.level.length}")
    print(f"Score: {game.score}")
    print(f"Coins: {game.coins}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play a specific level file")
    parser.add_argument("level_file", help="Path to level JSON file")
    parser.add_argument("--bot", default="coin_collector",
                       choices=["aggressive", "reactive", "coin_collector"],
                       help="Bot type to use (default: coin_collector)")
    parser.add_argument("--headless", action="store_true",
                       help="Run without graphics")

    args = parser.parse_args()
    play_level(args.level_file, args.bot, args.headless)
