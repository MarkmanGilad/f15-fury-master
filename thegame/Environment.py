import pygame
import random
import torch
import math
from buildings import Building
from fuel import Fuel
from airplane import Airplane
from human_agent import Human_agent
from openscreen import StartupScreen
from enemy import Enemy
from bullet import Bullet
from constant import *


class Environment(): 

    countBuildings = 0
    createFirtstEnemy = False
    timer = 0
    time = 0
    score = 0
    precentage = INITIAL_FUEL_PERCENTAGE
    fueldropspeed = 0
    episode_steps = 0  # ספירה של צעדים בפרק
    
    
    def __init__(self, delay = ENV_DEFAULT_DELAY):
        self.init_pygame()
        self.reset()
        self.delay = delay
        self.reward = 0.0

    def reset (self):
        Building.speed = BUILDING_SPEED
        Fuel.count = FUEL_INITIAL_COUNT
        Environment.precentage = INITIAL_FUEL_PERCENTAGE
        Environment.countBuildings = 0
        Environment.time = 0
        Environment.score = 0
        Environment.timer = 0
        Environment.speed = 0
        Environment.createFirtstEnemy = False
        Environment.episode_steps = 0  # אפס את ספירת הצעדים
        self.holes_passed = 0
        self.enemies_killed = 0
        self.fuels_collected = 0
        self.bullet = Bullet()
        self.bullet_group = pygame.sprite.Group(self.bullet)
        self.player = Airplane()
        Airplane.cooldown = 0
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.enemy_group = pygame.sprite.Group()  # <-- change to Group
        # pygame.mixer.stop()
        
        # pygame.mixer.music.play(-1)
        self.buildingsG = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self.fuels = pygame.sprite.Group()
        self.fueldrop = INITIAL_FUEL_DROP
        self.enemychance = INITIAL_ENEMY_CHANCE
        self.speed = INITIAL_SPEED
        self.create_buildings()
        
        
    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("F15 Fury: Urban Assult")
        self.outofgas = pygame.image.load("pictures/outofgas.png")
        self.outofgas = pygame.transform.scale(self.outofgas, OUT_OF_GAS_IMAGE_SIZE)
        self.collision_image = pygame.image.load("pictures/collision.png") 
        self.collision_image = pygame.transform.scale(self.collision_image, COLLISION_IMAGE_SIZE)
        self.main_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font = pygame.font.SysFont('arial', FONT_SIZE)
        self.background_color = BACKGROUND_COLOR  # כחול כהה
        # יצירת כוכבים
        self.stars = [{"x": random.randint(0, SCREEN_WIDTH), "y": random.randint(0, SCREEN_HEIGHT // 2)} for _ in range(NUM_STARS)]

        # יצירת ירח
        self.moon = {"x": SCREEN_WIDTH - MOON_X_OFFSET, "y": MOON_Y, "radius": MOON_RADIUS}
        # pygame.mixer.music.load("sounds/gamemusic.mp3")
        


    def create_buildings(self):
        Environment.countBuildings += 1  
        building1 = Building()
        building2 = Building()
        building1.set_random_height()
        building2.set_height(building1.height)
        self.buildingsG.add([building1, building2])
        if Environment.countBuildings == self.enemychance:
                enemy = Enemy()
                enemy.setheight(building2.height)
                self.enemy_group.add(enemy)
                Environment.countBuildings = 0
                Environment.createFirtstEnemy = True


    def render(self):
        # מילוי המסך בצבע רקע
        self.main_surf.fill(self.background_color)
        percentage_text = self.font.render(f"Fuel: {Environment.precentage}%", True, COLOR_WHITE)
        gametime = self.font.render(f"Time: {Environment.time}", True, COLOR_WHITE)
        Environment.fueldropspeed += 1
        if(Environment.fueldropspeed == self.fueldrop):
            Environment.precentage -= 1
            Environment.fueldropspeed = 0
       # if(Building.speed % 5 == 0):
            #if self.fueldrop > 1:
              #  self.fueldrop -= 0.5    
        Environment.timer += 1
        if Environment.timer == TIMER_TICKS:
            Environment.time += 1
            Environment.timer = 0
        if(Environment.time % SCORE_INTERVAL == 0) and Environment.time != 0:
            Environment.score += 1
        score = self.font.render(f"Score: {Environment.score}", True, COLOR_WHITE)
        self.main_surf.blit(percentage_text, (10, 10))
        self.main_surf.blit(score, (10, 50))
        self.main_surf.blit(gametime, (10, 90))
        # ציור כוכבים
        for star in self.stars:
            pygame.draw.circle(self.main_surf, COLOR_WHITE, (star["x"], star["y"]), 2)

        # ציור ירח
        pygame.draw.circle(self.main_surf, MOON_COLOR, (self.moon["x"], self.moon["y"]), self.moon["radius"])

      
        self.player.update_crystals()
        self.player.draw_crystals(self.main_surf)

        # ציור שאר האלמנטים
        self.player_group.draw(self.main_surf)
        self.player.debug_draw_mask(self.main_surf)
        if Environment.createFirtstEnemy:
                self.enemy_group.draw(self.main_surf)
        self.buildingsG.draw(self.main_surf)
        self.player.bullet_group.draw(self.main_surf)
        self.fuels.draw(self.main_surf)

        self.screen.blit(self.main_surf, (0, 0))
        pygame.display.update()

    def move(self, action):
        done = False
        self.reward = 0.0
        buildings_list = sorted(self.buildingsG, key=lambda b: b.rect.top, reverse=True)
        height1 = buildings_list[0].rect.top
        height2 = buildings_list[1].rect.bottom
        middle_hole_y = (height1 + height2) / 2
        
        self.player.move(action)
        Environment.episode_steps += 1
        
        # a) die / out of gas
        if self.is_coliding() or self.is_no_gas():
            self.reward = DIE_REWARD
            return DIE_REWARD, True
        
        # survival reward: small bonus every step for staying alive
        self.reward += SURVIVAL_REWARD
        
        # d) directional distance reward: teach agent to align to hole center (±10px)
        player_center_y = self.player.rect.centery
        delta = middle_hole_y - player_center_y  # + => hole below, - => hole above
        if abs(delta) <= HOLE_CENTER_TOLERANCE:
            # aligned: no shaping needed, survival reward already applied
            if action in (1, 2):
                self.reward -= DISTANCE_REWARD
        elif delta > HOLE_CENTER_TOLERANCE:
            # hole is below -> down (2) good, up (1) bad, else half penalty
            if action == 2:
                self.reward += DISTANCE_REWARD
            elif action == 1:
                self.reward -= DISTANCE_REWARD
            else:
                self.reward -= DISTANCE_REWARD / 2
        else:  # delta < -HOLE_CENTER_TOLERANCE
            # hole is above -> up (1) good, down (2) bad, else half penalty
            if action == 1:
                self.reward += DISTANCE_REWARD
            elif action == 2:
                self.reward -= DISTANCE_REWARD
            else:
                self.reward -= DISTANCE_REWARD / 2
        if abs(SCREEN_WIDTH - self.player.rect.centerx) <= EDGE_DISTANCE_THRESHOLD:
            if action == 3:  # only penalize moving right into the edge
                self.reward -= EDGE_TOO_CLOSE_PENALTY
                

        # shoot reward/penalty
        if action == 5:
            self.reward += SHOOT_REWARD
        Building.speed += SPEED_INCREMENT
        if Building.speed >= 6 and Building.speed < 6 + SPEED_INCREMENT:
            self.enemychance -= 1
            # print(self.enemychance)
        if Building.speed % 2 < 0.01:
            self.player.speed += PLAYER_SPEED_INCREMENT
        self.buildingsG.update()
        self.enemy_group.update()
        self.player.bullet_group.update()
        self.fuels.update()

        # b) kill enemy
        if self.hit():
            self.reward += ENEMY_REWARD
            self.enemies_killed += 1
        
    # בדוק אם אסף דלק
        # c) pickup fuel
        if self.check_fuel_pickup():
            self.reward += PICKUP_REWARD
            self.fuels_collected += 1

        if len(self.buildingsG) == 0:
            self.reward += THROUGH_HOLE_REWARD
            self.holes_passed += 1
            self.create_buildings()

        if len(self.fuels) == 0:
            self.spawn_fuel()

        # הזזת כוכבים
        for star in self.stars:
            star["x"] -= STAR_SPEED  # תנועה איטית שמאלה
            if star["x"] < 0:  # אם הכוכב יוצא מהמסך, החזר אותו לצד ימין
                star["x"] = SCREEN_WIDTH
                star["y"] = random.randint(0, SCREEN_HEIGHT // 2)

        # הזזת ירח
        self.moon["x"] -= MOON_SPEED  # תנועה איטית מאוד שמאלה
        if self.moon["x"] + self.moon["radius"] < 0:  # אם הירח יוצא מהמסך, החזר אותו לצד ימין
            self.moon["x"] = SCREEN_WIDTH

        return self.reward, done
        

    def spawn_fuel(self):
        fuel = Fuel()
        fuel1 = Fuel()
        self.fuels.add([fuel, fuel1])

    def display_collision_image(self):
        image_rect = self.collision_image.get_rect(topleft=(self.player.rect.x + 100, self.player.rect.y)) 
        # colis = pygame.mixer.Sound("sounds/collision.mp3").play()
        # colis.set_volume(0.01)
        self.screen.blit(self.collision_image, image_rect)
        pygame.display.update()
        # pygame.time.delay(self.delay)

    def check_fuel_pickup(self):
        collision = pygame.sprite.groupcollide(self.player_group, self.fuels, False, True, pygame.sprite.collide_rect)
        picked_up = bool(collision)
        if picked_up and Environment.precentage < INITIAL_FUEL_PERCENTAGE:
            # sheep = pygame.mixer.Sound("sounds/sheep.mp3").play()
            # sheep.set_volume(0.05)
            Environment.precentage += FUEL_PICKUP_BONUS
        return picked_up

    def display_out_of_gas_image(self):
        self.main_surf.blit(self.outofgas, ((SCREEN_WIDTH - 400) / 2  , (SCREEN_HEIGHT - 200) / 2))
        self.screen.blit(self.main_surf, (0, 0))
        pygame.display.update()
        pygame.time.delay(self.delay)
        StartupScreen().run()

    def is_coliding(self):
        collision = pygame.sprite.groupcollide(self.player_group, self.buildingsG, False, False, pygame.sprite.collide_mask)
        Enemycollision = pygame.sprite.groupcollide(self.player_group, self.enemy_group, False, False, pygame.sprite.collide_mask)  
        if collision or Enemycollision:
            # self.reward += DIE_REWARD
            return True
        return False
        
    

    def is_no_gas(self):
        if Environment.precentage <= 0:
            return True
        return False
    
    def is_end_of_game(self):
        if self.is_coliding() or self.is_no_gas():
            return True
        return False


    def hit(self):
        collision = pygame.sprite.groupcollide(self.player.bullet_group, self.enemy_group, True, True, pygame.sprite.collide_mask)
        if collision:
            # self.reward+= ENEMY_REWARD
            # score = pygame.mixer.Sound("sounds/score.mp3").play()
            # score.set_volume(0.05)
            return True
        # elif collision == False and list(self.bullet_group) >= 1:
        #     self.reward -=

            
        return False
    
    def Tensor_env(self):
        env_state = torch.zeros(DQN_INPUT_SIZE, dtype=torch.float32)
        # נרמל את כל הערכים ל-0-1 range
        env_state[0] = self.player.rect.centerx / SCREEN_WIDTH  # x coordinate normalized
        env_state[1] = self.player.rect.centery / SCREEN_HEIGHT  # y coordinate normalized
        env_state[2] = self.precentage / 100.0  # percentage normalized
        env_state[3] = float(Airplane.cooldown > AIRPLANE_COOLDOWN_THRESHOLD)  # boolean כ-0 או 1

        # Buildings — sort by rect.top so bottom building (higher top) is first
        buildings_list = sorted(self.buildingsG, key=lambda b: b.rect.top, reverse=True)
        if len(buildings_list) >= 2:
            # בניין תחתון — הקצה העליון שלו הוא תחתית החור
            env_state[4] = buildings_list[0].rect.x / SCREEN_WIDTH
            env_state[5] = buildings_list[0].rect.top / SCREEN_HEIGHT
            # בניין עליון — הקצה התחתון שלו הוא ראש החור
            env_state[6] = buildings_list[1].rect.x / SCREEN_WIDTH
            env_state[7] = buildings_list[1].rect.bottom / SCREEN_HEIGHT
        
        # Fuel items — max 2 slots (indices 8-11)
        for i, fuel in enumerate(self.fuels):
            if i >= 2:
                break
            env_state[8 + i * 2] = fuel.rect.x / SCREEN_WIDTH
            env_state[9 + i * 2] = fuel.rect.y / SCREEN_HEIGHT
        
        env_state[12] = float(Environment.countBuildings == self.enemychance)
        return env_state
    

    



        

