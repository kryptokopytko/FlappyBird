#!/usr/bin/env python3
"""Entry point for the Flappy Bird game with testing support."""

import argparse
import sys
import time


def run_headless_test(game, duration):
    """Run headless test for specified duration."""
    start_time = time.time()
    max_duration = duration

    print(f"Starting headless test: {game.bot_type} bot, {duration}s duration")

    while game.running and game.state == 'playing':
        game.update(game.dt)

        elapsed = time.time() - start_time
        if elapsed >= max_duration:
            # Test passed - survived duration
            print(f"\n✓ TEST PASSED: {game.bot_type} bot survived {duration} seconds!")
            print(f"  Score: {game.score}")
            print(f"  Coins: {game.coins}")
            return True

        # Throttle loop to match game FPS
        time.sleep(game.dt)

    # Test failed - bot died
    elapsed = time.time() - start_time
    if game.state == 'game_over':
        print(f"\n✗ TEST FAILED: {game.bot_type} bot died after {elapsed:.2f} seconds")
        print(f"  Score: {game.score}")
        print(f"  Bird position: y={game.bird.y:.2f}, velocity={game.bird.velocity:.2f}")

        # Save death frame
        save_death_frame(game, elapsed)
        return False

    return False


def save_death_frame(game, elapsed_time):
    """Save ASCII render of death frame for debugging."""
    import os

    # Create death_frames directory if it doesn't exist
    os.makedirs('death_frames', exist_ok=True)

    filename = f"death_frames/{game.bot_type}_{int(time.time())}.txt"

    # Render death frame in ASCII
    width = game.width
    height = game.height

    # Create empty grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Draw bird (as circle)
    # Bird is circular, center at (bird.x + width/2, bird.y + height/2)
    bird_center_x = game.bird.x + game.bird.width / 2
    bird_center_y = game.bird.y + game.bird.height / 2

    # Draw bird with more detail
    bird_box = game.bird.get_hitbox()
    for dy in range(int(bird_box['height'])):
        y = int(bird_box['y']) + dy
        for dx in range(int(bird_box['width'])):
            x = int(bird_box['x']) + dx
            if 0 <= y < height and 0 <= x < width:
                # Use different markers for center vs edge
                dist_from_center = ((x - bird_center_x)**2 + (y - bird_center_y)**2)**0.5
                if dist_from_center < 0.5:
                    grid[y][x] = '@'  # Center
                elif dist_from_center < 1.5:
                    grid[y][x] = 'O'  # Inner circle
                else:
                    grid[y][x] = 'o'  # Outer edge

    # Draw pipes
    for pipe in game.pipes:
        # Top pipe
        top_box = pipe.get_top_hitbox()
        for y in range(1, int(top_box['y'] + top_box['height'])):
            for dx in range(int(top_box['width'])):
                x = int(top_box['x']) + dx
                if 0 <= y < height and 0 <= x < width:
                    grid[y][x] = '█'

        # Bottom pipe
        bottom_box = pipe.get_bottom_hitbox()
        for dy in range(int(bottom_box['height'])):
            y = int(bottom_box['y']) + dy
            for dx in range(int(bottom_box['width'])):
                x = int(bottom_box['x']) + dx
                if 0 <= y < height and 0 <= x < width:
                    grid[y][x] = '█'

    # Draw ground
    ground_y = height - 1
    for x in range(width):
        grid[ground_y][x] = '='

    # Draw ceiling
    for x in range(width):
        grid[0][x] = '='

    # Verify collision
    collision_detected, collision_reason = verify_collision(game)

    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Bot: {game.bot_type}\n")
        f.write(f"Survived: {elapsed_time:.2f}s\n")
        f.write(f"\n=== BIRD INFO ===\n")
        f.write(f"Bird exact position: x={game.bird.x:.2f}, y={game.bird.y:.2f}\n")
        f.write(f"Bird size: {game.bird.width}x{game.bird.height}\n")
        f.write(f"Bird center: x={bird_center_x:.2f}, y={bird_center_y:.2f}\n")
        f.write(f"Bird velocity: {game.bird.velocity:.2f}\n")
        f.write(f"Bird hitbox (3x3): {bird_box}\n")
        f.write(f"\n=== GAME STATE ===\n")
        f.write(f"Score: {game.score}, Coins: {game.coins}\n")
        f.write(f"Scroll offset: {game.scroll_offset:.2f}\n")
        f.write(f"\n=== NEARBY PIPES ===\n")
        for i, pipe in enumerate(game.pipes[:3]):  # Show first 3 pipes
            f.write(f"Pipe {i+1}: x={pipe.x:.1f}-{pipe.x + pipe.width:.1f}, ")
            f.write(f"gap y={pipe.y_top:.1f}-{pipe.y_bottom:.1f}, ")
            f.write(f"gap_size={pipe.gap_size}\n")

        f.write(f"\n=== COLLISION ===\n")
        f.write(f"Collision detected: {collision_detected}\n")
        f.write(f"Collision reason: {collision_reason}\n")

        if not collision_detected:
            f.write("\n!!! WARNING: FALSE DEATH - NO COLLISION DETECTED !!!\n")

        f.write("\n" + "=" * width + "\n\n")

        for y, row in enumerate(grid):
            f.write(f"{y:2d} {''.join(row)}\n")

    print(f"  Death frame saved to: {filename}")

    if not collision_detected:
        print(f"  !!! WARNING: No collision detected - possible bug!")
    else:
        print(f"  Collision verified: {collision_reason}")


def verify_collision(game):
    """Verify if bird actually collided with something."""
    bird_box = game.bird.get_hitbox()

    # Check ceiling
    if bird_box['y'] <= 0:
        return True, "ceiling (y<=0)"

    # Check floor
    ground_level = game.height - 1
    if bird_box['y'] + bird_box['height'] > ground_level:
        return True, f"floor (y={bird_box['y']+bird_box['height']} > {ground_level})"

    # Check pipes
    for pipe in game.pipes:
        if game.collision_detector.check_bird_pipe(game.bird, pipe):
            return True, f"pipe at x={pipe.x:.1f}"

    return False, "NO COLLISION DETECTED (BUG!)"


def main():
    """Run the game with optional testing support."""
    parser = argparse.ArgumentParser(description='Flappy Bird Game')
    parser.add_argument('--bot', '--aggressive', '--reactive', '--coin-collector',
                        dest='bot',
                        choices=['aggressive', 'reactive', 'coin_collector'],
                        help='Run game with specified bot (conservative, aggressive, reactive, coin_collector)')
    parser.add_argument('--headless', '--no-graphics',
                        dest='headless',
                        action='store_true',
                        help='Run without graphics (for testing)')
    parser.add_argument('--test-duration', type=int, default=20,
                        help='Test duration in seconds (headless mode, default: 20)')

    args = parser.parse_args()

    # Import pygame only if NOT headless
    if not args.headless:
        import pygame
        pygame.init()

    from game_graphical import Game

    # Create game
    game = Game(headless=args.headless)

    # If bot mode, set bot and start game
    if args.bot:
        game.bot_type = args.bot
        game.start_game(bot_mode=True)

        if args.headless:
            # Headless test mode
            success = run_headless_test(game, args.test_duration)
            sys.exit(0 if success else 1)
        else:
            # Normal mode with bot
            game.run()
    else:
        # Normal mode - show menu
        if args.headless:
            print("Error: --headless requires --bot to be specified")
            sys.exit(1)
        game.run()


if __name__ == '__main__':
    main()
