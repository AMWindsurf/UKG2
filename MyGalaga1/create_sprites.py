import pygame
import os

# Initialize Pygame
pygame.init()

def create_player_ship():
    size = (40, 50)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    
    # Ship color
    ship_color = (0, 255, 255)  # Cyan
    
    # Draw the ship
    points = [(20, 0), (0, 50), (20, 40), (40, 50)]
    pygame.draw.polygon(surface, ship_color, points)
    
    return surface

def create_enemy_ship():
    size = (40, 40)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    
    # Ship color
    ship_color = (255, 0, 100)  # Pink
    
    # Draw the ship (more alien-like)
    # Main body
    pygame.draw.ellipse(surface, ship_color, (5, 15, 30, 20))
    # Top part
    pygame.draw.ellipse(surface, ship_color, (15, 5, 10, 15))
    # Wings
    pygame.draw.polygon(surface, ship_color, [(0, 20), (5, 20), (5, 30), (0, 35)])
    pygame.draw.polygon(surface, ship_color, [(35, 20), (40, 20), (40, 35), (35, 30)])
    
    return surface

# Create assets directory if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')

# Create and save player ship
player_ship = create_player_ship()
pygame.image.save(player_ship, 'assets/player_ship.png')

# Create and save enemy ship
enemy_ship = create_enemy_ship()
pygame.image.save(enemy_ship, 'assets/enemy_ship.png')

pygame.quit()
