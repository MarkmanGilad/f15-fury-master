import pygame
import random

WIDTH = 300
HEIGHT = 300

class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        transpert = (0, 0, 0)
        self.image = pygame.image.load("pictures/bullet.png").convert()  
        self.image = pygame.transform.scale(self.image, (140, 130))
        self.image.set_colorkey(transpert)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 10
        # sound = pygame.mixer.Sound("sounds/shot.mp3").play()
        # sound.set_volume(0.05)



    def update(self):
        self.rect.x += self.speed
        if self.rect.x > 1450:
            self.kill()    

    def set_position(self, x, y):
        self.rect = self.image.get_rect(topleft=(x, y)) 
        self.mask = pygame.mask.from_surface(self.image)