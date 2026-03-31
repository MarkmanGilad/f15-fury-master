import pygame
import random
from buildings import Building
from constant import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        transpert = (0, 0, 0)
        
        self.image = pygame.image.load("pictures/enemis.png")
        self.image = pygame.transform.scale(self.image, ENEMY_IMAGE_SIZE)
        self.rect = self.image.get_rect(topleft=(ENEMY_START_X, 0)) 
        self.mask = pygame.mask.from_surface(self.image)
        self.height = 0

        # משתנים לתנועה אנכית
        self.vertical_direction = 1  # כיוון התנועה (1 = למטה, -1 = למעלה)
        self.vertical_speed = ENEMY_VERTICAL_SPEED  # מהירות התנועה האנכית
        self.original_y = self.rect.y  # המיקום ההתחלתי של האויב

    def setheight(self, height):
        self.rect.y = height
        self.rect.x += ENEMY_X_OFFSET
        self.original_y = self.rect.y  # עדכון המיקום ההתחלתי

    def update(self):
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x -= Building.speed

        # תנועה אנכית למעלה ולמטה
        self.rect.y += self.vertical_direction * self.vertical_speed
        if abs(self.rect.y - self.original_y) >= ENEMY_VERTICAL_RANGE:  # אם עבר את הטווח של 5 פיקסלים
            self.vertical_direction *= -1  # החלפת כיוון

        # הסרת האויב אם הוא יוצא מהמסך
        if self.rect.x < ENEMY_KILL_X:
            self.kill()
