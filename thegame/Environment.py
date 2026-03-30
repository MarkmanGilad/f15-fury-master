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

WIDTH, HEIGHT = 1450, 720
FPS = 60
DIE_REWARD     = -1.0      # עונש למוות
HOLE_REWARD    = 0.9       # תגמול על הימצאות לאמצע החור
DISTANCE_REWARD = 0.3     # עונש על מרחק מהחור
ENEMY_REWARD   = 0.1       # תגמול על הריגת אויב
PICKUP_REWARD  = 0.1       # תגמול על איסוף דלק
SHOOT_REWARD   = -0.02     # עונש על יריות
SURVIVAL_REWARD = 0.01     # תגמול על הישרדות
THROUGH_HOLE_REWARD = 0.5  # תגמול על מעבר דרך חור
HOLE_CENTER_TOLERANCE = 10  # pixels: considered aligned to hole center
EDGE_TOO_CLOSE_PENALTY = -0.5     # עונש נוסף אם קרוב מדי לקצה החור (למנוע ניצול של קצוות)


class Environment(): 

    countBuildings = 0
    createFirtstEnemy = False
    timer = 0
    time = 0
    score = 0
    precentage = 100
    fueldropspeed = 0
    episode_steps = 0  # ספירה של צעדים בפרק
    
    
    def __init__(self, delay = 2000):
        self.init_pygame()
        self.reset()
        self.delay = delay
        self.reward = 0.0

    def reset (self):
        Building.speed = 5
        Fuel.count = 7
        Environment.precentage = 100
        Environment.countBuildings = 0
        Environment.time = 0
        Environment.score = 0
        Environment.timer = 0
        Environment.speed = 0
        Environment.createFirtstEnemy = False
        Environment.episode_steps = 0  # אפס את ספירת הצעדים
        self.bullet = Bullet()
        self.bullet_group = pygame.sprite.Group(self.bullet)
        self.player = Airplane()
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.enemy_group = pygame.sprite.Group()  # <-- change to Group
        # pygame.mixer.stop()
        
        # pygame.mixer.music.play(-1)
        self.buildingsG = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self.fuels = pygame.sprite.Group()
        self.fueldrop = 30
        self.enemychance = 3
        self.speed = 5
        self.create_buildings()
        
        
    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("F15 Fury: Urban Assult")
        self.outofgas = pygame.image.load("pictures/outofgas.png")
        self.outofgas = pygame.transform.scale(self.outofgas, (500,200))
        self.collision_image = pygame.image.load("pictures/collision.png") 
        self.collision_image = pygame.transform.scale(self.collision_image, (100, 100))
        self.main_surf = pygame.Surface((WIDTH, HEIGHT))
        self.font = pygame.font.SysFont('arial', 36)
        self.background_color = (0, 0, 40)  # כחול כהה
        # יצירת כוכבים
        self.stars = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT // 2)} for _ in range(100)]

        # יצירת ירח
        self.moon = {"x": WIDTH - 200, "y": 50, "radius": 50}
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
        percentage_text = self.font.render(f"Fuel: {Environment.precentage}%", True, (255, 255, 255))
        gametime = self.font.render(f"Time: {Environment.time}", True, (255, 255, 255))
        Environment.fueldropspeed += 1
        if(Environment.fueldropspeed == self.fueldrop):
            Environment.precentage -= 1
            Environment.fueldropspeed = 0
       # if(Building.speed % 5 == 0):
            #if self.fueldrop > 1:
              #  self.fueldrop -= 0.5    
        Environment.timer += 1
        if Environment.timer == 60:
            Environment.time += 1
            Environment.timer = 0
        if(Environment.time % 5 == 0) and Environment.time != 0:
            Environment.score += 1
        score = self.font.render(f"Score: {Environment.score}", True, (255, 255, 255))
        self.main_surf.blit(percentage_text, (10, 10))
        self.main_surf.blit(score, (10, 50))
        self.main_surf.blit(gametime, (10, 90))
        # ציור כוכבים
        for star in self.stars:
            pygame.draw.circle(self.main_surf, (255, 255, 255), (star["x"], star["y"]), 2)

        # ציור ירח
        pygame.draw.circle(self.main_surf, (255, 255, 200), (self.moon["x"], self.moon["y"]), self.moon["radius"])

      
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

    def building_reward (self):
        height1 = list(self.buildingsG)[0].rect.top
        height2 = list(self.buildingsG)[1].rect.bottom   
        middle_hole_y = (height1 + height2) / 2
        center_player_y = self.player.rect.centery
        distance = abs(middle_hole_y - center_player_y)
        # נרמל את המרחק (מקסימום הוא חצי מגובה המסך)
        normalized_distance = distance / (HEIGHT / 4)
       
        reward = HOLE_REWARD - normalized_distance
        return reward

    def move(self, action):
        done = False
        self.reward = 0.0
        height1 = list(self.buildingsG)[0].rect.top
        height2 = list(self.buildingsG)[1].rect.bottom
        middle_hole_y = (height1 + height2) / 2
        
        self.player.move(action)
        Environment.episode_steps += 1
        
        # a) die / out of gas
        if self.is_coliding() or self.is_no_gas():
            return DIE_REWARD, True
        
        # d) directional distance reward: teach agent to align to hole center (±10px)
        player_center_y = self.player.rect.centery
        delta = middle_hole_y - player_center_y  # + => hole below, - => hole above
        if abs(delta) <= HOLE_CENTER_TOLERANCE:
            # aligned: vertical movement is bad
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
        if abs(WIDTH - self.player.rect.x) <= 500:
            if action == 3:  # right
                self.reward += EDGE_TOO_CLOSE_PENALTY
            else:
                self.reward -= EDGE_TOO_CLOSE_PENALTY / 2
                

        # shoot reward/penalty
        if action == 5:
            self.reward += SHOOT_REWARD
        Building.speed += 0.005
        if Building.speed == 6:
            self.enemychance -= 1
            # print(self.enemychance)
        if Building.speed % 2 < 0.01:
            self.player.speed += 0.6
        self.buildingsG.update()
        self.enemy_group.update()
        self.player.bullet_group.update()
        self.fuels.update()

        # b) kill enemy
        if self.hit():
            self.reward += ENEMY_REWARD
        
    # בדוק אם אסף דלק
        # c) pickup fuel
        if self.check_fuel_pickup():
            self.reward += PICKUP_REWARD

        if len(self.buildingsG) == 0:
            self.create_buildings()

        if len(self.fuels) == 0:
            self.spawn_fuel()

        # הזזת כוכבים
        for star in self.stars:
            star["x"] -= 1  # תנועה איטית שמאלה
            if star["x"] < 0:  # אם הכוכב יוצא מהמסך, החזר אותו לצד ימין
                star["x"] = WIDTH
                star["y"] = random.randint(0, HEIGHT // 2)

        # הזזת ירח
        self.moon["x"] -= 0.5  # תנועה איטית מאוד שמאלה
        if self.moon["x"] + self.moon["radius"] < 0:  # אם הירח יוצא מהמסך, החזר אותו לצד ימין
            self.moon["x"] = WIDTH

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
        if picked_up and Environment.precentage < 100:
            # sheep = pygame.mixer.Sound("sounds/sheep.mp3").play()
            # sheep.set_volume(0.05)
            Environment.precentage += 2
        return picked_up

    def display_out_of_gas_image(self):
        self.main_surf.blit(self.outofgas, ((WIDTH - 400) / 2  , (HEIGHT - 200) / 2))
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
        env_state = torch.zeros(13, dtype=torch.float32)
        # נרמל את כל הערכים ל-0-1 range
        env_state[0] = self.player.x / WIDTH  # x coordinate normalized
        env_state[1] = self.player.y / HEIGHT  # y coordinate normalized
        env_state[2] = self.precentage / 100.0  # percentage normalized
        env_state[3] = float(Airplane.cooldown > 70)  # boolean כ-0 או 1
        # index = 4
        # for building in self.buildingsG:
        #     env_state[index] = building.rect.x
        #     index += 1
        #     if index == 1:
        #         env_state[index] = building.rect.top
        #     else:
        #         env_state[index] = building.rect.bottom
        #     index += 1
        # מלא בניינים - תמיד בדיוק 2
        buildings_list = list(self.buildingsG)
        if len(buildings_list) >= 2:
            # בניין ראשון (עליון)
            env_state[4] = buildings_list[0].rect.x / WIDTH  # x normalized
            env_state[5] = buildings_list[0].rect.top / HEIGHT  # top normalized
            # בניין שני (תחתון)
            env_state[6] = buildings_list[1].rect.x / WIDTH  # x normalized
            env_state[7] = buildings_list[1].rect.bottom / HEIGHT  # bottom normalized
        
        index = 8
        for fuel in self.fuels:
            env_state[index] = fuel.rect.x / WIDTH  # fuel x normalized
            index += 1
            env_state[index] = fuel.rect.y / HEIGHT  # fuel y normalized
            index += 1
        
        env_state[12] = float(Environment.countBuildings == self.enemychance)
        return env_state
    

    



        

