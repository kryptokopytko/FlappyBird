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
from ai.flat_bot import FlatBot
from utils.config import GAME_CONFIG

# Display constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Difficulty progression constants
SPEED_INCREASE_RATE = 0.15
MAX_SPEED_MULTIPLIER = 1.5

# Scoring constants
SCORE_PER_PIPE = 10

# Collision check ranges
PIPE_COLLISION_LOOKAHEAD = 2
ITEM_CHECK_MIN_OFFSET = -5
ITEM_CHECK_MAX_OFFSET = 15

# Menu constants
NUM_MAIN_MENU_OPTIONS = 3
NUM_BOT_MENU_OPTIONS = 4


class Game:
    def __init__(self, headless=False):
        self.headless = headless

        if not headless:
            self.renderer = GraphicalRenderer(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
            self.clock = pygame.time.Clock()
        else:
            self.renderer = None
            self.clock = None

        self.bird = Bird()
        self.level_generator = LevelGenerator(difficulty=GAME_CONFIG["level"]["difficulty"])
        self.collision_detector = CollisionDetector()
        self.effect_manager = EffectManager(self)

        self.width = GAME_CONFIG["screen"]["width"]
        self.height = GAME_CONFIG["screen"]["height"]
        self.fps = GAME_CONFIG["screen"]["fps"]
        self.dt = 1.0 / self.fps

        self.running = True
        self.paused = False
        self.game_over = False
        self.score = 0
        self.best_score = 0
        self.coins = 0

        self.scroll_offset = 0
        self.scroll_speed = GAME_CONFIG["level"]["scroll_speed"]
        self.base_scroll_speed = GAME_CONFIG["level"]["scroll_speed"]
        self.speed_increase_rate = SPEED_INCREASE_RATE
        self.max_scroll_speed = self.base_scroll_speed * MAX_SPEED_MULTIPLIER
        self.time_elapsed = 0

        self.pipes = []
        self.items = []

        self.state = "menu"
        self.selected_menu_option = 0
        self.selected_bot_option = 0
        self.game_started = False

        self.bot_mode = False
        self.bot = None
        self.bot_type = "aggressive"

    def run(self):
        if self.headless:
            import time

            while self.running and self.state == "playing":
                self.update(self.dt)
                time.sleep(self.dt)
        else:
            while self.running:
                self.handle_input()

                if (self.state == "ready") or (
                    self.state == "playing" and not self.paused
                ):
                    self.update(self.dt)

                self.render()
                self.clock.tick(self.fps)

            self.renderer.close()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if self._handle_escape_key(event):
                    return

                if self.state == "menu":
                    self._handle_menu_input(event)
                elif self.state == "bot_menu":
                    self._handle_bot_menu_input(event)
                elif self.state == "ready":
                    self._handle_ready_input(event)
                elif self.state == "playing":
                    self._handle_playing_input(event)
                elif self.state == "game_over":
                    self._handle_game_over_input(event)
                elif self.state == "victory":
                    self._handle_victory_input(event)

    def _handle_escape_key(self, event):
        if event.key == pygame.K_ESCAPE:
            if self.state in ("playing", "ready"):
                self.state = "menu"
                self.reset_game()
            else:
                self.running = False
            return True
        return False

    def _handle_menu_input(self, event):
        if event.key == pygame.K_UP:
            self.selected_menu_option = (
                self.selected_menu_option - 1
            ) % NUM_MAIN_MENU_OPTIONS
        elif event.key == pygame.K_DOWN:
            self.selected_menu_option = (
                self.selected_menu_option + 1
            ) % NUM_MAIN_MENU_OPTIONS
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.execute_menu_option(self.selected_menu_option)
        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
            option_index = event.key - pygame.K_1
            self.selected_menu_option = option_index
            self.execute_menu_option(option_index)

    def _handle_bot_menu_input(self, event):
        if event.key == pygame.K_UP:
            self.selected_bot_option = (
                self.selected_bot_option - 1
            ) % NUM_BOT_MENU_OPTIONS
        elif event.key == pygame.K_DOWN:
            self.selected_bot_option = (
                self.selected_bot_option + 1
            ) % NUM_BOT_MENU_OPTIONS
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.execute_bot_selection(self.selected_bot_option)
        elif event.key == pygame.K_ESCAPE:
            self.state = "menu"
            self.selected_bot_option = 0
        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
            option_index = event.key - pygame.K_1
            self.selected_bot_option = option_index
            self.execute_bot_selection(option_index)

    def _handle_ready_input(self, event):
        if event.key == pygame.K_SPACE:
            self.bird.jump()
            self.game_started = True
            self.state = "playing"

    def _handle_playing_input(self, event):
        if event.key == pygame.K_SPACE:
            if not self.paused:
                self.bird.jump()
        elif event.key == pygame.K_p:
            self.paused = not self.paused
        elif event.key == pygame.K_r:
            self.start_game(bot_mode=self.bot_mode)
        elif event.key == pygame.K_d:
            self.renderer.debug_mode = not self.renderer.debug_mode

    def _handle_game_over_input(self, event):
        if event.key == pygame.K_SPACE:
            self.start_game(bot_mode=self.bot_mode)
        elif event.key == pygame.K_ESCAPE:
            self.state = "menu"
            self.reset_game()

    def _handle_victory_input(self, event):
        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self.state = "menu"
            self.reset_game()
        elif event.key == pygame.K_ESCAPE:
            self.state = "menu"
            self.reset_game()

    def update(self, dt):
        if self.bot_mode and self.bot and self.game_started:
            if self.bot.decide_action():
                self.bird.jump()

        self.effect_manager.update(dt)

        if self.game_started:
            self.bird.update(dt)

            self.time_elapsed += dt
            self.scroll_speed = min(
                self.base_scroll_speed + (self.time_elapsed * self.speed_increase_rate),
                self.max_scroll_speed,
            )

            self.scroll_offset += self.scroll_speed * dt

            # Check if level completed
            if hasattr(self.level_generator, 'concrete_level'):
                if self.scroll_offset >= self.level_generator.concrete_level.length:
                    self.win_game()
                    return

            for pipe in self.pipes:
                pipe.update(self.scroll_speed, dt)

                if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                    pipe.passed = True
                    self.score += SCORE_PER_PIPE

            self.pipes = [p for p in self.pipes if not p.is_offscreen()]

            if self.level_generator.should_generate_pipe(self.pipes):
                new_pipe = self.level_generator.generate_pipe()
                self.pipes.append(new_pipe)
                new_items = self.level_generator.generate_items_for_pipe(new_pipe)
                self.items.extend(new_items)

            for item in self.items:
                item.update(self.scroll_speed, dt)

            self.items = [
                item
                for item in self.items
                if not item.is_offscreen() and not item.collected
            ]

            self.check_collisions()

            if self.bird.is_out_of_bounds(self.height):
                ground_level = self.height - self.bird.height - 1
                self.bird.y = max(0, min(self.bird.y, ground_level))
                self.end_game()

    def check_collisions(self):
        bird_x = self.bird.x

        for pipe in self.pipes:
            if pipe.x + pipe.width < bird_x - PIPE_COLLISION_LOOKAHEAD:
                continue
            if pipe.x > bird_x + self.bird.width + PIPE_COLLISION_LOOKAHEAD:
                break

            if self.collision_detector.check_bird_pipe(self.bird, pipe):
                if self.bird.has_shield:
                    self.bird.has_shield = False
                    self.effect_manager.remove_effect_by_type("shield")
                else:
                    self.end_game()
                return

        for item in self.items:
            if (
                item.x < bird_x + ITEM_CHECK_MIN_OFFSET
                or item.x > bird_x + ITEM_CHECK_MAX_OFFSET
            ):
                continue

            if self.collision_detector.check_bird_item(self.bird, item):
                if isinstance(item, Coin):
                    self.coins += 1
                    self.score += item.value
                    item.collected = True
                elif isinstance(item, PowerUp):
                    self.effect_manager.add_effect(item.type)
                    item.collected = True

    def render(self):
        if self.headless:
            return

        if self.state == "menu":
            self.render_menu()
        elif self.state == "bot_menu":
            self.render_bot_menu()
        elif (
            self.state == "ready"
            or self.state == "playing"
            or self.state == "game_over"
            or self.state == "victory"
        ):
            self.render_game()
            if self.state == "game_over":
                self.renderer.render_game_over(self.score, self.coins, self.best_score)
            elif self.state == "victory":
                self.renderer.render_victory(self.score, self.coins, self.best_score)
            elif self.state == "ready":
                self.renderer.render_ready()

        self.renderer.update()

    def render_menu(self):
        options = ["Start Game", "Play as Bot", "Exit"]
        self.renderer.render_menu(options, self.selected_menu_option)

    def render_bot_menu(self):
        options = ["Aggressive Bot", "Reactive Bot", "Coin Collector Bot (A*)"]
        self.renderer.render_menu(options, self.selected_bot_option)

    def execute_menu_option(self, option_index):
        if option_index == 0:
            self.start_game(bot_mode=False)
        elif option_index == 1:
            self.state = "bot_menu"
            self.selected_bot_option = 0
        elif option_index == 2:
            self.running = False

    def execute_bot_selection(self, bot_index):
        bot_types = ["aggressive", "reactive", "coin_collector"]
        self.bot_type = bot_types[bot_index]
        self.start_game(bot_mode=True)

    def render_game(self):
        self.renderer.clear()
        self.renderer.draw_ground()

        for pipe in self.pipes:
            self.renderer.draw_pipe(pipe)

        for item in self.items:
            if isinstance(item, Coin):
                self.renderer.draw_coin(item)
            elif isinstance(item, PowerUp):
                self.renderer.draw_powerup(item)

        self.renderer.draw_bird(self.bird)
        self.renderer.draw_score(self.score, self.coins)

    def start_game(self, bot_mode=False):
        self.state = "ready"
        self.game_started = False
        self.bot_mode = bot_mode
        self.reset_game()

        if bot_mode:
            if self.bot_type == "aggressive":
                self.bot = AggressiveBot(self)
            elif self.bot_type == "reactive":
                self.bot = ReactiveBot(self)
            elif self.bot_type == "coin_collector":
                self.bot = CoinCollectorBot(self)
            elif self.bot_type == "flat":
                self.bot = FlatBot(self)
            else:
                self.bot = AggressiveBot(self)

            self.bird.jump()
            self.game_started = True
            self.state = "playing"
        else:
            self.bot = None

    def reset_game(self):
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
        self.state = "game_over"
        if self.score > self.best_score:
            self.best_score = self.score

    def win_game(self):
        """Called when player completes the level."""
        self.state = "victory"
        if self.score > self.best_score:
            self.best_score = self.score
