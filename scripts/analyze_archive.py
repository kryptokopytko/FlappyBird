#!/usr/bin/env python3
"""Analyze and visualize MAP-Elites archive results.

This script provides comprehensive analysis and visualization of MAP-Elites archives,
including quality heatmaps, coverage plots, and statistical summaries.
"""

import argparse
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import matplotlib.pyplot as plt
import numpy as np

from pcg.map_elites import MAPElitesArchive


def plot_heatmap(archive, output_path='archive_heatmap.png'):
    """Plot quality heatmap of the archive."""
    heatmap = archive.get_heatmap()

    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(heatmap, cmap='viridis', origin='lower', aspect='auto')

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Quality Score', fontsize=12)

    # Labels
    ax.set_xlabel('Item Richness (0=sparse, 1=rich)', fontsize=12)
    ax.set_ylabel('Gap Tightness (0=loose, 1=tight)', fontsize=12)
    ax.set_title('MAP-Elites Archive - Level Quality Heatmap', fontsize=14, fontweight='bold')

    # Grid
    dims = heatmap.shape
    ax.set_xticks(range(dims[1]))
    ax.set_yticks(range(dims[0]))
    ax.grid(True, alpha=0.3, linewidth=0.5)

    # Add cell values
    for i in range(dims[0]):
        for j in range(dims[1]):
            if not np.isnan(heatmap[i, j]):
                text = ax.text(j, i, f'{heatmap[i, j]:.2f}',
                             ha="center", va="center", color="white", fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    print(f"Heatmap saved to {output_path}")


def plot_coverage_over_bins(archive, output_path='coverage_plot.png'):
    """Plot coverage distribution across gap tightness and item richness."""
    heatmap = archive.get_heatmap()
    dims = heatmap.shape

    # Calculate coverage per row (Gap Tightness levels)
    gap_tightness_coverage = []
    for i in range(dims[0]):
        row_coverage = np.sum(~np.isnan(heatmap[i, :])) / dims[1]
        gap_tightness_coverage.append(row_coverage)

    # Calculate coverage per column (Item Richness levels)
    item_richness_coverage = []
    for j in range(dims[1]):
        col_coverage = np.sum(~np.isnan(heatmap[:, j])) / dims[0]
        item_richness_coverage.append(col_coverage)

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Gap Tightness coverage
    ax1.bar(range(dims[0]), gap_tightness_coverage, color='steelblue', alpha=0.7)
    ax1.set_xlabel('Gap Tightness Bin (0=loose, 7=tight)', fontsize=11)
    ax1.set_ylabel('Coverage (%)', fontsize=11)
    ax1.set_title('Coverage across Gap Tightness Levels', fontsize=12, fontweight='bold')
    ax1.set_ylim([0, 1])
    ax1.grid(axis='y', alpha=0.3)

    # Item Richness coverage
    ax2.bar(range(dims[1]), item_richness_coverage, color='coral', alpha=0.7)
    ax2.set_xlabel('Item Richness Bin (0=sparse, 7=rich)', fontsize=11)
    ax2.set_ylabel('Coverage (%)', fontsize=11)
    ax2.set_title('Coverage across Item Richness Levels', fontsize=12, fontweight='bold')
    ax2.set_ylim([0, 1])
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Coverage plot saved to {output_path}")


def plot_quality_distribution(archive, output_path='quality_dist.png'):
    """Plot distribution of quality scores."""
    elites = archive.get_all_elites()
    qualities = [q for _, q, _ in elites]

    if not qualities:
        print("No elites to plot!")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram
    ax1.hist(qualities, bins=20, color='green', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Quality Score', fontsize=11)
    ax1.set_ylabel('Frequency', fontsize=11)
    ax1.set_title('Quality Score Distribution', fontsize=12, fontweight='bold')
    ax1.axvline(np.mean(qualities), color='red', linestyle='--', linewidth=2, label='Mean')
    ax1.axvline(np.median(qualities), color='blue', linestyle='--', linewidth=2, label='Median')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # Box plot
    ax2.boxplot(qualities, vert=True, patch_artist=True,
                boxprops=dict(facecolor='lightgreen', alpha=0.7))
    ax2.set_ylabel('Quality Score', fontsize=11)
    ax2.set_title('Quality Score Statistics', fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Quality distribution saved to {output_path}")


def print_statistics(archive):
    """Print detailed statistics about the archive."""
    stats = archive.get_statistics()
    elites = archive.get_all_elites()

    print(f"\n{'='*80}")
    print("ARCHIVE STATISTICS")
    print(f"{'='*80}")
    print(f"Archive dimensions: {archive.dims[0]} × {archive.dims[1]} = {archive.dims[0] * archive.dims[1]} cells")
    print(f"Number of elites: {stats['num_elites']}")
    print(f"Coverage: {stats['coverage']:.1%}")
    print(f"\nQuality scores:")
    print(f"  Minimum: {stats['min_quality']:.4f}")
    print(f"  Average: {stats['avg_quality']:.4f}")
    print(f"  Maximum: {stats['max_quality']:.4f}")

    if elites:
        qualities = [q for _, q, _ in elites]
        print(f"  Median:  {np.median(qualities):.4f}")
        print(f"  Std dev: {np.std(qualities):.4f}")

    # Coverage analysis
    heatmap = archive.get_heatmap()
    dims = heatmap.shape

    print(f"\nCoverage per Gap Tightness level:")
    for i in range(dims[0]):
        row_coverage = np.sum(~np.isnan(heatmap[i, :])) / dims[1]
        gap_tightness_level = (i + 0.5) / dims[0]
        print(f"  Gap Tightness {gap_tightness_level:.1f}: {row_coverage:.1%}")

    print(f"\nCoverage per Item Richness level:")
    for j in range(dims[1]):
        col_coverage = np.sum(~np.isnan(heatmap[:, j])) / dims[0]
        item_richness_level = (j + 0.5) / dims[1]
        print(f"  Item Richness {item_richness_level:.1f}: {col_coverage:.1%}")

    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description='Analyze MAP-Elites archive')
    parser.add_argument('archive', type=str,
                        help='Path to archive JSON file')
    parser.add_argument('--output-dir', '-o', type=str, default='.',
                        help='Output directory for plots')
    parser.add_argument('--heatmap', action='store_true',
                        help='Generate quality heatmap')
    parser.add_argument('--coverage', action='store_true',
                        help='Generate coverage plots')
    parser.add_argument('--distribution', action='store_true',
                        help='Generate quality distribution plots')
    parser.add_argument('--all', '-a', action='store_true',
                        help='Generate all plots')

    args = parser.parse_args()

    # Load archive
    print(f"Loading archive from {args.archive}...")
    archive = MAPElitesArchive.load(args.archive)
    print("Archive loaded successfully!\n")

    # Print statistics
    print_statistics(archive)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate plots
    if args.all or args.heatmap:
        output_path = os.path.join(args.output_dir, 'archive_heatmap.png')
        plot_heatmap(archive, output_path)

    if args.all or args.coverage:
        output_path = os.path.join(args.output_dir, 'coverage_plot.png')
        plot_coverage_over_bins(archive, output_path)

    if args.all or args.distribution:
        output_path = os.path.join(args.output_dir, 'quality_dist.png')
        plot_quality_distribution(archive, output_path)

    if not (args.heatmap or args.coverage or args.distribution or args.all):
        print("No plots requested. Use --all or specific plot flags.")
        print("Example: python analyze_archive.py archive.json --all")


if __name__ == '__main__':
    main()
