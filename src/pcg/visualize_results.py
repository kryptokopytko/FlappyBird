"""
Visualization utilities for comparing PCG algorithm results.

This module provides functions to create comprehensive visualizations
comparing MAP-Elites, MCTS-QD, and Novelty Search results.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from typing import Optional, Dict, Any, List, Tuple

from pcg.map_elites.map_elites import MAPElitesArchive
from pcg.mcts.mcts_archive import MCTSArchive
from pcg.novelty.novelty_archive import NoveltyArchive


def visualize_pcg_comparison(
    map_elites_archive: Optional[MAPElitesArchive] = None,
    mcts_qd_archive: Optional[MCTSArchive] = None,
    novelty_archive: Optional[NoveltyArchive] = None,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (20, 12),
    show: bool = True,
) -> plt.Figure:
    """
    Create comprehensive visualization comparing PCG algorithm results.

    Args:
        map_elites_archive: MAP-Elites archive (optional)
        mcts_qd_archive: MCTS-QD archive (optional)
        novelty_archive: Novelty Search archive (optional)
        save_path: Path to save the figure (optional)
        figsize: Figure size (width, height)
        show: Whether to show the figure

    Returns:
        Matplotlib figure object
    """
    # Count how many archives we have
    archives = []
    if map_elites_archive is not None:
        archives.append(("MAP-Elites", map_elites_archive))
    if mcts_qd_archive is not None:
        archives.append(("MCTS-QD", mcts_qd_archive))
    if novelty_archive is not None:
        archives.append(("Novelty Search", novelty_archive))

    if not archives:
        raise ValueError("At least one archive must be provided")

    # Create figure with subplots
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(3, len(archives), figure=fig, hspace=0.3, wspace=0.3)

    # Row 1: Quality heatmaps for grid-based archives, behavior scatter for novelty
    for idx, (name, archive) in enumerate(archives):
        ax = fig.add_subplot(gs[0, idx])
        _plot_archive_heatmap(ax, name, archive)

    # Row 2: Quality distributions
    ax_dist = fig.add_subplot(gs[1, :])
    _plot_quality_distributions(ax_dist, archives)

    # Row 3: Statistics comparison
    ax_stats = fig.add_subplot(gs[2, :])
    _plot_statistics_comparison(ax_stats, archives)

    plt.suptitle("PCG Algorithm Comparison", fontsize=16, fontweight="bold")

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Figure saved to {save_path}")

    if show:
        plt.show()

    return fig


def _plot_archive_heatmap(ax: plt.Axes, name: str, archive: Any) -> None:
    """Plot quality heatmap for grid-based archives or behavior scatter for novelty."""
    if isinstance(archive, (MAPElitesArchive, MCTSArchive)):
        # Grid-based archive: show heatmap
        heatmap = archive.get_heatmap()

        im = ax.imshow(heatmap, cmap="viridis", aspect="auto", origin="lower")
        ax.set_title(f"{name}\nQuality Heatmap", fontweight="bold")
        ax.set_xlabel("Spacing Density →")
        ax.set_ylabel("Gap Tightness →")

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Quality", rotation=270, labelpad=15)

        # Add grid
        ax.set_xticks(np.arange(heatmap.shape[1]))
        ax.set_yticks(np.arange(heatmap.shape[0]))
        ax.grid(which="both", color="white", linewidth=0.5, alpha=0.3)

        # Add coverage annotation
        stats = archive.get_statistics()
        coverage_text = (
            f"Coverage: {stats['coverage']:.1%}\n{stats['num_elites']} elites"
        )
        ax.text(
            0.02,
            0.98,
            coverage_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

    elif isinstance(archive, NoveltyArchive):
        # Novelty archive: scatter plot of behavior space
        individuals = archive.get_all_individuals()
        if individuals:
            behaviors = np.array([ind.behavior for ind in individuals])
            qualities = np.array([ind.quality for ind in individuals])

            scatter = ax.scatter(
                behaviors[:, 1],
                behaviors[:, 0],
                c=qualities,
                cmap="viridis",
                s=50,
                alpha=0.6,
                edgecolors="black",
                linewidth=0.5,
            )

            ax.set_title(f"{name}\nBehavior Space Coverage", fontweight="bold")
            ax.set_xlabel("Spacing Density →")
            ax.set_ylabel("Gap Tightness →")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.grid(True, alpha=0.3)

            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label("Quality", rotation=270, labelpad=15)

            # Add count annotation
            stats = archive.get_statistics()
            count_text = f"Individuals: {stats['size']}"
            ax.text(
                0.02,
                0.98,
                count_text,
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
            )
        else:
            ax.text(
                0.5,
                0.5,
                "No individuals in archive",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_title(f"{name}\nBehavior Space Coverage", fontweight="bold")


def _plot_quality_distributions(ax: plt.Axes, archives: List[Tuple[str, Any]]) -> None:
    """Plot quality distributions as violin plots."""
    data = []
    labels = []

    for name, archive in archives:
        if isinstance(archive, (MAPElitesArchive, MCTSArchive)):
            elites = archive.get_all_elites()
            if elites:
                qualities = [q for _, q, _ in elites]
                data.append(qualities)
                labels.append(name)
        elif isinstance(archive, NoveltyArchive):
            individuals = archive.get_all_individuals()
            if individuals:
                qualities = [ind.quality for ind in individuals]
                data.append(qualities)
                labels.append(name)

    if data:
        # Create violin plot
        parts = ax.violinplot(
            data, positions=range(len(data)), showmeans=True, showmedians=True
        )

        # Color the violin plots
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
        for i, pc in enumerate(parts["bodies"]):
            pc.set_facecolor(colors[i % len(colors)])
            pc.set_alpha(0.7)

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels)
        ax.set_ylabel("Quality Score")
        ax.set_title("Quality Distribution Comparison", fontweight="bold")
        ax.grid(True, axis="y", alpha=0.3)

        # Add mean/median legend
        ax.legend(
            [parts["cmeans"], parts["cmedians"]], ["Mean", "Median"], loc="upper right"
        )

        # Add statistics annotations
        for i, (name, qualities) in enumerate(zip(labels, data)):
            mean_q = np.mean(qualities)
            std_q = np.std(qualities)
            ax.text(
                i,
                ax.get_ylim()[1] * 0.95,
                f"μ={mean_q:.3f}\nσ={std_q:.3f}",
                ha="center",
                va="top",
                fontsize=8,
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.7),
            )
    else:
        ax.text(
            0.5,
            0.5,
            "No quality data available",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )


def _plot_statistics_comparison(ax: plt.Axes, archives: List[Tuple[str, Any]]) -> None:
    """Plot bar chart comparing key statistics across algorithms."""
    names = []
    avg_qualities = []
    max_qualities = []
    coverages = []

    for name, archive in archives:
        stats = archive.get_statistics()
        names.append(name)
        avg_qualities.append(stats.get("avg_quality", 0.0))
        max_qualities.append(stats.get("max_quality", 0.0))

        if isinstance(archive, (MAPElitesArchive, MCTSArchive)):
            coverages.append(stats.get("coverage", 0.0))
        elif isinstance(archive, NoveltyArchive):
            # For novelty search, use normalized size as "coverage"
            coverages.append(min(1.0, stats.get("size", 0) / archive.max_size))

    x = np.arange(len(names))
    width = 0.25

    # Create grouped bar chart
    ax.bar(
        x - width, avg_qualities, width, label="Avg Quality", color="#1f77b4", alpha=0.8
    )
    ax.bar(x, max_qualities, width, label="Max Quality", color="#ff7f0e", alpha=0.8)
    ax.bar(
        x + width,
        coverages,
        width,
        label="Coverage/Fullness",
        color="#2ca02c",
        alpha=0.8,
    )

    ax.set_ylabel("Score")
    ax.set_title("Key Statistics Comparison", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)

    # Add value labels on bars
    for i, (avg, max_q, cov) in enumerate(zip(avg_qualities, max_qualities, coverages)):
        ax.text(
            i - width, avg + 0.01, f"{avg:.3f}", ha="center", va="bottom", fontsize=8
        )
        ax.text(i, max_q + 0.01, f"{max_q:.3f}", ha="center", va="bottom", fontsize=8)
        ax.text(
            i + width, cov + 0.01, f"{cov:.2f}", ha="center", va="bottom", fontsize=8
        )


def load_and_visualize(
    map_elites_path: Optional[str] = None,
    mcts_qd_path: Optional[str] = None,
    novelty_path: Optional[str] = None,
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Load archives from files and create comparison visualization.

    Args:
        map_elites_path: Path to MAP-Elites archive JSON (optional)
        mcts_qd_path: Path to MCTS-QD archive JSON (optional)
        novelty_path: Path to Novelty Search archive JSON (optional)
        save_path: Path to save the figure (optional)
        show: Whether to show the figure

    Returns:
        Matplotlib figure object

    Example:
        >>> fig = load_and_visualize(
        ...     map_elites_path="results/map_elites.json",
        ...     mcts_qd_path="results/mcts_qd.json",
        ...     novelty_path="results/novelty.json",
        ...     save_path="comparison.png"
        ... )
    """
    map_elites_archive = None
    mcts_qd_archive = None
    novelty_archive = None

    if map_elites_path:
        print(f"Loading MAP-Elites archive from {map_elites_path}...")
        map_elites_archive = MAPElitesArchive.load(map_elites_path)

    if mcts_qd_path:
        print(f"Loading MCTS-QD archive from {mcts_qd_path}...")
        mcts_qd_archive = MCTSArchive.load(mcts_qd_path)

    if novelty_path:
        print(f"Loading Novelty Search archive from {novelty_path}...")
        novelty_archive = NoveltyArchive.load(novelty_path)

    return visualize_pcg_comparison(
        map_elites_archive=map_elites_archive,
        mcts_qd_archive=mcts_qd_archive,
        novelty_archive=novelty_archive,
        save_path=save_path,
        show=show,
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python visualize_results.py <map_elites.json> [mcts_qd.json] [novelty.json] [output.png]"
        )
        sys.exit(1)

    map_elites = sys.argv[1] if len(sys.argv) > 1 else None
    mcts_qd = sys.argv[2] if len(sys.argv) > 2 else None
    novelty = sys.argv[3] if len(sys.argv) > 3 else None
    output = sys.argv[4] if len(sys.argv) > 4 else None

    load_and_visualize(
        map_elites_path=map_elites,
        mcts_qd_path=mcts_qd,
        novelty_path=novelty,
        save_path=output,
        show=True,
    )
