import pygame
import sys
import os
import random
from .player import Player
from .enemy import BasicEnemy, StrongEnemy, FinalBoss
from .cloud import Cloud 
from .satellite import Satellite
from .shield import Shield
from .cinematic import Cinematics
from .levels import LevelManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Invasión Espacial")

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 64)
        self.small_font = pygame.font.SysFont(None, 28)
        
        self.level_manager = LevelManager(self.screen_width, self.screen_height)
        self.current_level = 1
        self.max_levels = 3
        self.level_background = None
        self.load_level_background()

        self.player = Player(self.screen_width // 2, self.screen_height - 70)
        self.enemies = []
        self.create_enemies()

        self.volume_general = 0.5
        self.volume_musica = 0.5
        self.volume_efectos = 0.5
        self.muted = False

        self.score = 0
        self.game_over = False
        self.victory = False
        self.enemy_direction = 1
        self.enemy_move_timer = 0
        self.enemy_move_interval = 15

        self.clouds = []
        self.cloud_spawn_timer = 0
        self.cloud_spawn_interval = 60

        self.satellites = []
        self.satellite_spawn_timer = 0
        self.satellite_spawn_interval_min = 240
        self.satellite_spawn_interval_max = 480
        self.next_satellite_spawn_interval = random.randint(
            self.satellite_spawn_interval_min, 
            self.satellite_spawn_interval_max
        )
        
        self.shields = []
        self.paused = False
        self.pause_menu_state = "main"
        self.pause_buttons = []
        self.game_over_buttons = []
        self.victory_buttons = []
        self.hovered_pause_buttons = set()

        self.cinematics = Cinematics(self.screen_width, self.screen_height)
        self.show_intro_cinematic = True

        base_path = os.path.dirname(__file__)
        self.save_path = os.path.join(base_path, '..', 'savegame.txt')
        self.init_sounds()

    def init_sounds(self):
        try:
            pygame.mixer.init()
            base_path = os.path.dirname(__file__)
            
            self.click_sound = pygame.mixer.Sound(os.path.join(base_path, '..', 'sounds', 'eleccion_menu.mp3'))
            self.hover_sound = pygame.mixer.Sound(os.path.join(base_path, '..', 'sounds', 'seleccionar_menu.mp3'))
            self.damage_sound = pygame.mixer.Sound(os.path.join(base_path, '..', 'sounds', 'daño_recibido_prota.mp3'))
            self.shoot_sound = pygame.mixer.Sound(os.path.join(base_path, '..', 'sounds', 'disparo_protagonista.mp3'))
            self.destroyed_sound = pygame.mixer.Sound(os.path.join(base_path, '..', 'sounds', 'estructura_destruida.mp3'))
            self.death_sound = pygame.mixer.Sound(os.path.join(base_path, '..', 'sounds', 'sonido_muerte_prota.mp3'))
            
            for sound in [self.click_sound, self.hover_sound, self.damage_sound, 
                         self.shoot_sound, self.destroyed_sound, self.death_sound]:
                sound.set_volume(0.5)
                
        except Exception as e:
            print(f"Error cargando sonidos: {e}")

        self.play_level_music()

    def show_level_intro(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  
        
        font = pygame.font.SysFont(None, 72)
        level_text = font.render(f"Nivel {self.current_level}", True, (255, 255, 255))
        text_rect = level_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
        
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(level_text, text_rect)
        pygame.display.flip()
        pygame.time.delay(1500)  # 1.5 segundos

    def play_level_music(self):
        base_path = os.path.dirname(__file__)
        sounds_path = os.path.join(base_path, '..', 'sounds')
        pygame.mixer.music.stop()
        
        music_file = self.level_manager.get_level_music(self.current_level)
        if music_file:
            try:
                pygame.mixer.music.load(os.path.join(sounds_path, music_file))
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(self.volume_musica * self.volume_general)
            except Exception as e:
                print(f"Error cargando música: {e}")

    def load_level_background(self):
        self.level_background = self.level_manager.load_level_background(self.current_level)

    def create_enemies(self):
        self.enemies = self.level_manager.create_enemies(self.current_level)
        self.shields = self.level_manager.create_shields(self.current_level)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.delete_save()
                pygame.quit()
                sys.exit()
    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over and not self.paused and not self.victory:
                    self.player.shoot()
                    if self.shoot_sound:
                        self.shoot_sound.play()
                if event.key == pygame.K_ESCAPE and not self.game_over and not self.victory:
                    if self.paused and self.pause_menu_state in ["options", "sound", "controls"]:
                        self.pause_menu_state = "main"
                    else:
                        self.paused = not self.paused
                        self.pause_menu_state = "main"
    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.paused and not self.game_over and not self.victory:
                    for i, btn_rect in enumerate(self.pause_buttons):
                        if btn_rect.collidepoint(mouse_pos):
                            if self.click_sound:
                                self.click_sound.play()
                            self.handle_pause_menu_click(i)

    def handle_pause_menu_click(self, button_index):
        if self.pause_menu_state == "main":
            if button_index == 0:
                self.resume_game()
            elif button_index == 1:
                self.show_options()
            elif button_index == 2:
                self.go_to_menu()
            elif button_index == 3:
                self.quit_game()
        elif self.pause_menu_state == "options":
            if button_index == 0:
                self.pause_menu_state = "controls"
            elif button_index == 1:
                self.pause_menu_state = "sound"
            elif button_index == 2:
                self.back_to_pause_main()
        elif self.pause_menu_state == "sound":
            if button_index == 0:
                self.toggle_mute()
            elif button_index == 1:
                self.pause_menu_state = "options"
        elif self.pause_menu_state == "controls":
            if button_index == 0:
                self.back_to_pause_main()

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.music.set_volume(0)
            for s in [self.shoot_sound, self.damage_sound, self.death_sound, 
                     self.click_sound, self.hover_sound, self.destroyed_sound]:
                if s: s.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.volume_musica * self.volume_general)
            for s in [self.shoot_sound, self.damage_sound, self.death_sound, 
                     self.click_sound, self.hover_sound, self.destroyed_sound]:
                if s: s.set_volume(self.volume_efectos * self.volume_general)

    def update(self):
        if self.game_over or self.paused or self.victory:
            return

        if not hasattr(self, 'level_shown'):
            self.show_level_intro()
            self.level_shown = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move("left", self.screen_width)
        if keys[pygame.K_RIGHT]:
            self.player.move("right", self.screen_width)

        self.player.update(self.screen_height)

        self.enemy_move_timer += 1
        if self.enemy_move_timer >= self.enemy_move_interval:
            self.enemy_move_timer = 0
            hit_edge = False
            
            for enemy in self.enemies:
                enemy.rect.x += enemy.speed * enemy.direction
                enemy.try_shoot()
                if enemy.rect.right >= self.screen_width or enemy.rect.left <= 0:
                    hit_edge = True

            if hit_edge:
                for enemy in self.enemies:
                    enemy.direction *= -1
                    enemy.rect.y += enemy.move_down_distance

        for enemy in self.enemies:
            enemy.update_bullets(self.screen_height)

        self.check_collisions()

        if self.level_manager.should_spawn_clouds(self.current_level):
            self.cloud_spawn_timer += 1
            if self.cloud_spawn_timer >= self.cloud_spawn_interval:
                self.clouds.append(Cloud(self.screen_width, self.screen_height))
                self.cloud_spawn_timer = 0
            for cloud in self.clouds[:]:
                cloud.update()
                if cloud.is_offscreen(self.screen_width):
                    self.clouds.remove(cloud)

        if self.level_manager.should_spawn_satellites(self.current_level):
            self.satellite_spawn_timer += 1
            if self.satellite_spawn_timer >= self.next_satellite_spawn_interval:
                self.satellites.append(Satellite(self.screen_width, self.screen_height))
                self.satellite_spawn_timer = 0
                self.next_satellite_spawn_interval = random.randint(
                    self.satellite_spawn_interval_min, 
                    self.satellite_spawn_interval_max
                )
            for satellite in self.satellites[:]:
                satellite.update()
                if satellite.is_offscreen(self.screen_width):
                    self.satellites.remove(satellite)

        if not self.enemies:
            if self.current_level < self.max_levels:
                self.current_level += 1
                self.save_progress()
                self.load_level_background()
                self.create_enemies()
                self.play_level_music()
                delattr(self, 'level_shown')
            else:
                self.victory = True

        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.game_over = True
                self.delete_save()
                break

    def check_collisions(self):
        # Colisiones de las balas del jugador con enemigos
        for bullet in self.player.bullets[:]:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height) if hasattr(bullet, 'width') else bullet.rect
            for enemy in self.enemies[:]:
                if bullet_rect.colliderect(enemy.rect):
                    self.player.bullets.remove(bullet)
                    enemy.receive_damage()
                    if enemy.dead:
                        self.enemies.remove(enemy)
                        self.score += 10
                    else:
                        self.score += 5
                    break

        # Colisiones de las balas enemigas con escudos/jugador
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                bullet_rect = bullet.rect if hasattr(bullet, 'rect') else pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
                
                # Con escudos
                for shield in self.shields[:]:
                    if bullet_rect.colliderect(shield.rect):
                        enemy.bullets.remove(bullet)
                        shield.take_damage()
                        if shield.is_destroyed():
                            self.shields.remove(shield)
                            if self.destroyed_sound:
                                self.destroyed_sound.play()
                        break
                        
                # Con jugador
                if bullet_rect.colliderect(self.player.rect):
                    enemy.bullets.remove(bullet)
                    if self.damage_sound:
                        self.damage_sound.play()
                    if self.player.damage_timer == 0:
                        self.player.take_damage()
                        if self.player.lives <= 0:
                            if self.death_sound:
                                self.death_sound.play()
                            self.game_over = True
                            self.delete_save()

    def draw(self):
        if self.level_background:
            self.screen.blit(self.level_background, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        if self.level_manager.should_spawn_clouds(self.current_level):
            for cloud in self.clouds:
                cloud.draw(self.screen)

        if self.level_manager.should_spawn_satellites(self.current_level):
            for satellite in self.satellites:
                satellite.draw(self.screen)

        self.player.draw(self.screen)

        for enemy in self.enemies:
            if isinstance(enemy, FinalBoss):
                health_bar_width = enemy.rect.width
                health_ratio = max(enemy.lives / 20, 0)
                pygame.draw.rect(self.screen, (255, 0, 0), (enemy.rect.x, enemy.rect.y - 15, health_bar_width, 10))
                pygame.draw.rect(self.screen, (0, 255, 0), (enemy.rect.x, enemy.rect.y - 15, int(health_bar_width * health_ratio), 10))
            enemy.draw(self.screen)

        for bullet in self.player.bullets:
            pygame.draw.rect(self.screen, (255, 255, 0), bullet)

        for enemy in self.enemies:
            for bullet in enemy.bullets:
                if hasattr(bullet, "draw"):
                    bullet.draw(self.screen)
                else:
                    pygame.draw.rect(self.screen, (255, 0, 0), bullet)

        lives_text = self.font.render(f"Vidas: {self.player.lives}", True, (255, 255, 255))
        score_text = self.font.render(f"Puntaje: {self.score}", True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 10))
        self.screen.blit(score_text, (self.screen_width - score_text.get_width() - 10, 10))

        for shield in self.shields:
            shield.draw(self.screen)

        if self.paused:
            self.draw_pause_menu()
        if self.game_over:
            self.draw_game_over_menu()
        if self.victory:
            self.draw_victory_menu()

        pygame.display.flip()

    def draw_pause_menu(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("PAUSA", True, (255, 255, 0))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 80))

        if self.pause_menu_state == "main":
            self.pause_buttons = [
                self.draw_button("Continuar", self.screen_width // 2, 250),
                self.draw_button("Opciones", self.screen_width // 2, 330),
                self.draw_button("Menú principal", self.screen_width // 2, 410),
                self.draw_button("Salir", self.screen_width // 2, 490)
            ]
        elif self.pause_menu_state == "options":
            self.pause_buttons = [
                self.draw_button("Controles", self.screen_width // 2, 270),
                self.draw_button("Sonido", self.screen_width // 2, 350),
                self.draw_button("Volver", self.screen_width // 2, 430)
            ]
        elif self.pause_menu_state == "sound":
            overlay = pygame.Surface((self.screen_width - 100, 220))
            overlay.set_alpha(220)
            overlay.fill((30, 30, 30))
            overlay_rect = overlay.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(overlay, overlay_rect)

            self.draw_text("Ajustes de Sonido", self.screen_width // 2, overlay_rect.top + 30, self.font)

            slider_width = 200
            base_x = overlay_rect.left + 50
            base_y = overlay_rect.top + 70

            self.draw_volume_slider("General", base_x, base_y, self.volume_general)
            self.draw_volume_slider("Música", base_x, base_y + 60, self.volume_musica)
            self.draw_volume_slider("Efectos", base_x, base_y + 120, self.volume_efectos)

            self.pause_buttons = [
                self.draw_button("Activar sonido" if self.muted else "Silenciar", self.screen_width // 2, overlay_rect.bottom + 40, 200, 40),
                self.draw_button("Volver", self.screen_width // 2, overlay_rect.bottom + 100, 200, 40)
            ]

    def draw_volume_slider(self, label, x, y, volume):
        self.draw_text(label, x, y, self.small_font)
        slider = pygame.Rect(x + 180, y - 10, 200, 20)
        pygame.draw.rect(self.screen, (100, 100, 100), slider)
        pygame.draw.rect(self.screen, (0, 255, 0), (slider.x, slider.y, int(volume * slider.width), slider.height))
        knob = pygame.Rect(slider.x + int(volume * slider.width) - 5, slider.y - 5, 10, 30)
        pygame.draw.rect(self.screen, (255, 255, 255), knob)

    def draw_text(self, text, x, y, font, color=(255, 255, 255)):
        text_surf = font.render(text, True, color)
        self.screen.blit(text_surf, text_surf.get_rect(center=(x, y)))

    def draw_button(self, text, x, y, w=250, h=60, 
                   bg_color=(0, 0, 255), text_color=(255, 255, 255), 
                   border_color=(0, 255, 0), hover_bg_color=(0, 100, 255), 
                   hover_text_color=(255, 255, 0)):
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (x, y)
        hovered = rect.collidepoint(pygame.mouse.get_pos())

        if hovered and text not in self.hovered_pause_buttons:
            self.hovered_pause_buttons.add(text)
            if self.hover_sound:
                self.hover_sound.play()
        elif not hovered:
            self.hovered_pause_buttons.discard(text)

        color = hover_bg_color if hovered else bg_color
        text_col = hover_text_color if hovered else text_color

        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
        text_surf = self.font.render(text, True, text_col)
        self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

        return rect

    def draw_game_over_menu(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        self.draw_text("GAME OVER", self.screen_width // 2, 100, self.title_font, (255, 0, 0))
        self.draw_text(f"Puntaje: {self.score}", self.screen_width // 2, 180, self.font)

        self.game_over_buttons = [
            self.draw_button("Reiniciar", self.screen_width // 2, 300),
            self.draw_button("Menú principal", self.screen_width // 2, 380),
            self.draw_button("Salir", self.screen_width // 2, 460)
        ]

    def draw_victory_menu(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        self.draw_text("¡VICTORIA FINAL!", self.screen_width // 2, 100, self.title_font, (0, 255, 0))
        self.draw_text("¡Has completado los 3 niveles!", self.screen_width // 2, 180, self.font)
        self.draw_text(f"Puntuación final: {self.score}", self.screen_width // 2, 220, self.font)

        self.victory_buttons = [
            self.draw_button("Menú principal", self.screen_width // 2, 300),
            self.draw_button("Salir", self.screen_width // 2, 380)
        ]

    def resume_game(self):
        self.paused = False

    def show_options(self):
        self.pause_menu_state = "options"

    def back_to_pause_main(self):
        self.pause_menu_state = "main"

    def go_to_menu(self):
        from .menu import Menu
        menu = Menu()
        menu.run()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def save_progress(self):
        try:
            with open(self.save_path, 'w') as f:
                f.write(str(self.current_level))
        except Exception as e:
            print(f"Error guardando progreso: {e}")

    def delete_save(self):
        try:
            if os.path.exists(self.save_path):
                os.remove(self.save_path)
        except Exception as e:
            print(f"Error eliminando progreso: {e}")

    def run(self):
        if self.show_intro_cinematic:
            self.cinematics.show_intro()
            self.show_intro_cinematic = False
        
        self.show_level_intro()
        
        while True:
            self.clock.tick(self.fps)
            self.handle_events()
            self.update()
            self.draw()
            
            if self.game_over or self.victory:
                break
        
        if self.game_over:
            self.cinematics.show_ending(victory=False)
        elif self.victory:
            self.cinematics.show_ending(victory=True)
        
        from .menu import Menu
        menu = Menu()
        menu.run()