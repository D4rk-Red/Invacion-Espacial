import pygame
import os
import random
import math
from .enemy import BasicEnemy, StrongEnemy, FinalBoss, RadialEnemy
from .shield import Shield

class LevelManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.level_config = {
            1: {
                'background': 'lvl1.png',
                'enemy_rows': 2,
                'enemy_cols': 6,
                'enemy_type': BasicEnemy,
                'clouds': False,
                'satellites': False,
                'shields': False,
                'music': 'musica_nivel1.mp3'
            },
            2: {
                'background': 'lvl2.png',
                'enemy_mix': True,
                'mix_rows': 3,
                'mix_cols': 7,
                'pattern': 'checker',
                'bullet_speed': 4,
                'clouds': True,
                'satellites': False,
                'shields': True,
                'music': 'musica_nivel2.mp3'
            },
            3: {
                'background': 'lvl3.png',
                'boss': True,
                'minion_type': RadialEnemy,  
                'minions_count': 4,
                'minion_bullet_speed': 3,  
                'clouds': False,
                'satellites': True,
                'shields': True,
                'music': 'musica_jefe_final.mp3',
                'boss_bullet_speed': 6  
            }
        }

    def load_level_background(self, level):
        if level not in self.level_config:
            return None
            
        bg_name = self.level_config[level]['background']
        try:
            path = os.path.join(self.base_path, 'images', bg_name)
            background = pygame.image.load(path).convert()
            return pygame.transform.scale(background, (self.screen_width, self.screen_height))
        except Exception as e:
            print(f"Error al cargar fondo {bg_name}: {e}")
            return None

    def create_enemies(self, level):
        config = self.level_config.get(level, {})
        enemies = []

        if config.get('boss', False):
            # Configuración del jefe final
            boss = FinalBoss(
                x=self.screen_width // 2 - 90,
                y=50,
                bullet_speed=config.get('boss_bullet_speed', 6)
            )
            boss.lives = 20
            boss.shoot_probability = 0.5
            enemies.append(boss)
            
            # Crear minions radiales
            MinionClass = config.get('minion_type', RadialEnemy)
            minion_bullet_speed = config.get('minion_bullet_speed', 3)
            
            for i in range(config.get('minions_count', 6)):
                x = random.randint(100, self.screen_width - 100)
                y = random.randint(50, 200)
                enemies.append(MinionClass(x, y, bullet_speed=minion_bullet_speed, level=level))
                
        elif config.get('enemy_mix', False):
            # Nivel 2 - Mezcla de enemigos
            rows = config.get('mix_rows', 3)
            cols = config.get('mix_cols', 7)
            pattern = config.get('pattern', 'checker')
            bullet_speed = config.get('bullet_speed', 3)
            
            for row in range(rows):
                for col in range(cols):
                    x = 100 + (col * (self.screen_width - 200) // cols)
                    y = 80 + (row * 70)
                    
                    if pattern == 'checker':
                        if (row + col) % 2 == 0:
                            enemy = BasicEnemy(x, y, bullet_speed, level)
                        else:
                            enemy = StrongEnemy(x, y, bullet_speed, level)
                    elif pattern == 'lines':
                        if row % 2 == 0:
                            enemy = BasicEnemy(x, y, bullet_speed, level)
                        else:
                            enemy = StrongEnemy(x, y, bullet_speed, level)
                    
                    enemies.append(enemy)
        else:
            # Nivel 1 - Enemigos básicos
            rows = config.get('enemy_rows', 2)
            cols = config.get('enemy_cols', 6)
            
            for row in range(rows):
                for col in range(cols):
                    x = 100 + (col * 100)
                    y = 80 + (row * 60)
                    enemies.append(BasicEnemy(x, y, bullet_speed=2, level=level))
        
        return enemies

    def create_shields(self, level):
        if not self.level_config.get(level, {}).get('shields', False):
            return []
        
        shields = []
        shield_y = self.screen_height - 150
        spacing = self.screen_width // 4
        
        # Escudos indestructibles solo en nivel 3
        indestructible = (level == 3)
        
        for i in range(3):
            shield_x = spacing * (i + 1) - 30
            shields.append(Shield(
                shield_x, 
                shield_y,
                indestructible=indestructible  # Pasamos el parámetro
            ))
        
        return shields

    def get_level_music(self, level):
        return self.level_config.get(level, {}).get('music')

    def should_spawn_clouds(self, level):
        return self.level_config.get(level, {}).get('clouds', False)

    def should_spawn_satellites(self, level):
        return self.level_config.get(level, {}).get('satellites', False)