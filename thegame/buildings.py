import pygame
import random
from constant import *

class Building(pygame.sprite.Sprite): 

    speed = BUILDING_SPEED

    def __init__(self):
        super().__init__() 
        self.height = 0
        self.image = pygame.image.load("pictures/buildings.png")
        self.mask = pygame.mask.from_surface(self.image)



   
    
    def set_random_height(self):
        options = list(range(BUILDING_HEIGHT_MIN, BUILDING_HEIGHT_MAX, BUILDING_HEIGHT_STEP))
        self.height =  random.choice(options)  
        self.image = pygame.transform.scale(self.image, (BUILDING_WIDTH, self.height))
        self.rect = self.image.get_rect(topleft=(BUILDING_START_X, BUILDING_SCREEN_HEIGHT - self.height))
        self.mask = pygame.mask.from_surface(self.image)

    def set_height(self, height):
        self.height = BUILDING_SCREEN_HEIGHT - height - BUILDING_GAP_OFFSET
        self.image = pygame.transform.scale(self.image, (BUILDING_WIDTH, self.height))
        self.rect = self.image.get_rect(topleft=(BUILDING_START_X, 0))

        self.image = pygame.transform.flip(self.image, False, True)
        self.mask = pygame.mask.from_surface(self.image)
    

    def update(self):
        self.rect.x -= Building.speed
        self.mask = pygame.mask.from_surface(self.image)
        if self.rect.x < BUILDING_KILL_X:
            self.kill()

    def get_height(self):
        return self.height