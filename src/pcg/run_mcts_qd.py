import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pcg.mcts_qd_runner import MCTSQDRunner
from pcg.level_tester import UltraFastLevelTester


def main():
    parser = argparse.ArgumentParser(description="Run MCTS-QD level generation")
    parser.add_argument("--iterations", "-n", type=int, default=36,
                       help="Number of MCTS iterations (default: 36)")
    parser.add_argument("--simulations", "-s", type=int, default=500,
                       help="Number of MCTS simulations per level (default: 500)")
    parser.add_argument("--exploration", "-e", type=float, default=1.414,
                       help="Exploration constant for UCT (default: sqrt(2))")
    parser.add_argument("--target-pipes", type=int, default=17,
                       help="Target number of pipes per level (default: 17, range: 15-19)")
    parser.add_argument("--output", "-o", type=str, default="data/mcts_qd_archive.json",
                       help="Output file path (default: data/mcts_qd_archive.json)")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Reduce verbosity")

    args = parser.parse_args()

    print("Starting MCTS-QD level generation...")
    print(f"Parameters:")
    print(f"  Iterations: {args.iterations}")
    print(f"  Simulations per level: {args.simulations}")
    print(f"  Exploration constant: {args.exploration}")
    print(f"  Target pipes: {args.target_pipes}")
    print(f"  Output: {args.output}")
    print()

    level_tester = UltraFastLevelTester()

    runner = MCTSQDRunner(
        level_tester=level_tester,
        exploration_constant=args.exploration,
        archive_dims=(6, 6)
    )

    archive = runner.run(
        num_iterations=args.iterations,
        simulations_per_level=args.simulations,
        target_pipes=args.target_pipes,
        verbose=not args.quiet
    )

    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    runner.save_archive(args.output)

    print(f"\nArchive saved to {args.output}")


if __name__ == "__main__":
    main()
