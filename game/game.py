import pygame
import sys
from player import Player
from enemy import FirstEnemy, SecondEnemy

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 900
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Invación Espacial")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        self.player = Player(self.screen_width // 2, self.screen_height - 70)
        self.enemies = []
        self.create_enemies()
        
        self.score = 0
        self.game_over = False
        self.enemy_direction = 1  # Dirección común para todos los enemigos
        self.enemy_speed = 2
        self.enemy_speed_increase = 0.5
        self.font = pygame.font.SysFont(None, 36)
        
        self.enemy_move_timer = 0
        self.enemy_move_interval = 25  # Mayor intervalo para movimiento más lento

    def create_enemies(self):
        self.enemies = []
        for row in range(5):
            for col in range(3):
                # Crear diferentes tipos de enemigos alternadamente
                if (row + col) % 2 == 0:
                    enemy = FirstEnemy(100 + row * 90, 50 + col * 75)
                else:
                    enemy = SecondEnemy(100 + row * 90, 50 + col * 75)
                self.enemies.append(enemy)


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.player.shoot()
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()

    def update(self):
        if self.game_over:
            return
                
        # Movimiento del jugador y actualización de balas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move("left", self.screen_width)
        if keys[pygame.K_RIGHT]:
            self.player.move("right", self.screen_width)
        
        self.player.update(self.screen_height)
        
        # Movimiento enemigo
        self.enemy_move_timer += 1
        if self.enemy_move_timer >= self.enemy_move_interval:
            self.enemy_move_timer = 0
            edge_hit = False
            
        
            for enemy in self.enemies:
                if enemy.update(self.screen_width):
                    edge_hit = True
            
            # Si algún enemigo tocó el borde, todos cambian de dirección y bajan
            if edge_hit:
                self.enemy_direction *= -1
                for enemy in self.enemies:
                    enemy.direction = self.enemy_direction
                    enemy.move_down()
        
        # Disparos enemigos y actualización de balas (ahora en cada frame)
        for enemy in self.enemies:
            enemy.try_shoot()
            enemy.update_bullets(self.screen_height)
            
            # Disparos enemigos
            for enemy in self.enemies:
                enemy.try_shoot()
                enemy.update_bullets(self.screen_height)
        
        self.check_collisions()
        
        if not self.enemies:
            self.enemy_speed += self.enemy_speed_increase
            self.create_enemies()
        
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.game_over = True
                break

    def check_collisions(self):
        # Balas del jugador contra enemigos
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.colliderect(enemy.hitbox):  # Cambiamos rect por hitbox
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    self.score += 10
                    break
        
        # Balas enemigas contra jugador 
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                if bullet.colliderect(self.player.rect):
                    enemy.bullets.remove(bullet)
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.game_over = True
                    break

    def draw(self):
        self.screen.fill((0, 0, 0))
        
        if not self.game_over:
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
        
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (self.screen_width - 120, 10))
        
        if self.game_over:
            game_over_text = self.font.render("GAME OVER - Presiona R para Restart", True, (255, 0, 0))
            self.screen.blit(game_over_text, (self.screen_width//2 - 180, self.screen_height//2))
        
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)

if __name__ == "__main__":
    game = Game()
    game.run()