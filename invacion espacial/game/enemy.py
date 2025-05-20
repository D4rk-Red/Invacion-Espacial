import pygame
import random
import os

class Enemy:
    def __init__(self, x, y):
        # Cargar imagen
        try:
            self.image = pygame.image.load(os.path.join('images', 'cat.png')).convert_alpha()
            self.image = pygame.transform.scale(self.image, (90, 80))
        except:
            # si no encuentra la imagen
            self.image = pygame.Surface((90, 80))
            self.image.fill((255, 0, 0))  # rojo

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 4
        self.direction = 1
        self.move_down_distance = 20
        self.bullets = []
        self.shoot_probability = 0.009
        self.should_move_down = False

    def update(self, screen_width):
        self.rect.x += self.speed * self.direction
        
        # Verificar si tocó un borde
        if self.rect.right >= screen_width or self.rect.left <= 0:
            self.direction *= -1  # Invertir dirección
            return True  # Indicar que debe bajar
        return False

    def move_down(self):
        self.rect.y += 15  # Bajar solo 15 píxeles

    def try_shoot(self):
        if random.random() < self.shoot_probability:
            bullet = pygame.Rect(self.rect.centerx - 2, self.rect.bottom, 4, 10)
            self.bullets.append(bullet)

    def update_bullets(self, screen_height):
        for bullet in self.bullets[:]:
            bullet.y += 3
            if bullet.top > screen_height:
                self.bullets.remove(bullet)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            pygame.draw.rect(screen, (255, 100, 100), bullet)
