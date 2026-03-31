import pygame
import sys
import random
from openscreen import StartupScreen
from Environment import Environment
from constant import *

class EndGameScreen:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set screen size
        pygame.display.set_caption("End Game")
        pygame.mixer.music.stop()  # Stop any previous music
        pygame.mixer.music.load("sounds/gameover.mp3")
        pygame.mixer.music.play(-1)  # Play game over music
        self.colorretry = COLOR_YELLOW  # Yellow color for retry button
        self.colormainmenu = (255, 50, 50)  # Red color for main menu button
        pygame.mixer.music.set_volume(ENDGAME_VOLUME)  # Set volume
        self.font = pygame.font.Font(None, ENDGAME_FONT_SIZE)
        self.font_stats = pygame.font.Font(None, ENDGAME_STATS_FONT_SIZE)
        self.small_font = pygame.font.Font(None, ENDGAME_BUTTON_FONT_SIZE)
        self.background_color = ENDGAME_BACKGROUND_COLOR  # Dark blue background
        self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(NUM_STARS)]  # Generate stars correctly
        self.retry_hover = False
        self.main_menu_hover = False

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        # Update hover states dynamically
        self.retry_hover = self.retry_button.collidepoint(mouse_pos)
        self.main_menu_hover = self.main_menu_button.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                if self.retry_button.collidepoint(mouse_pos):
                    return "retry"
                elif self.main_menu_button.collidepoint(mouse_pos):
                    return "main_menu"

        return None

    def display(self):
        self.screen.fill(self.background_color)  # Dark blue background

        # Move stars
        for i, star in enumerate(self.stars):
            self.stars[i] = (star[0] - 1 if star[0] > 0 else SCREEN_WIDTH, star[1])

        # Draw stars
        for star in self.stars:
            pygame.draw.circle(self.screen, COLOR_WHITE, star, 2)

        # Display "Game Over" text with shadow
        shadow_offset = SHADOW_OFFSET
        shadow_color = COLOR_BLACK
        game_over_text_shadow = self.font.render("Game Over", True, shadow_color)
        game_over_rect_shadow = game_over_text_shadow.get_rect(center=(self.screen.get_width() // 2 + shadow_offset, self.screen.get_height() // 3 + shadow_offset))
        self.screen.blit(game_over_text_shadow, game_over_rect_shadow)

        game_over_text = self.font.render("Game Over", True, COLOR_RED)
        game_over_rect = game_over_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 3))
        self.screen.blit(game_over_text, game_over_rect)
        game_score = self.font_stats.render(f"score: {Environment.score} points", True, COLOR_WHITE)
        game_score_rect = game_score.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 3 + 55))
        self.screen.blit(game_score, game_score_rect)
        game_time = self.font_stats.render(f"time: {Environment.time} seconds", True, COLOR_WHITE)
        game_time_rect = game_time.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 3 + 85))
        self.screen.blit(game_time, game_time_rect)

        # Display buttons with hover effect and updated design
        self.retry_button = pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() // 2, ENDGAME_BUTTON_WIDTH, ENDGAME_BUTTON_HEIGHT)
        self.main_menu_button = pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 + ENDGAME_BUTTON_SPACING, ENDGAME_BUTTON_WIDTH, ENDGAME_BUTTON_HEIGHT)

        # Retry button
        retry_color = COLOR_RED if self.retry_hover else COLOR_YELLOW
        pygame.draw.rect(self.screen, COLOR_BLACK, self.retry_button.inflate(10, 10), border_radius=10)  # Shadow
        pygame.draw.rect(self.screen, retry_color, self.retry_button, border_radius=10)  # Button
        retry_text = self.small_font.render("Retry", True, COLOR_BLACK)
        retry_text_rect = retry_text.get_rect(center=self.retry_button.center)
        self.screen.blit(retry_text, retry_text_rect)

        # Main Menu button
        main_menu_color = COLOR_RED if self.main_menu_hover else COLOR_YELLOW
        pygame.draw.rect(self.screen, COLOR_BLACK, self.main_menu_button.inflate(10, 10), border_radius=10)  # Shadow
        pygame.draw.rect(self.screen, main_menu_color, self.main_menu_button, border_radius=10)  # Button
        main_menu_text = self.small_font.render("Main Menu", True, COLOR_BLACK)
        main_menu_text_rect = main_menu_text.get_rect(center=self.main_menu_button.center)
        self.screen.blit(main_menu_text, main_menu_text_rect)

        pygame.display.flip()

        return self.retry_button, self.main_menu_button

    def run(self):
        while True:
            # Draw and update hover state every frame
            self.display()
            result = self.handle_events()

            if result == "retry":
                try:
                    import thegame.Game as Game  # Ensure correct import path
                    Game.main()  # Call the main function of the game
                except ImportError as e:
                    pass
                return
            elif result == "main_menu":
                try:
                    StartupScreen().run()  # Call the main function of the startup screen
                except ImportError as e:
                    pass
                return