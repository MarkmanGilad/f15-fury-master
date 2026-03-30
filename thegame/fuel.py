import pygame
import random
from buildings import Building

WIDTH = 300
HEIGHT = 750

class Fuel(pygame.sprite.Sprite):
    count = 7
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("pictures/fuel.png")  # שם התמונה נשאר fuel.png
        self.original_image = pygame.transform.scale(self.original_image, (100, 100))
        self.image = self.original_image
        self.y = random.randint(100, HEIGHT - 100)
        self.rect = self.image.get_rect(topleft=(1600 + random.randint(-200, 800), self.y))
        self.angle = 0  # זווית התחלתית לסיבוב

    def update(self):
        Fuel.count += 0.005
        self.rect.x -= Fuel.count
        if self.rect.x < -300:
            self.kill()

        # עדכון סיבוב
        self.angle += 1  # שינוי זווית הסיבוב (1 מעלות בכל פריים)
        if self.angle >= 360:  # שמירה על זווית בין 0 ל-359
            self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)  # סיבוב התמונה
        self.rect = self.image.get_rect(center=self.rect.center)  # עדכון המיקום לאחר הסיבוב
