import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pcg.novelty_runner import NoveltySearchRunner
from pcg.level_tester import UltraFastLevelTester


def main():
    parser = argparse.ArgumentParser(description="Run Novelty Search level generation")
    parser.add_argument("--iterations", "-n", type=int, default=2000,
                       help="Number of iterations (default: 2000)")
    parser.add_argument("--k-neighbors", "-k", type=int, default=15,
                       help="Number of nearest neighbors for novelty (default: 15)")
    parser.add_argument("--max-archive-size", type=int, default=1000,
                       help="Maximum archive size (default: 1000)")
    parser.add_argument("--initial-samples", type=int, default=200,
                       help="Initial random samples (default: 200)")
    parser.add_argument("--mutation-rate", type=float, default=0.45,
                       help="Mutation rate (default: 0.45)")
    parser.add_argument("--mutation-sigma", type=float, default=0.25,
                       help="Mutation sigma (default: 0.25)")
    parser.add_argument("--output", "-o", type=str, default="data/novelty_archive.json",
                       help="Output file path (default: data/novelty_archive.json)")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Reduce verbosity")

    args = parser.parse_args()

    print("Starting Novelty Search level generation...")
    print(f"Parameters:")
    print(f"  Iterations: {args.iterations}")
    print(f"  k-neighbors: {args.k_neighbors}")
    print(f"  Max archive size: {args.max_archive_size}")
    print(f"  Initial samples: {args.initial_samples}")
    print(f"  Mutation rate: {args.mutation_rate}")
    print(f"  Mutation sigma: {args.mutation_sigma}")
    print(f"  Output: {args.output}")
    print()

    level_tester = UltraFastLevelTester()

    runner = NoveltySearchRunner(
        level_tester=level_tester,
        max_archive_size=args.max_archive_size
    )

    archive = runner.run(
        num_iterations=args.iterations,
        k_neighbors=args.k_neighbors,
        initial_samples=args.initial_samples,
        mutation_rate=args.mutation_rate,
        mutation_sigma=args.mutation_sigma,
        verbose=not args.quiet
    )

    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    runner.save_archive(args.output)

    print(f"\nArchive saved to {args.output}")


if __name__ == "__main__":
    main()
