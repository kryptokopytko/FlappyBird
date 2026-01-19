"""Level testing system for evaluating genomes with bots."""
import time
from typing import Dict, List
from pcg.level_genome import LevelGenome
from utils.config import PCG_CONFIG


class LevelTester:
    """
    Tests level genomes by running bots and collecting performance data.
    """

    def __init__(self):
        self.config = PCG_CONFIG['evaluation']

    def test_genome(self, genome: LevelGenome) -> Dict[str, List[Dict]]:
        """
        Test a genome with all configured bots.

        Args:
            genome: LevelGenome to test

        Returns:
            Dict mapping bot_name -> list of run results
            Each run result: {score, distance, coins, survived, death_reason}
        """
        results = {}

        # Test with each bot type
        for bot_type in self.config['bots']:
            bot_results = []

            # Run multiple tests per bot
            for run_idx in range(self.config['num_runs_per_bot']):
                run_result = self._run_single_test(genome, bot_type, run_idx)
                bot_results.append(run_result)

            results[bot_type] = bot_results

        return results

    def _run_single_test(self, genome: LevelGenome, bot_type: str, run_idx: int) -> Dict:
        """
        Run a single test with a specific bot on a genome.

        Args:
            genome: LevelGenome to test
            bot_type: Type of bot to use
            run_idx: Run index for this test

        Returns:
            Dict with test results
        """
        from game_graphical import Game
        from level_generator import LevelGenerator

        # Create headless game instance
        game = Game(headless=True)

        # Configure level generator with genome parameters
        game.level_generator = LevelGenerator.from_genome(genome)

        # Set bot type and start game
        game.bot_type = bot_type
        game.start_game(bot_mode=True)

        # Run test for specified duration
        start_time = time.time()
        duration = self.config['test_duration']

        while game.running and game.state == 'playing':
            game.update(game.dt)

            elapsed = time.time() - start_time
            if elapsed >= duration:
                # Survived full duration
                break

            # No sleep - run as fast as possible
            # (We can add minimal sleep for CPU if needed)

        # Collect results
        survived = game.state == 'playing'
        elapsed = time.time() - start_time

        # Calculate distance traveled
        distance = game.scroll_offset

        result = {
            'score': game.score,
            'distance': distance,
            'coins': game.coins,
            'survived': survived,
            'death_reason': 'survived' if survived else 'collision',
            'time': elapsed,
            'bot_type': bot_type,
            'run_idx': run_idx
        }

        return result


class FastLevelTester(LevelTester):
    """
    Optimized level tester that runs tests faster by:
    - Removing unnecessary delays
    - Simplifying physics simulation
    - Running multiple tests in parallel (future)
    """

    def _run_single_test(self, genome: LevelGenome, bot_type: str, run_idx: int) -> Dict:
        """
        Run a single test in fast mode (no delays, simplified simulation).
        """
        from game_graphical import Game
        from level_generator import LevelGenerator

        # Create headless game instance
        game = Game(headless=True)

        # Configure level generator with genome parameters
        game.level_generator = LevelGenerator.from_genome(genome)

        # Set bot type and start game
        game.bot_type = bot_type
        game.start_game(bot_mode=True)

        # Run test for specified duration (in simulation time)
        sim_time = 0
        duration = self.config['test_duration']

        # Use larger time steps for faster simulation
        fast_dt = game.dt * 2  # 2x faster simulation

        max_iterations = int(duration / fast_dt) + 100  # Safety limit
        iterations = 0

        while game.running and game.state == 'playing' and iterations < max_iterations:
            game.update(fast_dt)
            sim_time += fast_dt
            iterations += 1

            if sim_time >= duration:
                # Survived full duration
                break

        # Collect results
        survived = game.state == 'playing'

        # Calculate distance traveled
        distance = game.scroll_offset

        result = {
            'score': game.score,
            'distance': distance,
            'coins': game.coins,
            'survived': survived,
            'death_reason': 'survived' if survived else 'collision',
            'time': sim_time,
            'bot_type': bot_type,
            'run_idx': run_idx
        }

        return result
