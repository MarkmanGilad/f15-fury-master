import pygame
import pygame.pypm


class Human_agent():
    def __init__(self):  
        self.keys = {"up" : False, "down" : False, "left" : False, "right" : False, "space" : False}

    def Get_Action(self, events, state=None):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in {pygame.K_UP, pygame.K_w}:
                    self.keys["up"] = True
                if event.key in {pygame.K_DOWN, pygame.K_s}:
                    self.keys["down"] = True    
                if event.key in {pygame.K_RIGHT, pygame.K_d}:
                    self.keys["right"] = True
                if event.key in {pygame.K_LEFT, pygame.K_a}:
                    self.keys["left"] = True
                if event.key in {pygame.K_SPACE}:
                    self.keys["space"] = True

            if event.type == pygame.KEYUP:
                if event.key in {pygame.K_UP, pygame.K_w}:
                    self.keys["up"] = False
                if event.key in {pygame.K_DOWN, pygame.K_s}:
                    self.keys["down"] = False    
                if event.key in {pygame.K_RIGHT, pygame.K_d}:
                    self.keys["right"] = False
                if event.key in {pygame.K_LEFT, pygame.K_a}:
                    self.keys["left"] = False
                if event.key in {pygame.K_SPACE}:
                    self.keys["space"] = False    
        if self.keys["up"]:
            return 1
        if self.keys["down"]:
            return 2
        if self.keys["right"]:
            return 3
        if self.keys["left"]:
            return 4     
        if self.keys["space"]:
            return 5            
        return 0
    
    def reset (self):
        self.keys = {"up" : False, "down" : False, "left" : False, "right" : False, "space" : False}