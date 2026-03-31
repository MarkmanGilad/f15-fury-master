import pygame
import sys
import random
import math
from constant import *

class StartupScreen:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.mixer.music.load("sounds/backgroundmusic.mp3")
        pygame.mixer.music.set_volume(OPENSCREEN_MUSIC_VOLUME)
        pygame.mixer.music.play(-1)

        # רקע כהה
        self.background_color = OPENSCREEN_BACKGROUND_COLOR  # כחול כהה

        # כוכבים
        self.stars = [{"x": random.randint(0, SCREEN_WIDTH), "y": random.randint(0, SCREEN_HEIGHT // 2)} for _ in range(NUM_STARS)]


        # כוכבי לכת
        self.planets = [
            {"x": SCREEN_WIDTH, "y": SCREEN_HEIGHT // 3, "size": 200, "angle": 0, "rotation_speed": 0.1, "speed": 0.5, "color": (0, 102, 204)},
            {"x": SCREEN_WIDTH + 500, "y": SCREEN_HEIGHT // 4, "size": 300, "angle": 0, "rotation_speed": 0.05, "speed": 0.3, "color": (204, 102, 0)}
        ]

        # אסטרואידים
        self.asteroids = []
        for _ in range(NUM_ASTEROIDS):  # יצירת 7 אסטרואידים
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(30, 80)
            angle = random.randint(0, 360)
            rotation_speed = random.uniform(1, 5)  # מהירות סיבוב
            speed = random.uniform(3, 7)  # מהירות תנועה
            particles = []  # רשימת חלקיקים לשובל
            self.asteroids.append({
                "x": x, "y": y, "size": size, "angle": angle,
                "rotation_speed": rotation_speed, "speed": speed, "particles": particles
            })

        # מטוס
        self.airplane = pygame.image.load("pictures/player.png")
        self.airplane = pygame.transform.scale(self.airplane, AIRPLANE_IMAGE_SIZE)

        # תמונת אסטרואיד
        self.asteroid_image = pygame.image.load("pictures/asteroid.png")

        self.airplane_x = SCREEN_WIDTH // 4
        self.airplane_y = SCREEN_HEIGHT // 2
        self.airplane_direction = 1  # כיוון תנועה (1 = למטה, -1 = למעלה)

        # כפתורים
        pygame.font.init()
        self.title_font = pygame.font.SysFont('arial', 64, bold=True)
        self.button_font = pygame.font.SysFont('arial', 36)

        self.start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, ENDGAME_BUTTON_WIDTH, ENDGAME_BUTTON_HEIGHT)
        self.exit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + ENDGAME_BUTTON_SPACING, ENDGAME_BUTTON_WIDTH, ENDGAME_BUTTON_HEIGHT)

        self.title = self.title_font.render("SPACESHIP FURY : SPACE ASSULT", True, COLOR_YELLOW)
        self.title_rect = self.title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

        self.start_text = self.button_font.render("START", True, COLOR_BLACK)
        self.exit_text = self.button_font.render("EXIT", True, COLOR_BLACK)

        self.startcolor = COLOR_YELLOW
        self.hovercolor = COLOR_RED
        self.exitcolor = COLOR_YELLOW
        self.hoverexitcolor = COLOR_RED
        self.start_text_rect = self.start_text.get_rect(center=self.start_button.center)
        self.exit_text_rect = self.exit_text.get_rect(center=self.exit_button.center)

        self.start_hovered = False
        self.exit_hovered = False
        self.button_sound = pygame.mixer.Sound("sounds/buttonselect.mp3")
        self.button_sound.set_volume(OPENSCREEN_MUSIC_VOLUME)

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        # START button hover
        if self.start_button.collidepoint(mouse_pos):
            if not self.start_hovered:
                self.button_sound.play()
                self.start_hovered = True
            self.startcolor = self.hovercolor
        else:
            self.startcolor = COLOR_YELLOW
            self.start_hovered = False
        # EXIT button hover
        if self.exit_button.collidepoint(mouse_pos):
            if not self.exit_hovered:
                self.button_sound.play()
                self.exit_hovered = True
            self.exitcolor = self.hoverexitcolor
        else:
            self.exitcolor = COLOR_YELLOW
            self.exit_hovered = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if self.start_button.collidepoint(mouse_pos):
                    click = pygame.mixer.Sound("sounds/buttonclick.mp3").play() 
                    click.set_volume(OPENSCREEN_MUSIC_VOLUME)
                    pygame.time.delay(300)  
                    return True  # המשתמש לחץ על "START"

                if self.exit_button.collidepoint(mouse_pos):
                    click = pygame.mixer.Sound("sounds/buttonclick.mp3").play() 
                    click.set_volume(OPENSCREEN_MUSIC_VOLUME)
                    pygame.time.delay(300)   
                    pygame.quit()
                    sys.exit()

        return False

    def update(self):
        # עדכון כוכבים
        for star in self.stars:
            star["x"] -= STAR_SPEED  # תנועה שמאלה
            if star["x"] < 0:  # אם הכוכב יוצא מהמסך
                star["x"] = SCREEN_WIDTH  # החזר אותו לצד הימני של המסך
                star["y"] = random.randint(0, SCREEN_HEIGHT // 2)  # מיקום אנכי חדש


        # עדכון אסטרואידים
        for asteroid in self.asteroids:
            asteroid["x"] -= asteroid["speed"]  # תנועה שמאלה
            asteroid["angle"] += asteroid["rotation_speed"]  # סיבוב

            # יצירת חלקיקים לשובל
            for _ in range(3):  # יצירת 3 חלקיקים בכל פריים
                particle_x = asteroid["x"] + asteroid["size"] // 2
                particle_y = asteroid["y"] + asteroid["size"] // 2
                particle_size = random.randint(2, 6)
                particle_color = random.choice([(255, 69, 0), (255, 140, 0), (255, 215, 0)])  # גווני אש
                particle_speed = random.uniform(0.5, 1.5)
                asteroid["particles"].append({
                    "x": particle_x, "y": particle_y,
                    "size": particle_size, "color": particle_color,
                    "speed": particle_speed
                })

            # עדכון חלקיקים
            for particle in asteroid["particles"]:
                particle["x"] -= particle["speed"]  # תנועה שמאלה
                particle["size"] -= 0.1  # הקטנת גודל
            asteroid["particles"] = [p for p in asteroid["particles"] if p["size"] > 0]  # הסרת חלקיקים שנעלמו

            # אם האסטרואיד יוצא מהמסך
            if asteroid["x"] + asteroid["size"] < 0:
                asteroid["x"] = SCREEN_WIDTH
                asteroid["y"] = random.randint(0, SCREEN_HEIGHT)
                asteroid["size"] = random.randint(30, 80)
                asteroid["angle"] = random.randint(0, 360)
                asteroid["rotation_speed"] = random.uniform(1, 5)
                asteroid["speed"] = random.uniform(3, 7)
                asteroid["particles"] = []  # איפוס חלקיקים

        # עדכון תנועת החללית
        self.airplane_y += self.airplane_direction * AIRPLANE_VERTICAL_SPEED  # מהירות תנועה אנכית
        if self.airplane_y <= AIRPLANE_UPPER_BOUND or self.airplane_y + 75 >= SCREEN_HEIGHT - AIRPLANE_LOWER_OFFSET:  # טווח תנועה
            self.airplane_direction *= -1  # שינוי כיוון

    def draw(self):
        # ציור רקע
        self.screen.fill(self.background_color)

        # ציור כוכבים
        for star in self.stars:
            pygame.draw.circle(self.screen, COLOR_WHITE, (star["x"], star["y"]), 2)

        
        # ציור אסטרואידים
        for asteroid in self.asteroids:
            draw_asteroid(self.screen, asteroid, self.asteroid_image)

        # ציור מטוס
        self.screen.blit(self.airplane, (self.airplane_x, self.airplane_y))

        # ציור כותרת עם צל
        shadow_offset = SHADOW_OFFSET
        shadow_color = COLOR_BLACK
        self.screen.blit(self.title_font.render("SPACESHIP FURY : SPACE ASSULT", True, shadow_color),
                         (self.title_rect.x + shadow_offset, self.title_rect.y + shadow_offset))
        self.screen.blit(self.title, self.title_rect)

        # ציור כפתור START
        pygame.draw.rect(self.screen, COLOR_BLACK, self.start_button.inflate(10, 10))  # צל
        pygame.draw.rect(self.screen, self.startcolor, self.start_button, border_radius=10)  # כפתור עם פינות מעוגלות
        self.screen.blit(self.start_text, self.start_text_rect)

        # ציור כפתור EXIT
        pygame.draw.rect(self.screen, COLOR_BLACK, self.exit_button.inflate(10, 10))  # צל
        pygame.draw.rect(self.screen, self.exitcolor, self.exit_button, border_radius=10)  # כפתור עם פינות מעוגלות
        self.screen.blit(self.exit_text, self.exit_text_rect)

        pygame.display.flip()

    def run(self):
        while True:
            if self.handle_events():
                return True  # חזרה למסך הראשי

            self.update()
            self.draw()
            self.clock.tick(FPS)

# ציור כוכב לכת
def draw_planet(surface, planet):
    """מצייר כוכב לכת עם אפקטים של צללים וסיבוב"""
    x, y, size, angle, color = planet["x"], planet["y"], planet["size"], planet["angle"], planet["color"]

    # יצירת משטח זמני לכוכב הלכת
    planet_surface = pygame.Surface((size, size), pygame.SRCALPHA)

    # ציור עיגול בסיסי
    pygame.draw.circle(planet_surface, color, (size // 2, size // 2), size // 2)

    # הוספת צללים
    for i in range(size // 2, 0, -5):
        alpha = int(255 * (i / (size // 2)))
        pygame.draw.circle(planet_surface, (0, 0, 0, alpha), (size // 2, size // 2), i)

    # סיבוב הכוכב
    rotated_surface = pygame.transform.rotate(planet_surface, angle)

    # ציור הכוכב על המסך
    surface.blit(rotated_surface, (x, y))

# ציור אסטרואיד עם שובל אש
def draw_asteroid(surface, asteroid, asteroid_image):
    """מצייר אסטרואיד עם תמונה ושובל אש"""
    size = asteroid["size"]
    angle = asteroid["angle"]

    # שינוי גודל תמונת האסטרואיד לפי גודל האובייקט
    scaled_asteroid = pygame.transform.scale(asteroid_image, (size, size))

    # סיבוב האסטרואיד
    rotated_asteroid = pygame.transform.rotate(scaled_asteroid, angle)

    # מיקום האסטרואיד
    asteroid_rect = rotated_asteroid.get_rect(center=(asteroid["x"] + size // 2, asteroid["y"] + size // 2))

    # ציור חלקיקים (שובל אש)
    for particle in asteroid["particles"]:
        pygame.draw.circle(surface, particle["color"], (int(particle["x"]), int(particle["y"])), int(particle["size"]))

    # ציור האסטרואיד
    surface.blit(rotated_asteroid, asteroid_rect)
