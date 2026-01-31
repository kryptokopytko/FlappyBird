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
        gap_bin, spacing_bin = cell
        dims = archive.dims

        # Get actual computed features from level
        actual_features = genome.level.compute_features()
        gap_actual = actual_features.get("gap_tightness", 0.5)
        spacing_actual = actual_features.get("spacing_density", 0.5)
        vertical_actual = actual_features.get("vertical_variance", 0.5)

        print(
            f"\n{i}. Quality: {quality:.3f} | "
            f"Gap: {gap_actual:.2f} | Spacing: {spacing_actual:.2f} | Vertical: {vertical_actual:.2f}"
        )
        print(f"   Cell: ({gap_bin}, {spacing_bin})")
        print(f"   Level structure:")

        # Print concrete level info
        level = genome.level
        print(f"     Total pipes: {len(level.pipes)}")
        print(f"     Total items: {len(level.items)} ({len([i for i in level.items if i.type == 'coin'])} coins)")
        print(f"     Length: {level.length:.1f} units")

        # Compute average metrics
        if level.pipes:
            avg_gap = sum(p.gap_size for p in level.pipes) / len(level.pipes)
            spacings = [level.pipes[i+1].x - level.pipes[i].x for i in range(len(level.pipes)-1)]
            avg_spacing = sum(spacings) / len(spacings) if spacings else 0
            print(f"     Avg gap size: {avg_gap:.1f}, Avg spacing: {avg_spacing:.1f}")


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

    # Always use ultra-fast mode (10-15x speed, optimized for PCG)
    print("Using UltraFastLevelTester (10-15x speed, optimized for PCG)")
    from pcg.level_tester import UltraFastLevelTester

    level_tester = UltraFastLevelTester()

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
