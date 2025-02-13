import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED = 2
ENEMY_BULLET_SPEED = 5
ENEMY_SHOOT_CHANCE = 0.01  # 1% chance to shoot each frame
STAR_COUNT = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaga Clone")
clock = pygame.time.Clock()

# Load images
PLAYER_SHIP = pygame.image.load(os.path.join('assets', 'player_ship.png'))
ENEMY_SHIP = pygame.image.load(os.path.join('assets', 'enemy_ship.png'))

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.randint(1, 3)
        self.brightness = random.randint(50, 255)
        
    def update(self):
        self.y = (self.y + self.speed) % SCREEN_HEIGHT
        self.brightness = random.randint(50, 255)
    
    def draw(self, surface):
        pygame.draw.circle(surface, (self.brightness, self.brightness, self.brightness), 
                         (self.x, self.y), 1)

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 50)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def show_start_screen(screen, stars):
    # Create start button
    button_width = 200
    button_height = 60
    start_button = Button(
        SCREEN_WIDTH//2 - button_width//2,
        SCREEN_HEIGHT//2 - button_height//2,
        button_width,
        button_height,
        "START",
        BLUE
    )
    
    # Title font
    title_font = pygame.font.Font(None, 100)
    title_text = title_font.render("GALAGA", True, CYAN)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(event.pos):
                    waiting = False
        
        # Update and draw stars
        for star in stars:
            star.update()
        
        screen.fill(BLACK)
        
        # Draw stars
        for star in stars:
            star.draw(screen)
            
        # Draw title
        screen.blit(title_text, title_rect)
        
        # Draw button
        start_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_SHIP
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.lives = 3
        
    def respawn(self):
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PLAYER_SPEED

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, can_shoot=False):
        super().__init__()
        self.image = ENEMY_SHIP
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.distance = 0
        self.cycles = 0
        self.can_shoot = can_shoot
        
    def shoot(self, enemy_bullets, all_sprites):
        if self.can_shoot and random.random() < ENEMY_SHOOT_CHANCE:
            bullet = Bullet(self.rect.centerx, self.rect.bottom, -ENEMY_BULLET_SPEED, YELLOW)
            enemy_bullets.add(bullet)
            all_sprites.add(bullet)
        
    def update(self):
        self.rect.x += ENEMY_SPEED * self.direction
        self.distance += ENEMY_SPEED
        if self.distance >= 100:
            self.direction *= -1
            self.distance = 0
            self.rect.y += 20

        if self.rect.top > SCREEN_HEIGHT and self.cycles < 1:
            self.rect.y = -50
            self.rect.x = random.randint(50, SCREEN_WIDTH - 50)
            self.cycles += 1
        elif self.rect.top > SCREEN_HEIGHT and self.cycles >= 1:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = speed
        
    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

def create_enemies(round_number, all_sprites, enemies):
    enemies.empty()
    num_enemies = 12 if round_number == 1 else 8
    can_shoot = round_number > 1
    
    rows = 3 if round_number == 1 else 2
    cols = 6 if round_number == 1 else 4
    
    for row in range(rows):
        for col in range(cols):
            enemy = Enemy(col * 80 + 100, row * 60 + 50, can_shoot)
            all_sprites.add(enemy)
            enemies.add(enemy)

def show_game_over(screen, score):
    font = pygame.font.Font(None, 74)
    text = font.render('Game Over', True, RED)
    score_text = font.render(f'Final Score: {score}', True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
    screen.blit(text, text_rect)
    screen.blit(score_text, score_rect)
    pygame.display.flip()
    pygame.time.wait(3000)

def main():
    # Create starfield
    stars = [Star() for _ in range(STAR_COUNT)]
    
    # Show start screen
    show_start_screen(screen, stars)
    
    all_sprites = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    
    player = Player()
    all_sprites.add(player)
    
    round_number = 1
    create_enemies(round_number, all_sprites, enemies)
    
    running = True
    score = 0
    game_over = False
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.top, BULLET_SPEED, CYAN)
                    all_sprites.add(bullet)
                    player_bullets.add(bullet)
        
        if not game_over:
            # Update stars
            for star in stars:
                star.update()
            
            all_sprites.update()
            
            # Handle enemy shooting
            for enemy in enemies:
                enemy.shoot(enemy_bullets, all_sprites)
            
            # Check for enemy destruction
            hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
            for hit in hits:
                score += 10
            
            # Check for player hit by bullets
            if pygame.sprite.spritecollide(player, enemy_bullets, True):
                player.lives -= 1
                if player.lives <= 0:
                    game_over = True
                else:
                    player.respawn()
            
            # Check if all enemies destroyed
            if len(enemies) == 0:
                round_number += 1
                if round_number <= 2:
                    create_enemies(round_number, all_sprites, enemies)
                else:
                    game_over = True
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw stars
        for star in stars:
            star.draw(screen)
        
        all_sprites.draw(screen)
        
        # Draw score and lives
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        lives_text = font.render(f'Lives: {player.lives}', True, WHITE)
        round_text = font.render(f'Round: {round_number}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(round_text, (10, 70))
        
        if game_over:
            show_game_over(screen, score)
            running = False
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
