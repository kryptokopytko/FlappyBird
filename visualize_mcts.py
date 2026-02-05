#!/usr/bin/env python3
"""Quick script to visualize all three PCG algorithms: MAP-Elites, MCTS-QD, and Novelty Search."""

import sys
sys.path.insert(0, '/home/kasia/FlappyBird/src')

from pcg.visualize_results import load_and_visualize

# Visualize all three PCG algorithms
load_and_visualize(
    map_elites_path='data/map_elites/archive.json',
    mcts_qd_path='mcts_levels/mcts_qd_archive.json',
    novelty_path='data/novelty_archive.json',
    save_path='pcg_comparison_full.png',
    show=False  # Don't show GUI, just save
)

print("✓ Full PCG comparison saved to: pcg_comparison_full.png")
print("  - MAP-Elites")
print("  - MCTS-QD")
print("  - Novelty Search")
