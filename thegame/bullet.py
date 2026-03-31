import pygame
import random
from constant import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        transpert = COLOR_BLACK
        self.image = pygame.image.load("pictures/bullet.png").convert()  
        self.image = pygame.transform.scale(self.image, BULLET_IMAGE_SIZE)
        self.image.set_colorkey(transpert)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = BULLET_SPEED
        # sound = pygame.mixer.Sound("sounds/shot.mp3").play()
        # sound.set_volume(0.05)



    def update(self):
        self.rect.x += self.speed
        if self.rect.x > BULLET_KILL_X:
            self.kill()    

    def set_position(self, x, y):
        self.rect = self.image.get_rect(topleft=(x, y)) 
        self.mask = pygame.mask.from_surface(self.image)