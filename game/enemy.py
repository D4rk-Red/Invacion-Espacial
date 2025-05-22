import pygame
import random
import os
from abc import ABC, abstractmethod

class Enemy(ABC):
    def __init__(self, x, y):
        self.image = self.load_image()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 10
        self.direction = 1
        self.bullets = []
        self.shoot_probability = 0.0002
        # Área de colisión más grande que el rectángulo original para obtener mejor la colision
        self.hitbox = None
        self.create_hitbox()
        
    def create_hitbox(self):
        # Reducimos el margen del hitbox (0 = mismo tamaño que la imagen)
        margin_reduction = 0 
        self.hitbox = self.rect.inflate(-margin_reduction, -margin_reduction)
        
    def update(self, screen_width):
        self.rect.x += self.speed * self.direction
        self.hitbox.center = self.rect.center  # Actualiza la posición del hitbox
        
        if self.rect.right >= screen_width or self.rect.left <= 0:
            return True
        return False
    
    def move_down(self):
        self.rect.y += 40
        
    def try_shoot(self):
        if random.random() < self.shoot_probability:
            self.shoot()
            
    def shoot(self):
        bullet = pygame.Rect(self.rect.centerx - 2, self.rect.bottom, 4, 10)
        self.bullets.append(bullet)
        
    def update_bullets(self, screen_height):
        for bullet in self.bullets[:]:
            bullet.y += 1  # Velocidad constante de balas
            if bullet.top > screen_height:
                self.bullets.remove(bullet)
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            pygame.draw.rect(screen, (255, 100, 100), bullet)

class FirstEnemy(Enemy):
    def load_image(self):
        try:
            image = pygame.image.load('images/pulpo.png').convert_alpha()
            return pygame.transform.scale(image, (80, 80))
        except:
            surface = pygame.Surface((80, 80))
            surface.fill((255, 0, 0))
            return surface
            
    def create_hitbox(self):
        # Hitbox más grande para este enemigo específico
        self.hitbox = self.rect.inflate(-10, -10)  # Menos reducción = hitbox más grande

class SecondEnemy(Enemy):
    def load_image(self):
        try:
            image = pygame.image.load('images/enemigo.png').convert_alpha()
            return pygame.transform.scale(image, (60, 60))
        except:
            surface = pygame.Surface((60, 60))
            surface.fill((0, 255, 0))
            return surface
            
    def create_hitbox(self):
        self.hitbox = self.rect.inflate(-2, -2) 