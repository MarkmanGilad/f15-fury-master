import pygame
import random

WIDTH = 300
HEIGHT = 750

class Building(pygame.sprite.Sprite): 

    speed = 5

    def __init__(self):
        super().__init__() 
        self.height = 0
        self.image = pygame.image.load("pictures/buildings.png")
        self.mask = pygame.mask.from_surface(self.image)



   
    
    def set_random_height(self):
        options = list(range(60, 401, 100))
        self.height =  random.choice(options)  
        self.image = pygame.transform.scale(self.image, (WIDTH, self.height))
        self.rect = self.image.get_rect(topleft=(1600, 750 - self.height))
        self.mask = pygame.mask.from_surface(self.image)

    def set_height(self, height):
        self.height = 750 - height - 200
        self.image = pygame.transform.scale(self.image, (WIDTH, self.height))
        self.rect = self.image.get_rect(topleft=(1600, 0))

        self.image = pygame.transform.flip(self.image, False, True)
        self.mask = pygame.mask.from_surface(self.image)
    

    def update(self):
        self.rect.x -= Building.speed
        self.mask = pygame.mask.from_surface(self.image)
        if self.rect.x < -300:
            self.kill()

    def get_height(self):
        return self.height