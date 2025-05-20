import pygame
import os

class Player:
    def __init__(self, x, y):
        # Cargar imagen
        try:
            self.image = pygame.image.load(os.path.join('images', 'nave.png')).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 40))
        except:
            # si no encuentra la imagen
            self.image = pygame.Surface((50, 40))
            self.image.fill((0, 255, 0))  # Verde

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.lives = 3
        self.bullets = []
        self.bullet_speed = 7
        self.cooldown = 0

    def move(self, direction, screen_width):
        if direction == "left" and self.rect.left > 0:
            self.rect.x -= self.speed
        if direction == "right" and self.rect.right < screen_width:
            self.rect.x += self.speed

    def shoot(self):
        if self.cooldown == 0:
            bullet = pygame.Rect(self.rect.centerx - 2, self.rect.top, 4, 10)
            self.bullets.append(bullet)
            self.cooldown = 20

    def update(self, screen_height):
        # Actualizar posición de balas
        for bullet in self.bullets[:]:
            bullet.y -= self.bullet_speed
            if bullet.bottom < 0:
                self.bullets.remove(bullet)
        
        # Reducir cooldown
        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            pygame.draw.rect(screen, (255, 255, 0), bullet)