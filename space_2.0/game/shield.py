import pygame
import os
import math

class Shield:
    def __init__(self, x, y, width=60, height=30, life=10, indestructible=False):
        # Cargar imagen del escudo
        base_path = os.path.dirname(__file__)
        image_path = os.path.join(base_path, '..', 'images', 'block.jpeg')  
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height))
        except Exception as e:
            print(f"Error cargando imagen de escudo: {e}")
            # Fallback: crear superficie con color
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (0, 255, 0, 128), (0, 0, width, height))
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_life = life
        self.life = life
        self.indestructible = indestructible  # Nuevo atributo
        self.damage_timer = 0
        self.glow_timer = 0  # Para efecto de brillo en escudos indestructibles

    def take_damage(self):
        """Reduce la vida del escudo a menos que sea indestructible"""
        if not self.indestructible:
            self.life -= 1
            self.damage_timer = 10

    def is_destroyed(self):
        """Determina si el escudo debe ser eliminado"""
        return self.life <= 0 and not self.indestructible

    def update(self):
        """Actualiza temporizadores para efectos visuales"""
        if self.damage_timer > 0:
            self.damage_timer -= 1
        
        if self.indestructible:
            self.glow_timer = (self.glow_timer + 1) % 60  # Ciclo de 60 frames

    def draw(self, screen):
        """Dibuja el escudo con efectos visuales apropiados"""
        # Efecto de daño visual (parpadeo rojo)
        if self.damage_timer > 0:
            if self.damage_timer % 2 == 0:  # Parpadeo cada 2 frames
                tinted = self.image.copy()
                tinted.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(tinted, self.rect)
                return
        
        # Dibujar base del escudo
        if self.indestructible:
            # Efecto especial para escudos indestructibles
            glow_intensity = 0.5 + 0.5 * abs(math.sin(self.glow_timer * 0.1))  # Efecto pulsante
            
            # Borde dorado
            border = pygame.Surface((self.rect.width + 6, self.rect.height + 6), pygame.SRCALPHA)
            pygame.draw.rect(border, (255, 215, 0, int(200 * glow_intensity)), 
                           (0, 0, border.get_width(), border.get_height()), 3)
            screen.blit(border, (self.rect.x - 3, self.rect.y - 3))
            
            # Escudo con brillo
            shield_img = self.image.copy()
            shield_img.fill((255, 255, 255, int(50 * glow_intensity)), 
                          special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(shield_img, self.rect)
        else:
            # Escudo normal con transparencia basada en la vida
            alpha = int(255 * (self.life / self.max_life))
            if alpha < 255:
                temp_img = self.image.copy()
                temp_img.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(temp_img, self.rect)
            else:
                screen.blit(self.image, self.rect)