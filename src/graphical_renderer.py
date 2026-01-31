import pygame


class GraphicalRenderer:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Flappy Bird")

        self.scale_x = width / 80
        self.scale_y = height / 24

        self.bg_color = (135, 206, 235)
        self.bird_color = (255, 200, 0)
        self.pipe_color = (113, 157, 161)
        self.ground_color = (139, 69, 19)
        self.coin_color = (100, 220, 220)
        self.text_color = (255, 255, 255)
        self.accent_color = (150, 230, 230)
        self.menu_bg = (30, 30, 30)
        self.menu_selected = (70, 130, 180)

        self.title_font = pygame.font.SysFont('quicksand', 64, bold=True)
        self.menu_font = pygame.font.SysFont('quicksand', 40, bold=True)
        self.score_font = pygame.font.SysFont('quicksand', 30, bold=True)
        self.small_font = pygame.font.SysFont('quicksand', 24, bold=False)

        self.debug_mode = False

        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bg_path = os.path.join(project_root, 'background.png')

        bg_img = pygame.image.load(bg_path)
        self.background_surface = pygame.transform.scale(bg_img, (self.width, self.height)).convert()
        del bg_img

        bird_path = os.path.join(project_root, 'bird.png')
        bird_img = pygame.image.load(bird_path).convert_alpha()
        self.bird_sprite = bird_img

        self.coin_symbol = self.menu_font.render('$', True, self.coin_color)
        self.powerup_plus = self.menu_font.render('+', True, (255, 255, 255))
        self.powerup_question = self.menu_font.render('?', True, (255, 255, 255))

    def clear(self):
        self.screen.blit(self.background_surface, (0, 0))

    def scale_pos(self, x, y):
        return (int(x * self.scale_x), int(y * self.scale_y))

    def scale_size(self, w, h):
        return (int(w * self.scale_x), int(h * self.scale_y))

    def draw_text_with_outline(self, text, font, color, outline_color, x, y, thickness=3):
        """Draw text with a thick outline for better readability."""
        text_surface = font.render(text, True, color)

        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx*dx + dy*dy <= thickness*thickness:
                    outline_surface = font.render(text, True, outline_color)
                    self.screen.blit(outline_surface, (x + dx, y + dy))

        self.screen.blit(text_surface, (x, y))

    def draw_debug_hitbox(self, hitbox, color, thickness=2):
        x, y = self.scale_pos(hitbox['x'], hitbox['y'])
        w, h = self.scale_size(hitbox['width'], hitbox['height'])
        pygame.draw.rect(self.screen, color, (x, y, w, h), thickness)

    def draw_bird(self, bird):
        original_w, original_h = self.scale_size(bird.width, bird.height)

        target_w = original_w * 3.5
        target_h = original_h * 3.5

        sprite_w = self.bird_sprite.get_width()
        sprite_h = self.bird_sprite.get_height()
        sprite_aspect = sprite_w / sprite_h

        target_aspect = target_w / target_h

        if sprite_aspect > target_aspect:
            scaled_w = int(target_w)
            scaled_h = int(target_w / sprite_aspect)
        else:
            scaled_h = int(target_h)
            scaled_w = int(target_h * sprite_aspect)

        # Use smoothscale for high-quality scaling
        scaled_sprite = pygame.transform.smoothscale(self.bird_sprite, (scaled_w, scaled_h))

        angle = 0
        if bird.velocity < -10:
            angle = 20
        elif bird.velocity > 10:
            angle = -20

        rotated_sprite = pygame.transform.rotate(scaled_sprite, angle)

        x, y = self.scale_pos(bird.x, bird.y)
        sprite_rect = rotated_sprite.get_rect(center=(x + original_w/2, y + original_h/2))

        self.screen.blit(rotated_sprite, sprite_rect)

        if self.debug_mode:
            self.draw_debug_hitbox(bird.get_hitbox(), (255, 0, 0), 3)

    def draw_pipe(self, pipe):
        pipe_screen_x = pipe.x * self.scale_x
        pipe_width_px = pipe.width * self.scale_x

        if pipe_screen_x + pipe_width_px < -10 or pipe_screen_x > self.width + 10:
            return

        pipe_fill = self.pipe_color
        pipe_border = (68, 94, 97)

        if pipe.y_top > 0:
            top_x, top_y = self.scale_pos(pipe.x, 0)
            top_w, top_h = self.scale_size(pipe.width, pipe.y_top)

            pygame.draw.rect(self.screen, pipe_fill, (top_x, top_y, top_w, top_h))
            pygame.draw.rect(self.screen, pipe_border, (top_x, top_y, top_w, top_h), 2)

            cap_x = top_x - 5
            cap_w = top_w + 10
            cap_y = top_y + top_h - 15
            pygame.draw.rect(self.screen, pipe_fill, (cap_x, cap_y, cap_w, 15))
            pygame.draw.rect(self.screen, pipe_border, (cap_x, cap_y, cap_w, 15), 2)

        if pipe.y_bottom < 24:
            bot_x, bot_y = self.scale_pos(pipe.x, pipe.y_bottom)
            bot_w, bot_h = self.scale_size(pipe.width, 24 - pipe.y_bottom)

            pygame.draw.rect(self.screen, pipe_fill, (bot_x, bot_y, bot_w, bot_h))
            pygame.draw.rect(self.screen, pipe_border, (bot_x, bot_y, bot_w, bot_h), 2)

            cap_x = bot_x - 5
            cap_w = bot_w + 10
            pygame.draw.rect(self.screen, pipe_fill, (cap_x, bot_y, cap_w, 15))
            pygame.draw.rect(self.screen, pipe_border, (cap_x, bot_y, cap_w, 15), 2)

        if self.debug_mode:
            self.draw_debug_hitbox(pipe.get_top_hitbox(), (0, 255, 0), 2)
            self.draw_debug_hitbox(pipe.get_bottom_hitbox(), (0, 255, 0), 2)

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
            self.draw_debug_hitbox(top_cap_box, (255, 255, 0), 2)
            self.draw_debug_hitbox(bottom_cap_box, (255, 255, 0), 2)

    def draw_coin(self, coin):
        coin_x_px = coin.x * self.scale_x
        if coin_x_px < -20 or coin_x_px > self.width + 20:
            return

        center_x, center_y = self.scale_pos(coin.x + 0.5, coin.y + 0.5)
        radius = int(1.8 * self.scale_x)

        if coin.is_gold:
            main_color = (255, 215, 0)
            shine_color = (255, 255, 150)
            border_color = (180, 140, 0)
        else:
            main_color = self.coin_color
            shine_color = (180, 250, 250)
            border_color = (80, 180, 180)

        pygame.draw.circle(self.screen, main_color, (center_x, center_y), radius)
        inner_radius = int(radius * 0.7)
        pygame.draw.circle(self.screen, shine_color, (center_x - radius//4, center_y - radius//4), inner_radius//2)
        pygame.draw.circle(self.screen, border_color, (center_x, center_y), radius, 2)

        text_rect = self.coin_symbol.get_rect(center=(center_x, center_y))
        self.screen.blit(self.coin_symbol, text_rect)

    def draw_powerup(self, powerup):
        powerup_x_px = powerup.x * self.scale_x
        if powerup_x_px < -20 or powerup_x_px > self.width + 20:
            return

        x, y = self.scale_pos(powerup.x, powerup.y)
        w, h = self.scale_size(3.0, 3.0)

        color_map = {
            'speed_boost': (100, 220, 255),
            'shield': (180, 140, 255),
            'slow_motion': (100, 255, 150),
            'gravity_down': (255, 100, 50),
            'reverse': (255, 80, 100)
        }
        color = color_map.get(powerup.type, (200, 200, 200))

        is_debuff = powerup.type in ['gravity_down', 'reverse']

        glow_color = tuple(min(255, c + 40) for c in color)
        pygame.draw.rect(self.screen, glow_color,
                        (x - 3, y - 3, w + 6, h + 6),
                        border_radius=8)

        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=6)

        border_color = (50, 50, 50) if is_debuff else (255, 255, 255)
        pygame.draw.rect(self.screen, border_color, (x, y, w, h), 3, border_radius=6)

        symbol_font = pygame.font.SysFont('quicksand', 42, bold=True)
        if is_debuff:
            symbol_text = symbol_font.render('!', True, (255, 255, 255))
        else:
            symbol_text = symbol_font.render('+', True, (255, 255, 255))

        shadow = symbol_font.render('!' if is_debuff else '+', True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(x + w // 2 + 1, y + h // 2 + 1))
        self.screen.blit(shadow, shadow_rect)

        text_rect = symbol_text.get_rect(center=(x + w // 2, y + h // 2))
        self.screen.blit(symbol_text, text_rect)

    def draw_ground(self):
        pass

    def draw_score(self, score, coins=0):
        self.draw_text_with_outline(
            f'Score: {score}',
            self.score_font,
            self.text_color,
            (0, 0, 0),
            10, 10,
            thickness=4
        )

        self.draw_text_with_outline(
            f'Coins: {coins}',
            self.score_font,
            self.coin_color,
            (0, 0, 0),
            10, 50,
            thickness=4
        )

    def render_menu(self, options, selected_index):
        self.clear()

        title_text = 'FLAPPY BIRD'
        title_surface = self.title_font.render(title_text, True, self.accent_color)
        title_rect = title_surface.get_rect(center=(self.width // 2, 100))

        for dx in range(-5, 6):
            for dy in range(-5, 6):
                if dx*dx + dy*dy <= 25:
                    outline = self.title_font.render(title_text, True, (0, 0, 0))
                    outline_rect = outline.get_rect(center=(self.width // 2 + dx, 100 + dy))
                    self.screen.blit(outline, outline_rect)

        self.screen.blit(title_surface, title_rect)

        y_offset = 250
        for i, option in enumerate(options):
            y_pos = y_offset + i * 60

            if i == selected_index:
                text = self.menu_font.render(option, True, self.accent_color)
                text_rect = text.get_rect(center=(self.width // 2, y_pos))
                bg_rect = text_rect.inflate(40, 20)
                pygame.draw.rect(self.screen, self.menu_selected, bg_rect, border_radius=10)

                text_surface = self.menu_font.render(option, True, self.accent_color)
                text_rect = text_surface.get_rect(center=(self.width // 2, y_pos))

                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        if dx*dx + dy*dy <= 9:
                            outline = self.menu_font.render(option, True, (0, 0, 0))
                            outline_rect = outline.get_rect(center=(self.width // 2 + dx, y_pos + dy))
                            self.screen.blit(outline, outline_rect)

                self.screen.blit(text_surface, text_rect)
            else:
                text_surface = self.menu_font.render(option, True, self.text_color)
                text_rect = text_surface.get_rect(center=(self.width // 2, y_pos))

                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if dx*dx + dy*dy <= 4:
                            outline = self.menu_font.render(option, True, (0, 0, 0))
                            outline_rect = outline.get_rect(center=(self.width // 2 + dx, y_pos + dy))
                            self.screen.blit(outline, outline_rect)

                self.screen.blit(text_surface, text_rect)

        inst_text = 'Use ↑↓ arrows and ENTER to select'
        inst_surface = self.small_font.render(inst_text, True, (200, 200, 200))
        inst_rect = inst_surface.get_rect(center=(self.width // 2, self.height - 50))

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx*dx + dy*dy <= 4:
                    outline = self.small_font.render(inst_text, True, (0, 0, 0))
                    outline_rect = outline.get_rect(center=(self.width // 2 + dx, self.height - 50 + dy))
                    self.screen.blit(outline, outline_rect)

        self.screen.blit(inst_surface, inst_rect)

    def render_game_over(self, score, coins, high_score):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = 'GAME OVER'
        game_over_surface = self.title_font.render(game_over_text, True, (255, 0, 0))
        go_rect = game_over_surface.get_rect(center=(self.width // 2, 150))

        for dx in range(-5, 6):
            for dy in range(-5, 6):
                if dx*dx + dy*dy <= 25:
                    outline = self.title_font.render(game_over_text, True, (0, 0, 0))
                    outline_rect = outline.get_rect(center=(self.width // 2 + dx, 150 + dy))
                    self.screen.blit(outline, outline_rect)

        self.screen.blit(game_over_surface, go_rect)

        y_offset = 250
        stats = [
            f'Score: {score}',
            f'Coins: {coins}',
            f'High Score: {high_score}'
        ]

        for i, stat in enumerate(stats):
            y_pos = y_offset + i * 50
            text_surface = self.menu_font.render(stat, True, self.text_color)
            rect = text_surface.get_rect(center=(self.width // 2, y_pos))

            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx*dx + dy*dy <= 9:
                        outline = self.menu_font.render(stat, True, (0, 0, 0))
                        outline_rect = outline.get_rect(center=(self.width // 2 + dx, y_pos + dy))
                        self.screen.blit(outline, outline_rect)

            self.screen.blit(text_surface, rect)

    def render_victory(self, score, coins, high_score):
        """Render victory screen when level is completed."""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 50, 0))  # Dark green overlay
        self.screen.blit(overlay, (0, 0))

        victory_text = 'VICTORY!'
        victory_surface = self.title_font.render(victory_text, True, (50, 255, 50))  # Bright green
        go_rect = victory_surface.get_rect(center=(self.width // 2, 150))

        # Outline effect
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                if dx*dx + dy*dy <= 25:
                    outline = self.title_font.render(victory_text, True, (0, 0, 0))
                    outline_rect = outline.get_rect(center=(self.width // 2 + dx, 150 + dy))
                    self.screen.blit(outline, outline_rect)

        self.screen.blit(victory_surface, go_rect)

        # Level completed message
        completed_text = 'LEVEL COMPLETED!'
        completed_surface = self.menu_font.render(completed_text, True, (200, 255, 200))
        completed_rect = completed_surface.get_rect(center=(self.width // 2, 200))
        self.screen.blit(completed_surface, completed_rect)

        # Stats
        y_offset = 250
        stats = [
            f'Final Score: {score}',
            f'Coins Collected: {coins}',
            f'High Score: {high_score}'
        ]

        for i, stat in enumerate(stats):
            y_pos = y_offset + i * 50
            text_surface = self.menu_font.render(stat, True, (200, 255, 200))
            rect = text_surface.get_rect(center=(self.width // 2, y_pos))

            # Outline
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx*dx + dy*dy <= 9:
                        outline = self.menu_font.render(stat, True, (0, 0, 0))
                        outline_rect = outline.get_rect(center=(self.width // 2 + dx, y_pos + dy))
                        self.screen.blit(outline, outline_rect)

            self.screen.blit(text_surface, rect)

        # Press ENTER prompt
        prompt_text = 'Press ENTER to continue'
        prompt_surface = self.small_font.render(prompt_text, True, (150, 255, 150))
        prompt_rect = prompt_surface.get_rect(center=(self.width // 2, 420))
        self.screen.blit(prompt_surface, prompt_rect)

        inst_text = 'Press SPACE to restart or ESC for menu'
        inst_surface = self.small_font.render(inst_text, True, (200, 200, 200))
        inst_rect = inst_surface.get_rect(center=(self.width // 2, self.height - 80))

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx*dx + dy*dy <= 4:
                    outline = self.small_font.render(inst_text, True, (0, 0, 0))
                    outline_rect = outline.get_rect(center=(self.width // 2 + dx, self.height - 80 + dy))
                    self.screen.blit(outline, outline_rect)

        self.screen.blit(inst_surface, inst_rect)

    def render_ready(self):
        ready_text = 'Press SPACE to start!'
        text_surface = self.menu_font.render(ready_text, True, (255, 255, 255))
        rect = text_surface.get_rect(center=(self.width // 2, 100))

        for dx in range(-4, 5):
            for dy in range(-4, 5):
                if dx*dx + dy*dy <= 16:
                    outline = self.menu_font.render(ready_text, True, (0, 0, 0))
                    outline_rect = outline.get_rect(center=(self.width // 2 + dx, 100 + dy))
                    self.screen.blit(outline, outline_rect)

        self.screen.blit(text_surface, rect)

    def update(self):
        pygame.display.flip()

    def close(self):
        pygame.quit()
