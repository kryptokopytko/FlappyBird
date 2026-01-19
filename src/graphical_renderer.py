"""
Graphical renderer using Pygame for vector-based rendering.
"""
import pygame


class GraphicalRenderer:
    """Handles all rendering using Pygame with vector graphics."""

    def __init__(self, width=800, height=600):
        """Initialize the graphical renderer.

        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Flappy Bird")

        # Scale factors to convert game coordinates to pixels
        # Game uses 80x24 coordinate system
        self.scale_x = width / 80
        self.scale_y = height / 24

        # Colors (RGB tuples)
        self.bg_color = (135, 206, 235)  # Sky blue
        self.bird_color = (255, 200, 0)  # Yellow
        self.pipe_color = (50, 205, 50)  # Green
        self.ground_color = (139, 69, 19)  # Brown
        self.coin_color = (255, 215, 0)  # Gold
        self.text_color = (255, 255, 255)  # White
        self.menu_bg = (30, 30, 30)  # Dark gray
        self.menu_selected = (70, 130, 180)  # Steel blue

        # Fonts
        self.title_font = pygame.font.Font(None, 74)
        self.menu_font = pygame.font.Font(None, 48)
        self.score_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)

        # DEBUG mode flag
        self.debug_mode = False

        # Pre-render static background elements
        self.background_surface = self._create_background()

    def _create_background(self):
        """Create static background with mountains and clouds (rendered once)."""
        bg_surface = pygame.Surface((self.width, self.height))
        bg_surface.fill(self.bg_color)

        # Draw clouds first (behind mountains)
        cloud_color = (255, 255, 255, 180)
        cloud_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Static clouds at fixed positions
        clouds = [
            {'x': 100, 'y': 90, 'type': 'fluffy', 'size': 1.0},
            {'x': 650, 'y': 75, 'type': 'small', 'size': 0.9},
            {'x': 380, 'y': 130, 'type': 'elongated', 'size': 1.0},
            {'x': 220, 'y': 165, 'type': 'small', 'size': 0.85},
            {'x': 530, 'y': 145, 'type': 'wispy', 'size': 1.0},
        ]

        for cloud in clouds:
            cx = cloud['x']
            cy = cloud['y']
            s = cloud['size']

            if cloud['type'] == 'fluffy':
                # Large, round fluffy cloud
                r = int(32 * s)
                pygame.draw.circle(cloud_surface, cloud_color, (cx + int(35*s), cy), r)
                pygame.draw.circle(cloud_surface, cloud_color, (cx + int(10*s), cy + int(5*s)), int(28*s))
                pygame.draw.circle(cloud_surface, cloud_color, (cx + int(60*s), cy - int(10*s)), int(30*s))
                pygame.draw.circle(cloud_surface, cloud_color, (cx + int(50*s), cy + int(18*s)), int(25*s))

            elif cloud['type'] == 'elongated':
                # Long, stretched cloud
                w, h = int(140 * s), int(28 * s)
                pygame.draw.ellipse(cloud_surface, cloud_color, (cx, cy - h//2, w, h))
                pygame.draw.circle(cloud_surface, cloud_color, (cx + int(15*s), cy - int(5*s)), int(18*s))
                pygame.draw.circle(cloud_surface, cloud_color, (cx + int(120*s), cy + int(2*s)), int(17*s))

            elif cloud['type'] == 'small':
                # Small puffy cloud
                r = int(22 * s)
                pygame.draw.circle(cloud_surface, cloud_color, (cx + int(20*s), cy), r)
                pygame.draw.circle(cloud_surface, cloud_color, (cx, cy + int(3*s)), int(18*s))
                pygame.draw.circle(cloud_surface, cloud_color, (cx + int(38*s), cy - int(5*s)), int(20*s))

            elif cloud['type'] == 'wispy':
                # Thin, wispy cloud
                w1, h1 = int(95 * s), int(14 * s)
                pygame.draw.ellipse(cloud_surface, cloud_color, (cx, cy - h1//2, w1, h1))
                pygame.draw.circle(cloud_surface, cloud_color, (cx + int(12*s), cy), int(11*s))

        bg_surface.blit(cloud_surface, (0, 0))

        # Mountain colors
        mountain_color = (80, 100, 120)
        snow_color = (240, 248, 255)
        snow_shadow = (200, 210, 220)
        shadow_color = (60, 75, 90)

        # Define multiple mountain ranges at different heights
        mountains = [
            {'base_x': 0, 'peak_offset': 200, 'peak_y': 280, 'width': 400},
            {'base_x': 350, 'peak_offset': 200, 'peak_y': 320, 'width': 350},
            {'base_x': 650, 'peak_offset': 150, 'peak_y': 300, 'width': 350},
        ]

        for mtn in mountains:
            base_x = mtn['base_x']
            peak_offset = mtn['peak_offset']
            peak_y = mtn['peak_y']
            width = mtn['width']
            peak_x = base_x + peak_offset

            # Mountain body
            points = [
                (base_x, self.height),
                (peak_x - 50, peak_y + 80),
                (peak_x, peak_y),
                (peak_x + 30, peak_y + 60),
                (base_x + width, self.height)
            ]
            pygame.draw.polygon(bg_surface, mountain_color, points)

            # Shadow side (left side darker)
            shadow_points = [
                (base_x, self.height),
                (peak_x - 50, peak_y + 80),
                (peak_x - 10, peak_y + 20),
                (peak_x, peak_y),
                (peak_x - 25, self.height)
            ]
            pygame.draw.polygon(bg_surface, shadow_color, shadow_points)

            # Snow cap
            snow_line_y = peak_y + 55
            snow_points = [
                (peak_x - 28, snow_line_y),
                (peak_x - 5, peak_y + 15),
                (peak_x, peak_y),
                (peak_x + 15, peak_y + 20),
                (peak_x + 18, snow_line_y + 8)
            ]
            pygame.draw.polygon(bg_surface, snow_color, snow_points)

            # Snow cap shadow (left side)
            snow_shadow_points = [
                (peak_x - 28, snow_line_y),
                (peak_x - 5, peak_y + 15),
                (peak_x, peak_y),
                (peak_x - 3, snow_line_y - 10)
            ]
            pygame.draw.polygon(bg_surface, snow_shadow, snow_shadow_points)

        return bg_surface

    def clear(self):
        """Clear the screen with background (cached static background)."""
        # Just blit the pre-rendered background - super fast!
        self.screen.blit(self.background_surface, (0, 0))

    def scale_pos(self, x, y):
        """Convert game coordinates to pixel coordinates.

        Args:
            x: Game x coordinate (0-80)
            y: Game y coordinate (0-24)

        Returns:
            Tuple of (pixel_x, pixel_y)
        """
        return (int(x * self.scale_x), int(y * self.scale_y))

    def scale_size(self, w, h):
        """Convert game dimensions to pixel dimensions.

        Args:
            w: Game width
            h: Game height

        Returns:
            Tuple of (pixel_width, pixel_height)
        """
        return (int(w * self.scale_x), int(h * self.scale_y))

    def draw_debug_hitbox(self, hitbox, color, thickness=2):
        """Draw collision hitbox for debugging.

        Args:
            hitbox: Dict with 'x', 'y', 'width', 'height'
            color: RGB tuple for the border color
            thickness: Line thickness in pixels
        """
        x, y = self.scale_pos(hitbox['x'], hitbox['y'])
        w, h = self.scale_size(hitbox['width'], hitbox['height'])
        pygame.draw.rect(self.screen, color, (x, y, w, h), thickness)

    def draw_bird(self, bird):
        """Draw a cute detailed bird.

        Args:
            bird: Bird entity
        """
        # Bird center position
        center_x, center_y = self.scale_pos(bird.x + bird.width / 2, bird.y + bird.height / 2)
        radius = int((bird.width * self.scale_x + bird.height * self.scale_y) / 4)

        # Draw wing (behind body) - darker shade
        wing_offset = int(radius * 0.6)
        wing_y = center_y + radius // 4
        # Animate wing flapping based on velocity
        if bird.velocity < 0:  # Going up
            wing_points = [
                (center_x - wing_offset, wing_y),
                (center_x - wing_offset - 8, wing_y - 12),
                (center_x - wing_offset + 8, wing_y - 8)
            ]
        else:  # Falling
            wing_points = [
                (center_x - wing_offset, wing_y),
                (center_x - wing_offset - 8, wing_y + 8),
                (center_x - wing_offset + 8, wing_y + 12)
            ]
        pygame.draw.polygon(self.screen, (220, 170, 0), wing_points)

        # Draw body - main circle (bright yellow)
        pygame.draw.circle(self.screen, (255, 220, 50), (center_x, center_y), radius)

        # Draw belly - lighter circle
        belly_radius = int(radius * 0.6)
        belly_y = center_y + radius // 4
        pygame.draw.circle(self.screen, (255, 240, 150), (center_x, belly_y), belly_radius)

        # Draw body outline
        pygame.draw.circle(self.screen, (200, 150, 0), (center_x, center_y), radius, 3)

        # Draw beak (orange triangle pointing right)
        beak_size = radius // 2
        beak_points = [
            (center_x + radius - 5, center_y),
            (center_x + radius + beak_size, center_y - 6),
            (center_x + radius + beak_size, center_y + 6)
        ]
        pygame.draw.polygon(self.screen, (255, 140, 0), beak_points)
        # Beak outline
        pygame.draw.polygon(self.screen, (200, 100, 0), beak_points, 2)

        # Draw eye - white background
        eye_x = center_x + radius // 3
        eye_y = center_y - radius // 3
        eye_size = radius // 3
        pygame.draw.circle(self.screen, (255, 255, 255), (eye_x, eye_y), eye_size)
        # Black pupil
        pupil_size = eye_size // 2
        pygame.draw.circle(self.screen, (0, 0, 0), (eye_x + 2, eye_y), pupil_size)
        # White highlight
        highlight_size = pupil_size // 3
        pygame.draw.circle(self.screen, (255, 255, 255), (eye_x + 4, eye_y - 2), highlight_size)

        # Draw eyebrow (always visible - determined look)
        eyebrow_start = (eye_x - eye_size, eye_y - eye_size - 3)
        eyebrow_end = (eye_x + eye_size + 2, eye_y - eye_size - 1)
        pygame.draw.line(self.screen, (200, 150, 0), eyebrow_start, eyebrow_end, 3)

        # Draw tail feathers
        tail_x = center_x - radius
        tail_points = [
            (tail_x, center_y - 8),
            (tail_x - 12, center_y - 12),
            (tail_x - 8, center_y)
        ]
        pygame.draw.polygon(self.screen, (220, 180, 40), tail_points)
        tail_points2 = [
            (tail_x, center_y),
            (tail_x - 12, center_y),
            (tail_x - 8, center_y + 8)
        ]
        pygame.draw.polygon(self.screen, (200, 160, 30), tail_points2)
        # Tail outlines
        pygame.draw.polygon(self.screen, (180, 130, 0), tail_points, 2)
        pygame.draw.polygon(self.screen, (180, 130, 0), tail_points2, 2)

        # DEBUG: Draw actual hitbox
        if self.debug_mode:
            self.draw_debug_hitbox(bird.get_hitbox(), (255, 0, 0), 3)  # Red

    def draw_pipe(self, pipe):
        """Draw a pipe as rectangles.

        Args:
            pipe: Pipe entity
        """
        # Cache colors as locals
        pipe_fill = self.pipe_color
        pipe_border = (34, 139, 34)

        # Top pipe
        if pipe.y_top > 0:
            top_x, top_y = self.scale_pos(pipe.x, 0)
            top_w, top_h = self.scale_size(pipe.width, pipe.y_top)

            # Draw filled rect with border in one call
            pygame.draw.rect(self.screen, pipe_fill, (top_x, top_y, top_w, top_h))
            pygame.draw.rect(self.screen, pipe_border, (top_x, top_y, top_w, top_h), 3)

            # Pipe cap (slightly wider) - combine fill and border
            cap_x = top_x - 5
            cap_w = top_w + 10
            cap_y = top_y + top_h - 15
            pygame.draw.rect(self.screen, pipe_fill, (cap_x, cap_y, cap_w, 15))
            pygame.draw.rect(self.screen, pipe_border, (cap_x, cap_y, cap_w, 15), 3)

        # Bottom pipe
        if pipe.y_bottom < 24:
            bot_x, bot_y = self.scale_pos(pipe.x, pipe.y_bottom)
            bot_w, bot_h = self.scale_size(pipe.width, 24 - pipe.y_bottom)

            # Draw filled rect with border
            pygame.draw.rect(self.screen, pipe_fill, (bot_x, bot_y, bot_w, bot_h))
            pygame.draw.rect(self.screen, pipe_border, (bot_x, bot_y, bot_w, bot_h), 3)

            # Pipe cap (slightly wider)
            cap_x = bot_x - 5
            cap_w = bot_w + 10
            pygame.draw.rect(self.screen, pipe_fill, (cap_x, bot_y, cap_w, 15))
            pygame.draw.rect(self.screen, pipe_border, (cap_x, bot_y, cap_w, 15), 3)

        # DEBUG: Draw actual hitboxes
        if self.debug_mode:
            self.draw_debug_hitbox(pipe.get_top_hitbox(), (0, 255, 0), 2)  # Green
            self.draw_debug_hitbox(pipe.get_bottom_hitbox(), (0, 255, 0), 2)  # Green

            # Draw cap hitboxes (from physics.py check_bird_pipe)
            top_cap_box = {
                'x': pipe.x + 1,
                'y': max(1, pipe.y_top - 2),
                'width': pipe.width - 2,
                'height': 2
            }
            bottom_cap_box = {
                'x': pipe.x + 1,
                'y': pipe.y_bottom,
                'width': pipe.width - 2,
                'height': 2
            }
            self.draw_debug_hitbox(top_cap_box, (255, 255, 0), 2)  # Yellow
            self.draw_debug_hitbox(bottom_cap_box, (255, 255, 0), 2)  # Yellow

    def draw_coin(self, coin):
        """Draw a coin as a large circle.

        Args:
            coin: Coin entity
        """
        center_x, center_y = self.scale_pos(coin.x + 0.5, coin.y + 0.5)
        radius = int(1.8 * self.scale_x)  # Even bigger coins (was 1.2)

        # Draw coin body with gradient effect
        pygame.draw.circle(self.screen, self.coin_color, (center_x, center_y), radius)
        # Inner circle for shine effect
        inner_radius = int(radius * 0.7)
        pygame.draw.circle(self.screen, (255, 235, 100), (center_x - radius//4, center_y - radius//4), inner_radius//2)
        # Outer border
        pygame.draw.circle(self.screen, (218, 165, 32), (center_x, center_y), radius, 3)

        # Draw $ symbol (bigger font)
        text = self.menu_font.render('$', True, (218, 165, 32))
        text_rect = text.get_rect(center=(center_x, center_y))
        self.screen.blit(text, text_rect)

    def draw_powerup(self, powerup):
        """Draw a powerup as a colored square.

        Args:
            powerup: Powerup entity
        """
        x, y = self.scale_pos(powerup.x, powerup.y)
        w, h = self.scale_size(2.5, 2.5)  # Bigger power-ups (was 1.5)

        # Color based on type
        color_map = {
            'speed_boost': (0, 191, 255),  # Deep sky blue
            'shield': (147, 112, 219),      # Medium purple
            'slow_motion': (50, 205, 50),   # Lime green
            'gravity_down': (255, 69, 0),   # Red-orange (debuff)
            'reverse': (220, 20, 60)        # Crimson (debuff)
        }
        color = color_map.get(powerup.type, (200, 200, 200))

        # Draw square with rounded corners effect
        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=5)
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, w, h), 2, border_radius=5)

        # Draw symbol based on type
        symbol = '?' if powerup.type in ['gravity_down', 'reverse'] else '+'
        text = self.menu_font.render(symbol, True, (255, 255, 255))
        text_rect = text.get_rect(center=(x + w // 2, y + h // 2))
        self.screen.blit(text, text_rect)

    def draw_ground(self):
        """Draw the ground at the bottom."""
        # No visible ground - just sky
        pass

    def draw_score(self, score, coins=0):
        """Draw the score and coin count.

        Args:
            score: Current score
            coins: Number of coins collected
        """
        # Score
        score_text = self.score_font.render(f'Score: {score}', True, self.text_color)
        score_rect = score_text.get_rect(topleft=(10, 10))

        # Add shadow for better visibility
        shadow = self.score_font.render(f'Score: {score}', True, (0, 0, 0))
        shadow_rect = shadow.get_rect(topleft=(12, 12))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(score_text, score_rect)

        # Coins
        coins_text = self.score_font.render(f'Coins: {coins}', True, self.coin_color)
        coins_rect = coins_text.get_rect(topleft=(10, 50))

        shadow = self.score_font.render(f'Coins: {coins}', True, (0, 0, 0))
        shadow_rect = shadow.get_rect(topleft=(12, 52))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(coins_text, coins_rect)

    def render_menu(self, options, selected_index):
        """Render the main menu.

        Args:
            options: List of menu option strings
            selected_index: Index of currently selected option
        """
        self.clear()

        # Draw title
        title = self.title_font.render('FLAPPY BIRD', True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.width // 2, 100))

        # Title shadow
        shadow = self.title_font.render('FLAPPY BIRD', True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(self.width // 2 + 3, 103))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(title, title_rect)

        # Draw menu options
        y_offset = 250
        for i, option in enumerate(options):
            if i == selected_index:
                # Highlight selected option
                color = (255, 215, 0)
                # Draw background rectangle
                text = self.menu_font.render(option, True, color)
                text_rect = text.get_rect(center=(self.width // 2, y_offset + i * 60))
                bg_rect = text_rect.inflate(40, 20)
                pygame.draw.rect(self.screen, self.menu_selected, bg_rect, border_radius=10)
            else:
                color = self.text_color
                text = self.menu_font.render(option, True, color)
                text_rect = text.get_rect(center=(self.width // 2, y_offset + i * 60))

            self.screen.blit(text, text_rect)

        # Draw instructions
        instructions = self.small_font.render('Use ↑↓ arrows and ENTER to select', True, (200, 200, 200))
        inst_rect = instructions.get_rect(center=(self.width // 2, self.height - 50))
        self.screen.blit(instructions, inst_rect)

    def render_game_over(self, score, coins, high_score):
        """Render the game over overlay.

        Args:
            score: Final score
            coins: Total coins collected
            high_score: High score
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over = self.title_font.render('GAME OVER', True, (255, 0, 0))
        go_rect = game_over.get_rect(center=(self.width // 2, 150))
        self.screen.blit(game_over, go_rect)

        # Stats
        y_offset = 250
        stats = [
            f'Score: {score}',
            f'Coins: {coins}',
            f'High Score: {high_score}'
        ]

        for i, stat in enumerate(stats):
            text = self.menu_font.render(stat, True, self.text_color)
            rect = text.get_rect(center=(self.width // 2, y_offset + i * 50))
            self.screen.blit(text, rect)

        # Instructions
        instructions = self.small_font.render('Press SPACE to restart or ESC for menu', True, (200, 200, 200))
        inst_rect = instructions.get_rect(center=(self.width // 2, self.height - 80))
        self.screen.blit(instructions, inst_rect)

    def render_ready(self):
        """Render the ready state message."""
        text = self.menu_font.render('Press SPACE to start!', True, (255, 255, 255))
        rect = text.get_rect(center=(self.width // 2, 100))

        # Draw with shadow
        shadow = self.menu_font.render('Press SPACE to start!', True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(self.width // 2 + 2, 102))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(text, rect)

    def update(self):
        """Update the display."""
        pygame.display.flip()

    def close(self):
        """Clean up and close pygame."""
        pygame.quit()
