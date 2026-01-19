"""Main game loop and logic with graphical renderer."""

import time
import pygame
from graphical_renderer import GraphicalRenderer
from entities.bird import Bird
from entities.coin import Coin
from entities.powerup import PowerUp
from level_generator import LevelGenerator
from physics import CollisionDetector
from effects import EffectManager
from ai.aggressive_bot import AggressiveBot
from ai.reactive_bot import ReactiveBot
from ai.coin_collector_bot import CoinCollectorBot
from utils.config import GAME_CONFIG


class Game:
    """Main game class handling the game loop with graphical rendering."""

    def __init__(self, headless=False):
        self.headless = headless

        if not headless:
            self.renderer = GraphicalRenderer(width=800, height=600)
            self.clock = pygame.time.Clock()
        else:
            self.renderer = None
            self.clock = None

        self.bird = Bird()
        self.level_generator = LevelGenerator(difficulty='medium')
        self.collision_detector = CollisionDetector()
        self.effect_manager = EffectManager(self)

        self.width = GAME_CONFIG['screen']['width']
        self.height = GAME_CONFIG['screen']['height']
        self.fps = GAME_CONFIG['screen']['fps']
        self.dt = 1.0 / self.fps

        self.running = True
        self.paused = False
        self.game_over = False
        self.score = 0
        self.best_score = 0
        self.coins = 0

        self.scroll_offset = 0
        self.scroll_speed = GAME_CONFIG['level']['scroll_speed']
        self.base_scroll_speed = GAME_CONFIG['level']['scroll_speed']
        self.speed_increase_rate = 0.15  # Increase speed by 0.15 per second
        self.max_scroll_speed = self.base_scroll_speed * 1.5  # Max 1.5x base speed
        self.time_elapsed = 0

        # Entities
        self.pipes = []
        self.items = []  # Coins and power-ups

        # Game state
        self.state = 'menu'  # menu, bot_menu, ready, playing, game_over
        self.selected_menu_option = 0  # Currently selected menu option
        self.selected_bot_option = 0  # Currently selected bot
        self.game_started = False  # Track if player has pressed space to start

        # Bot mode
        self.bot_mode = False
        self.bot = None
        self.bot_type = 'aggressive'  # aggressive, reactive, coin_collector

    def run(self):
        """Main game loop."""
        if self.headless:
            # Headless mode - simplified loop for testing
            import time
            while self.running and self.state == 'playing':
                self.update(self.dt)
                time.sleep(self.dt)
        else:
            # Normal graphical mode
            while self.running:
                # Handle input
                self.handle_input()

                # Update game state
                if (self.state == 'ready') or (self.state == 'playing' and not self.paused):
                    self.update(self.dt)

                # Render
                self.render()

                # Frame rate control
                self.clock.tick(self.fps)

            self.renderer.close()

    def handle_input(self):
        """Handle keyboard and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                # Global keys
                if event.key == pygame.K_ESCAPE:
                    if self.state == 'playing' or self.state == 'ready':
                        self.state = 'menu'
                        self.reset_game()
                    else:
                        self.running = False
                    return

                # Menu state
                if self.state == 'menu':
                    if event.key == pygame.K_UP:
                        self.selected_menu_option = (self.selected_menu_option - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        self.selected_menu_option = (self.selected_menu_option + 1) % 3
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.execute_menu_option(self.selected_menu_option)
                    # Number keys for direct selection (1-3)
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        option_index = event.key - pygame.K_1
                        self.selected_menu_option = option_index
                        self.execute_menu_option(option_index)

                # Bot selection menu state
                elif self.state == 'bot_menu':
                    if event.key == pygame.K_UP:
                        self.selected_bot_option = (self.selected_bot_option - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        self.selected_bot_option = (self.selected_bot_option + 1) % 4
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.execute_bot_selection(self.selected_bot_option)
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                        self.selected_bot_option = 0
                    # Number keys for direct selection (1-4)
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        option_index = event.key - pygame.K_1
                        self.selected_bot_option = option_index
                        self.execute_bot_selection(option_index)

                # Ready state (waiting for first jump)
                elif self.state == 'ready':
                    if event.key == pygame.K_SPACE:
                        # First jump - start the game
                        self.bird.jump()
                        self.game_started = True
                        self.state = 'playing'

                # Playing state
                elif self.state == 'playing':
                    if event.key == pygame.K_SPACE:
                        if not self.paused:
                            self.bird.jump()
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self.start_game(bot_mode=self.bot_mode)
                    elif event.key == pygame.K_d:
                        # Toggle DEBUG mode
                        self.renderer.debug_mode = not self.renderer.debug_mode

                # Game over state
                elif self.state == 'game_over':
                    if event.key == pygame.K_SPACE:
                        self.start_game(bot_mode=self.bot_mode)
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                        self.reset_game()

    def update(self, dt):
        """Update game state."""
        # Bot AI decision
        if self.bot_mode and self.bot and self.game_started:
            if self.bot.decide_action():
                self.bird.jump()

        # Update bird physics (only when game has started)
        if self.game_started:
            self.bird.update(dt)

            # Progressive speed increase
            self.time_elapsed += dt
            self.scroll_speed = min(
                self.base_scroll_speed + (self.time_elapsed * self.speed_increase_rate),
                self.max_scroll_speed
            )

        # Update effects
        self.effect_manager.update(dt)

        # Update scroll
        self.scroll_offset += self.scroll_speed * dt

        # Update pipes
        for pipe in self.pipes:
            pipe.update(self.scroll_speed, dt)

            # Check if bird passed the pipe (for scoring)
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 10

        # Remove offscreen pipes
        self.pipes = [p for p in self.pipes if not p.is_offscreen()]

        # Generate new pipes
        if self.level_generator.should_generate_pipe(self.pipes):
            new_pipe = self.level_generator.generate_pipe()
            self.pipes.append(new_pipe)
            # Generate items for this pipe
            new_items = self.level_generator.generate_items_for_pipe(new_pipe)
            self.items.extend(new_items)

        # Update items
        for item in self.items:
            item.update(self.scroll_speed, dt)

        # Remove offscreen items
        self.items = [item for item in self.items if not item.is_offscreen()]

        # Check collisions
        self.check_collisions()

        # Check bounds
        if self.bird.is_out_of_bounds(self.height):
            self.end_game()

    def check_collisions(self):
        """Check for collisions between bird and obstacles."""
        bird_x = self.bird.x

        # Check pipe collisions - only check nearby pipes
        for pipe in self.pipes:
            # Skip pipes that are too far away
            if pipe.x + pipe.width < bird_x - 2:
                continue
            if pipe.x > bird_x + self.bird.width + 2:
                break  # Pipes are sorted, so we can stop

            if self.collision_detector.check_bird_pipe(self.bird, pipe):
                if self.bird.has_shield:
                    # Shield absorbs one hit
                    self.bird.has_shield = False
                    self.effect_manager.remove_effect_by_type('shield')
                else:
                    self.end_game()
                return

        # Check item collisions - only check nearby items
        for item in self.items[:]:
            # Skip items that are too far away (more than 10 units)
            if item.x < bird_x - 5 or item.x > bird_x + 15:
                continue

            if self.collision_detector.check_bird_item(self.bird, item):
                if isinstance(item, Coin):
                    # Collect coin
                    self.coins += 1
                    self.score += item.value
                    self.items.remove(item)
                elif isinstance(item, PowerUp):
                    # Apply power-up or debuff
                    self.effect_manager.add_effect(item.type)
                    self.items.remove(item)

    def render(self):
        """Render current game state."""
        if self.headless:
            return  # Skip rendering in headless mode

        if self.state == 'menu':
            self.render_menu()
        elif self.state == 'bot_menu':
            self.render_bot_menu()
        elif self.state == 'ready' or self.state == 'playing' or self.state == 'game_over':
            # Render game (for game_over, this shows the frozen last frame)
            self.render_game()
            # Overlay game over screen
            if self.state == 'game_over':
                self.renderer.render_game_over(self.score, self.coins, self.best_score)
            elif self.state == 'ready':
                self.renderer.render_ready()

        # Update display
        self.renderer.update()

    def render_menu(self):
        """Render main menu."""
        options = [
            'Start Game',
            'Play as Bot',
            'Exit'
        ]
        self.renderer.render_menu(options, self.selected_menu_option)

    def render_bot_menu(self):
        """Render bot selection menu."""
        options = [
            'Aggressive Bot (100%!)',
            'Reactive Bot (65%)',
            'Coin Collector Bot (A* 90%)'
        ]
        self.renderer.render_menu(options, self.selected_bot_option)

    def execute_menu_option(self, option_index):
        """Execute the selected menu option."""
        if option_index == 0:  # Start Game
            self.start_game(bot_mode=False)
        elif option_index == 1:  # Play as Bot
            self.state = 'bot_menu'
            self.selected_bot_option = 0
        elif option_index == 2:  # Exit
            self.running = False

    def execute_bot_selection(self, bot_index):
        """Execute the selected bot option."""
        bot_types = ['aggressive', 'reactive', 'coin_collector']
        self.bot_type = bot_types[bot_index]
        self.start_game(bot_mode=True)

    def render_game(self):
        """Render the game screen."""
        self.renderer.clear()

        # Draw ground
        self.renderer.draw_ground()

        # Draw pipes
        for pipe in self.pipes:
            self.renderer.draw_pipe(pipe)

        # Draw items (coins and power-ups)
        for item in self.items:
            if isinstance(item, Coin):
                self.renderer.draw_coin(item)
            elif isinstance(item, PowerUp):
                self.renderer.draw_powerup(item)

        # Draw bird
        self.renderer.draw_bird(self.bird)

        # Draw score
        self.renderer.draw_score(self.score, self.coins)

    def start_game(self, bot_mode=False):
        """Start a new game."""
        self.state = 'ready'
        self.game_started = False
        self.bot_mode = bot_mode

        # Reset FIRST (clears velocity, pipes, etc.)
        self.reset_game()

        # THEN create bot and jump
        if bot_mode:
            # Create bot based on selected type
            if self.bot_type == 'aggressive':
                self.bot = AggressiveBot(self)
            elif self.bot_type == 'reactive':
                self.bot = ReactiveBot(self)
            elif self.bot_type == 'coin_collector':
                self.bot = CoinCollectorBot(self)
            else:
                self.bot = AggressiveBot(self)  # Default fallback (100% success!)

            # Auto-start for bot - now jump will work correctly
            self.bird.jump()
            self.game_started = True
            self.state = 'playing'
        else:
            self.bot = None

    def reset_game(self):
        """Reset game to initial state."""
        self.bird.reset()
        self.score = 0
        self.coins = 0
        self.scroll_offset = 0
        self.scroll_speed = self.base_scroll_speed
        self.time_elapsed = 0
        self.paused = False
        self.game_over = False
        self.pipes = []
        self.items = []
        self.level_generator.reset()
        self.effect_manager.clear_all()

    def end_game(self):
        """End the current game."""
        self.state = 'game_over'
        if self.score > self.best_score:
            self.best_score = self.score
