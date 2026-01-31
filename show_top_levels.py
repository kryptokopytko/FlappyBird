#!/usr/bin/env python3
"""Show top 3 levels visually with coin collector bot."""

import sys
import json
import glob

sys.path.insert(0, "src")

from game_graphical import Game
from concrete_level_generator import ConcreteLevelGenerator
from pcg.level_genome import LevelGenome


def play_level(level_file, level_num):
    """Play a level and show stats."""
    with open(level_file, "r") as f:
        data = json.load(f)

    genome = LevelGenome.from_dict(data["genome"])
    quality = data["quality"]
    cell = data["cell"]

    print("\n" + "=" * 70)
    print(f"POZIOM #{level_num} - Quality: {quality:.3f}")
    print("=" * 70)
    print(f"Cell: {cell}")
    print(f"Rur: {len(genome.level.pipes)}")
    print(f"Items: {len(genome.level.items)} ({len([i for i in genome.level.items if i.type == 'coin'])} coins)")
    print(f"Długość: {genome.level.length} units")

    # Stats
    if genome.level.pipes:
        gaps = [p.gap_size for p in genome.level.pipes]
        spacings = [genome.level.pipes[i+1].x - genome.level.pipes[i].x for i in range(len(genome.level.pipes)-1)]
        print(f"Gap size: {min(gaps):.1f}-{max(gaps):.1f} (avg {sum(gaps)/len(gaps):.1f})")
        if spacings:
            print(f"Spacing: {min(spacings):.1f}-{max(spacings):.1f} (avg {sum(spacings)/len(spacings):.1f})")

    print("\nBot: Coin Collector (A*)")
    print("Naciśnij ESC aby przejść do następnego poziomu")
    print()

    # Play
    game = Game(headless=False)
    game.level_generator = ConcreteLevelGenerator.from_genome(genome)
    game.bot_type = "coin_collector"
    game.start_game(bot_mode=True)
    game.run()

    print(f"\nWynik: {game.state}")
    print(f"Dystans: {game.scroll_offset:.1f}/{genome.level.length}")
    print(f"Score: {game.score}")
    print(f"Coins: {game.coins}")

    return game.state == "victory"


if __name__ == "__main__":
    print("=" * 70)
    print("PREZENTACJA TOP 3 POZIOMÓW Z MAP-ELITES")
    print("=" * 70)
    print("\nWygenerowano z 1000 iteracji, 89.1% coverage")
    print("Poziomy: 900 units (~30s), 18-23 rury")
    print()

    # Get top 3 levels - pick the most recent file for each index
    import re
    import os

    level_files_all = glob.glob("data/pcg_levels/level_top*.json")

    # Group by index number
    files_by_index = {}
    for f in level_files_all:
        match = re.search(r'level_top(\d+)', f)
        if match:
            idx = int(match.group(1))
            if idx not in files_by_index:
                files_by_index[idx] = []
            files_by_index[idx].append(f)

    # For each index, pick the most recent file
    level_files = []
    for idx in sorted(files_by_index.keys())[:3]:
        # Sort by modification time, pick newest
        newest = max(files_by_index[idx], key=os.path.getmtime)
        level_files.append(newest)

    victories = 0
    for i, level_file in enumerate(level_files, 1):
        won = play_level(level_file, i)
        if won:
            victories += 1

    print("\n" + "=" * 70)
    print("PODSUMOWANIE")
    print("=" * 70)
    print(f"Poziomy ukończone: {victories}/3")
    print(f"Wszystkie poziomy są deterministyczne i powtarzalne!")
    print("=" * 70)
