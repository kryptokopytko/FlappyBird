#!/usr/bin/env python3
import argparse
import sys
import time


def run_headless_test(game, duration):
    start_time = time.time()
    print(f"Starting headless test: {game.bot_type} bot, {duration}s duration")

    while game.running and game.state == 'playing':
        game.update(game.dt)

        elapsed = time.time() - start_time
        if elapsed >= duration:
            print(f"\n✓ TEST PASSED: {game.bot_type} bot survived {duration} seconds!")
            print(f"  Score: {game.score}")
            print(f"  Coins: {game.coins}")
            return True

        time.sleep(game.dt)

    elapsed = time.time() - start_time
    if game.state == 'game_over':
        print(f"\n✗ TEST FAILED: {game.bot_type} bot died after {elapsed:.2f} seconds")
        print(f"  Score: {game.score}")
        print(f"  Bird position: y={game.bird.y:.2f}, velocity={game.bird.velocity:.2f}")
        return False

    return False


def main():
    parser = argparse.ArgumentParser(description='Flappy Bird Game')
    parser.add_argument('--bot', '--aggressive', '--reactive', '--coin-collector',
                        dest='bot',
                        choices=['aggressive', 'reactive', 'coin_collector'],
                        help='Run game with specified bot')
    parser.add_argument('--headless', '--no-graphics',
                        dest='headless',
                        action='store_true',
                        help='Run without graphics for testing')
    parser.add_argument('--test-duration', type=int, default=20,
                        help='Test duration in seconds (default: 20)')

    args = parser.parse_args()

    if not args.headless:
        import pygame
        pygame.init()

    from game_graphical import Game

    game = Game(headless=args.headless)

    if args.bot:
        game.bot_type = args.bot
        game.start_game(bot_mode=True)

        if args.headless:
            success = run_headless_test(game, args.test_duration)
            sys.exit(0 if success else 1)
        else:
            game.run()
    else:
        if args.headless:
            print("Error: --headless requires --bot to be specified")
            sys.exit(1)
        game.run()


if __name__ == '__main__':
    main()
