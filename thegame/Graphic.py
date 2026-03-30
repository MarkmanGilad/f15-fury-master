import pygame
from Environment import Environment
from airplane import Airplane
import random

BLUE = (0, 0, 255)
LIGHTGRAY = (211, 211, 211)
WIDTH, HEIGHT = 1450, 720
FPS = 60

class Graphics:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("F15 Fury: Urban Assult")
        self.main_surf = pygame.Surface((WIDTH, HEIGHT))
        self.background = pygame.image.load("pictures/background.jpg")
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        self.buildings = []
        self.clock = pygame.time.Clock()
        self.player = Airplane(self)
        self.player_rect = self.player.player_rect
        self.collision = False
        self.collision_image = pygame.image.load("pictures/collision.png") 
        self.collision_image = pygame.transform.scale(self.collision_image, (100, 100))

        self.time = pygame.time.Clock()
        self.starttimer = pygame.time.get_ticks()
        self.elapsed_time = (pygame.time.get_ticks() - self.starttimer) // 1000

        self.precentage = 100
        self.FUEL_DECREASE_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.FUEL_DECREASE_EVENT, 500)

        self.FUEL_BONUS_EVENT = pygame.USEREVENT + 2
        pygame.time.set_timer(self.FUEL_BONUS_EVENT, 2000)

        self.fuel_image = pygame.image.load("pictures/fuel.png")  
        self.fuel_image = pygame.transform.scale(self.fuel_image, (100, 100))

        self.outofgas = pygame.image.load("pictures/outofgas.png")
        self.outofgas = pygame.transform.scale(self.outofgas, (500,200))
        self.fuel_items = [] 

    def render (self):
        self.main_surf.blit(self.background, (0,0))
        self.screen.blit(self.main_surf, (0,0))
        for building in self.buildings:
            building.render()
        if self.player:
            self.player.render(self.screen)     

        for building in self.buildings:
            if self.player.check_collision(building):
                self.display_collision_image()
                pygame.display.update()
                pygame.time.delay(1000)  
                pygame.quit()
                exit()
            
        else:
            self.collision = False

        for fuel in self.fuel_items:
            self.screen.blit(self.fuel_image, (fuel["x"], fuel["y"]))
            
        font = pygame.font.Font(None, 50)
        text = font.render(f"fuel: {self.precentage}%", True, (255, 0, 0))
        self.screen.blit(text, (10, 45))
        font = pygame.font.Font(None, 50)
        self.elapsed_time = (pygame.time.get_ticks() - self.starttimer) // 1000
        text = font.render(f"Time: {self.elapsed_time}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))
        self.time.tick(60)


        self.check_fuel_pickup()
        pygame.display.update()

    def is_quit (self,speed):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return True
            elif(event.type == self.FUEL_DECREASE_EVENT):
                if(self.precentage > 0):
                    self.precentage -= 2
                if(self.precentage == 0):
                    pygame.time.delay(200)
                    self.screen.blit(self.outofgas, (500, 250))
                    pygame.display.update()
                    pygame.time.delay(3000)
                    exit()
            elif event.type == self.FUEL_BONUS_EVENT:
                self.spawn_fuel_item()    
            return False
    
    
    def handle_events(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys)  

    def add_building(self, building):
        self.buildings.append(building)

    def move_objects(self, speed):
        for building in self.buildings[:]:  
            building.move(speed)
            
            if building.x < -500:
                self.buildings.remove(building)
        for fuel in self.fuel_items[:]:
            fuel["x"] -= (speed + 5)
            if(fuel["x"] < - 500):
                self.fuel_items.remove(fuel)        


    def add_agent(self, agent):
        self.agent = agent

    def display_collision_image(self):
        image_rect = self.collision_image.get_rect(topleft=(self.player.x + 100 , self.player.y)) 
        self.screen.blit(self.collision_image, image_rect)  

    def spawn_fuel_item(self):
        fuel_x = 1600
        fuel_y = random.randint(100, HEIGHT - 100)
        self.fuel_items.append({"x":  fuel_x, "y": fuel_y})

    def check_fuel_pickup(self):

        for fuel in self.fuel_items[:]:  
            fuel_rect = pygame.Rect(fuel["x"], fuel["y"], 50, 50)

            if self.player_rect.colliderect(fuel_rect):  
                self.precentage = min(100, self.precentage + 3)  
                self.fuel_items.remove(fuel)  