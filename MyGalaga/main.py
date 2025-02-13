import pygame
import sys
import random
import math
from typing import List, Tuple
from enum import Enum

# Initialize Pygame and its mixer for sound
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Game settings
PLAYER_SPEED = 5
BULLET_SPEED = 8
ENEMY_SPEED = 3
DIVE_SPEED = 5
PLAYER_LIVES = 3

class GameState(Enum):
    MENU = 1
    ROUND1 = 2
    ROUND2 = 3
    GAME_OVER = 4

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 2.0)
        self.brightness = random.randint(100, 255)
        
    def update(self):
        self.y = (self.y + self.speed) % SCREEN_HEIGHT
        self.brightness = max(100, min(255, self.brightness + random.randint(-10, 10)))
        
    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 1)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((38, 38), pygame.SRCALPHA)

        # Classic Galaga player ship design
        pygame.draw.polygon(self.image, (255, 255, 255), [(19, 0), (0, 38), (38, 38)])  # White triangle
        pygame.draw.polygon(self.image, (0, 0, 255), [(19, 5), (5, 33), (33, 33)])  # Blue inner triangle
        pygame.draw.polygon(self.image, (255, 0, 0), [(19, 10), (10, 28), (28, 28)])  # Red center

        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.captured = False
        self.dual_shooting = False
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = PLAYER_LIVES
        self.respawning = False
        self.respawn_timer = 0
        self.exploding = False
        self.explosion_timer = 0

    def explode(self):
        self.exploding = True
        self.explosion_timer = 0

    def start_respawn(self):
        self.respawning = True
        self.respawn_timer = 0
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT + 50  # Start below screen

    def update(self):
        if self.exploding:
            self.explosion_timer += 1
            if self.explosion_timer >= 60:  # 1 second explosion
                self.exploding = False
                self.start_respawn()
        elif self.respawning:
            self.respawn_timer += 1
            # Move ship up from bottom
            if self.respawn_timer < 60:
                self.rect.y -= 2
            else:
                self.respawning = False
        elif not self.captured:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.rect.left > 0:
                self.rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
                self.rect.x += PLAYER_SPEED

    def draw_explosion(self, screen):
        if self.exploding:
            radius = self.explosion_timer // 2
            color = (255, 200 - self.explosion_timer * 3, 0)
            pygame.draw.circle(screen, color, self.rect.center, radius)

    def shoot(self) -> List['Bullet']:
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullets = []
            bullets.append(Bullet(self.rect.centerx, self.rect.top))
            if self.dual_shooting:
                bullets.append(Bullet(self.rect.centerx - 20, self.rect.top))
                bullets.append(Bullet(self.rect.centerx + 20, self.rect.top))
            return bullets
        return []

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 12))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        
    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, can_shoot=False):
        super().__init__()
        self.image = pygame.Surface((36, 36), pygame.SRCALPHA)

        # Spaceship-like enemy design
        # Main body
        pygame.draw.polygon(self.image, (255, 0, 0), [(18, 0), (0, 36), (36, 36)])  # Red triangle
        # Cockpit
        pygame.draw.polygon(self.image, (0, 255, 0), [(18, 10), (10, 26), (26, 26)])  # Green center
        # Wings
        pygame.draw.polygon(self.image, (255, 255, 0), [(0, 18), (18, 18), (0, 36)])  # Left wing
        pygame.draw.polygon(self.image, (255, 255, 0), [(36, 18), (18, 18), (36, 36)])  # Right wing

        self.rect = self.image.get_rect()
        self.start_x = x
        self.start_y = y
        self.rect.x = x
        self.rect.y = y
        self.can_shoot = can_shoot
        self.diving = False
        self.dive_timer = 0
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randint(2000, 4000)  # Shooting delay

    def update(self):
        if self.diving:
            self._update_diving()
        else:
            self._update_formation()

        self.rect.x = int(self.rect.x)
        self.rect.y = int(self.rect.y)

        if self.can_shoot and random.random() < 0.01:  # 1% chance to shoot each frame
            self.shoot()

    def _update_formation(self):
        # Simple horizontal movement
        self.rect.x = self.start_x + math.sin(pygame.time.get_ticks() * 0.002) * 50

    def _update_diving(self):
        self.dive_timer += 1
        self.rect.y += 5
        if self.dive_timer > 60:
            self.diving = False
            self.rect.x = self.start_x
            self.rect.y = self.start_y

    def start_dive(self):
        self.diving = True
        self.dive_timer = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            game.enemy_bullets.add(bullet)
            game.all_sprites.add(bullet)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 12))
        self.image.fill((255, 255, 0))  # Yellow bullet
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y

    def update(self):
        self.rect.y += BULLET_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class CaptureBeam(pygame.sprite.Sprite):
    def __init__(self, enemy, target_pos):
        super().__init__()
        self.image = pygame.Surface((4, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.image.fill((255, 0, 255, 128))  # Semi-transparent purple
        self.rect = self.image.get_rect()
        self.enemy = enemy
        self.rect.centerx = enemy.rect.centerx
        self.rect.top = enemy.rect.bottom

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced Galaga")
        self.clock = pygame.time.Clock()
        self.score = 0
        self.round = 1
        self.state = GameState.MENU
        self.stars = [Star() for _ in range(100)]
        
        # Create start button
        button_width = 200
        button_height = 50
        button_x = (SCREEN_WIDTH - button_width) // 2
        button_y = (SCREEN_HEIGHT - button_height) // 2
        self.start_button = Button(button_x, button_y, button_width, button_height, "Start Game", GREEN)
        
        self.reset_game()

    def reset_game(self):
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.capture_beams = pygame.sprite.Group()
        
        self.player = Player()
        self.players.add(self.player)
        self.all_sprites.add(self.player)
        
        self.spawn_enemies()

    def spawn_enemies(self):
        for row in range(2):
            for col in range(5):  # Adjusted to 5 enemies per row
                x = col * 120 + 100  # Centered across the screen
                y = row * 60 + 50
                enemy = Enemy(x, y, self.state == GameState.ROUND2)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

    def reset_enemies(self):
        # Store current enemies
        remaining_enemies = len(self.enemies)
        # Remove all enemies
        self.enemies.empty()
        # Respawn the same number of enemies in formation
        for row in range(2):
            for col in range(5):
                if remaining_enemies <= 0:
                    break
                x = col * 120 + 100
                y = row * 60 + 50
                enemy = Enemy(x, y, self.state == GameState.ROUND2)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
                remaining_enemies -= 1
            if remaining_enemies <= 0:
                break

    def update_stars(self):
        for star in self.stars:
            star.update()

    def draw_stars(self):
        for star in self.stars:
            star.draw(self.screen)

    def handle_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button.is_clicked(event.pos):
                    self.state = GameState.ROUND1
                    self.reset_game()
        
        self.screen.fill(BLACK)
        self.update_stars()
        self.draw_stars()
        self.start_button.draw(self.screen)
        
        # Draw title
        font = pygame.font.Font(None, 74)
        title = font.render("GALAGA", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        self.screen.blit(title, title_rect)
        
        pygame.display.flip()
        return True

    def handle_game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button.is_clicked(event.pos):
                    self.state = GameState.MENU
                    self.score = 0
                    self.round = 1
        
        self.screen.fill(BLACK)
        self.update_stars()
        self.draw_stars()
        
        # Draw game over text and score
        font = pygame.font.Font(None, 74)
        game_over = font.render("Game Over", True, WHITE)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        
        self.screen.blit(game_over, game_over_rect)
        self.screen.blit(score_text, score_rect)
        
        # Change button text to "Play Again"
        self.start_button.text = "Play Again"
        self.start_button.draw(self.screen)
        
        pygame.display.flip()
        return True

    def handle_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.player.captured and not self.player.exploding and not self.player.respawning:
                    bullets = self.player.shoot()
                    for bullet in bullets:
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)

        # Update
        self.update_stars()
        self.all_sprites.update()

        # Random chance for an enemy to dive
        if random.random() < 0.01:  # 1% chance per frame
            enemy = random.choice(self.enemies.sprites())
            if not enemy.diving:
                enemy.start_dive()

        # Handle collisions only if player is not exploding or respawning
        if not self.player.exploding and not self.player.respawning:
            # Enemy hits player
            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if hits:
                self.player.lives -= 1
                self.player.explode()
                if self.player.lives <= 0:
                    self.state = GameState.GAME_OVER
                else:
                    self.reset_enemies()

            # Enemy bullet hits player
            hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
            if hits:
                self.player.lives -= 1
                self.player.explode()
                if self.player.lives <= 0:
                    self.state = GameState.GAME_OVER
                else:
                    self.reset_enemies()

        # Bullet hits enemy
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        for enemy in hits:
            self.score += 10

        # Check if round is complete
        if len(self.enemies) == 0:
            if self.state == GameState.ROUND1:
                self.state = GameState.ROUND2
                self.round = 2
                self.spawn_enemies()
            else:
                self.state = GameState.GAME_OVER

        # Draw
        self.screen.fill(BLACK)
        self.draw_stars()
        self.all_sprites.draw(self.screen)
        
        # Draw explosion if player is exploding
        if self.player.exploding:
            self.player.draw_explosion(self.screen)

        # Draw score and lives
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        lives_text = font.render(f'Lives: {self.player.lives}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))

        pygame.display.flip()
        return True

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            if self.state == GameState.MENU:
                running = self.handle_menu()
            elif self.state == GameState.GAME_OVER:
                running = self.handle_game_over()
            else:  # ROUND1 or ROUND2
                running = self.handle_game()

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()
