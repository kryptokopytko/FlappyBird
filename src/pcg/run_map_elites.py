#!/usr/bin/env python3
import argparse
import os
import sys
import time
import matplotlib.pyplot as plt
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pcg.map_elites_runner import MAPElitesRunner
from pcg.level_tester import FastLevelTester
from pcg.level_genome import LevelGenome
from utils.config import PCG_CONFIG


def plot_archive_heatmap(archive, filepath="archive_heatmap.png"):
    heatmap = archive.get_heatmap()

    plt.figure(figsize=(10, 8))
    plt.imshow(heatmap, cmap="viridis", origin="lower", aspect="auto")
    plt.colorbar(label="Quality Score")
    plt.xlabel("Item Richness (0=sparse, 1=rich)")
    plt.ylabel("Gap Tightness (0=loose, 1=tight)")
    plt.title("MAP-Elites Archive - Level Quality Heatmap")

    # Add grid
    dims = heatmap.shape
    plt.xticks(range(dims[1]))
    plt.yticks(range(dims[0]))
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    print(f"Heatmap saved to {filepath}")


def print_best_genomes(archive, n=5):
    elites = archive.get_all_elites()

    if not elites:
        print("No elites in archive!")
        return

    # Sort by quality
    elites_sorted = sorted(elites, key=lambda x: x[1], reverse=True)

    print(f"\n{'='*80}")
    print(f"Top {n} Level Genomes:")
    print(f"{'='*80}")

    for i, (genome, quality, cell) in enumerate(elites_sorted[:n], 1):
        difficulty_bin, accessibility_bin = cell
        dims = archive.dims

        # Convert cell to approximate behavior values
        gap_tightness = (difficulty_bin + 0.5) / dims[0]
        item_richness = (accessibility_bin + 0.5) / dims[1]

        print(
            f"\n{i}. Quality: {quality:.3f} | "
            f"Gap tightness: {gap_tightness:.2f} | Item richness: {item_richness:.2f}"
        )
        print(f"   Cell: ({difficulty_bin}, {accessibility_bin})")
        print(f"   Parameters:")

        params = genome.params
        print(
            f"     Pipes: spacing={params['pipe_spacing']:.1f}, "
            f"gap={params['gap_size']:.1f}, "
            f"height_change={params['max_height_change']:.1f}"
        )
        print(
            f"     Spawn rates: coins={params['coin_spawn_rate']:.2f}, "
            f"powerups={params['powerup_spawn_rate']:.2f}, "
            f"debuffs={params['debuff_spawn_rate']:.2f}"
        )


def save_best_genomes(archive, output_dir="data/pcg_levels", n=10):
    """Save best genomes to JSON files."""
    os.makedirs(output_dir, exist_ok=True)

    elites = archive.get_all_elites()
    elites_sorted = sorted(elites, key=lambda x: x[1], reverse=True)

    for i, (genome, quality, cell) in enumerate(elites_sorted[:n], 1):
        filepath = os.path.join(output_dir, f"level_top{i}_q{quality:.3f}.json")

        import json

        data = {"quality": quality, "cell": cell, "genome": genome.to_dict()}

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    print(f"\nSaved top {n} genomes to {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Run MAP-Elites level generation")
    parser.add_argument(
        "--iterations",
        "-n",
        type=int,
        default=None,
        help="Number of iterations (default: from config)",
    )
    parser.add_argument(
        "--initial-samples",
        "-i",
        type=int,
        default=None,
        help="Number of initial random samples (default: from config)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="data/map_elites_archive.json",
        help="Output archive file",
    )
    parser.add_argument(
        "--load",
        "-l",
        type=str,
        default=None,
        help="Load existing archive and continue evolution",
    )
    parser.add_argument(
        "--fast", "-f", action="store_true", help="Use fast testing mode (2x speed)"
    )
    parser.add_argument(
        "--ultra-fast",
        "-u",
        action="store_true",
        help="Use ultra-fast mode (10-15x speed, less accurate but good for PCG)",
    )
    parser.add_argument(
        "--plot",
        "-p",
        action="store_true",
        help="Generate heatmap plot after completion",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Reduce output verbosity"
    )

    args = parser.parse_args()

    print(f"{'='*80}")
    print("MAP-Elites Level Generation for Flappy Bird")
    print(f"{'='*80}\n")

    # Create level tester
    if args.ultra_fast:
        print("Using UltraFastLevelTester (10-15x speed, optimized for PCG)")
        from pcg.level_tester import UltraFastLevelTester

        level_tester = UltraFastLevelTester()
    elif args.fast:
        print("Using FastLevelTester (2x simulation speed)")
        level_tester = FastLevelTester()
    else:
        from pcg.level_tester import LevelTester

        level_tester = LevelTester()

    # Create runner
    runner = MAPElitesRunner(level_tester=level_tester, verbose=not args.quiet)

    # Load existing archive if specified
    if args.load:
        print(f"Loading archive from {args.load}...")
        runner.load_archive(args.load)

    # Override config if specified
    if args.iterations:
        runner.config["num_iterations"] = args.iterations
    if args.initial_samples:
        runner.config["initial_samples"] = args.initial_samples

    # Run MAP-Elites
    print("\nStarting MAP-Elites evolution...")
    start_time = time.time()

    try:
        archive = runner.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user!")
        archive = runner.archive

    elapsed = time.time() - start_time

    # Print results
    stats = archive.get_statistics()
    print(f"\nEvolution completed in {elapsed:.1f}s")
    print(f"Final coverage: {stats['coverage']:.1%}")
    print(f"Total elites: {stats['num_elites']}")
    print(f"Quality range: [{stats['min_quality']:.3f}, {stats['max_quality']:.3f}]")

    # Save archive
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    runner.save_archive(args.output)

    print_best_genomes(archive, n=5)

    save_best_genomes(archive, n=10)

    if args.plot:
        plot_path = args.output.replace(".json", "_heatmap.png")
        plot_archive_heatmap(archive, plot_path)

    print(f"\n{'='*80}")
    print("Done!")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
