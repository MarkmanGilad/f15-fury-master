import pygame
import random
from buildings import Building
from constant import *

class Fuel(pygame.sprite.Sprite):
    count = FUEL_INITIAL_COUNT
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("pictures/fuel.png")  # שם התמונה נשאר fuel.png
        self.original_image = pygame.transform.scale(self.original_image, FUEL_IMAGE_SIZE)
        self.image = self.original_image
        self.y = random.randint(FUEL_Y_MIN, BUILDING_SCREEN_HEIGHT - FUEL_Y_MIN)
        self.rect = self.image.get_rect(topleft=(FUEL_START_X + random.randint(FUEL_X_OFFSET_MIN, FUEL_X_OFFSET_MAX), self.y))
        self.angle = 0  # זווית התחלתית לסיבוב

    def update(self):
        Fuel.count += FUEL_SPEED_INCREMENT
        self.rect.x -= Fuel.count
        if self.rect.x < FUEL_KILL_X:
            self.kill()

        # עדכון סיבוב
        self.angle += FUEL_ROTATION_SPEED  # שינוי זווית הסיבוב (1 מעלות בכל פריים)
        if self.angle >= FUEL_ROTATION_MAX:  # שמירה על זווית בין 0 ל-359
            self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)  # סיבוב התמונה
        self.rect = self.image.get_rect(center=self.rect.center)  # עדכון המיקום לאחר הסיבוב
