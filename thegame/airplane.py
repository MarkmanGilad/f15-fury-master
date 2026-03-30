import pygame
import random
from bullet import Bullet

WIDTH = 300
HEIGHT = 300

class Airplane(pygame.sprite.Sprite):

    cooldown = 0

    def __init__(self):
        super().__init__()
        transpert = (0, 0, 0)
        self.x = 200
        self.y = 300
        self.bullet_group = pygame.sprite.Group()
        self.image = pygame.image.load("pictures/player.png")       
        self.image = pygame.transform.scale(self.image, (150, 140))
        self.rect = self.image.get_rect(topleft=(self.x, self.y)) 
        self.speed = 10
        self.mask = pygame.mask.from_surface(self.image)

        # רשימת קריסטלים
        self.crystals = []

    def move(self, action):
        Airplane.cooldown += 1
        if action == 1 and self.rect.top > 0:  # למעלה, רק אם לא יוצא מגבול עליון
            self.rect.centery -= self.speed
        elif action == 2 and self.rect.bottom < 720:  # למטה, רק אם לא יוצא מגבול תחתון
            self.rect.centery += self.speed
        elif action == 3 and self.rect.right < 1500:  # ימינה, רק אם לא יוצא מגבול ימני
            self.rect.centerx += self.speed
        elif action == 4 and self.rect.left > 0:  # שמאלה, רק אם לא יוצא מגבול שמאלי
            self.rect.centerx -= self.speed
        elif action == 5 and Airplane.cooldown > 70:  # ירי
            self.shoot()
            Airplane.cooldown = 0
    

        # הוספת קריסטל חדש במיקום הנוכחי של המטוס
        self.crystals.append({
            "x": self.rect.centerx - 70,
            "y": self.rect.centery,
            "dx": random.uniform(-2, 2),  # תנועה רנדומלית בציר ה-x
            "dy": random.uniform(-1, 1)  # תנועה רנדומלית בציר ה-y
        })

        # שמירה על מספר מוגבל של קריסטלים
        if len(self.crystals) > 30:  # לדוגמה, שמירה על 30 קריסטלים בלבד
            self.crystals.pop(0)

        # Always update mask after movement (future-proof for animation/rotation)
        self.mask = pygame.mask.from_surface(self.image)

    def update_crystals(self):
        # הזזת הקריסטלים לאחור עם תנועה רנדומלית
        for crystal in self.crystals:
            crystal["x"] -= 0.01 + crystal["dx"]  # תנועה שמאלה עם רנדומליות
            crystal["y"] += crystal["dy"]  # תנועה רנדומלית למעלה/למטה

    def draw_crystals(self, screen):
        # ציור הקריסטלים
        for crystal in self.crystals:
            pygame.draw.circle(screen, (255, 50, 230), (int(crystal["x"]), int(crystal["y"])), 5)  # קריסטל בצבע תכלת

    def shoot(self):
        bullet = Bullet()
        bullet.set_position(self.rect.centerx + 40, self.rect.centery - 45)
        self.bullet_group.add(bullet)

    def debug_draw_mask(self, surface):
        # Draw the mask outline in blue for debugging
        if hasattr(self, 'mask') and hasattr(self, 'rect'):
            mask_outline = self.mask.outline()
            if mask_outline:
                offset = (self.rect.x, self.rect.y)
                pygame.draw.lines(surface, (255, 50, 230), True, [(x+offset[0], y+offset[1]) for (x, y) in mask_outline], 2)


    def reset(self):
        transpert = (0, 0, 0)
        self.x = 200
        self.y = 75
        self.bullet_group = pygame.sprite.Group()
        self.image = pygame.image.load("pictures/player.png")       
        self.image = pygame.transform.scale(self.image, (150, 140))
        self.rect = self.image.get_rect(topleft=(self.x, self.y)) 
        self.speed = 10
        self.mask = pygame.mask.from_surface(self.image)

