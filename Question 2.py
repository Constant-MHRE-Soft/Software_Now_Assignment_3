import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Clock for FPS control
clock = pygame.time.Clock()

# Global colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Load images (dummy placeholders for simplicity)
HERO_IMAGE = pygame.Surface((50, 50))
HERO_IMAGE.fill(GREEN)
ENEMY_IMAGE = pygame.Surface((50, 50))
ENEMY_IMAGE.fill(RED)
PROJECTILE_IMAGE = pygame.Surface((10, 10))
PROJECTILE_IMAGE.fill(WHITE)

# Fonts for score display
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)

# Camera class for dynamic scrolling
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + int(SCREEN_WIDTH / 2)
        y = -target.rect.y + int(SCREEN_HEIGHT / 2)
        self.camera = pygame.Rect(x, y, self.width, self.height)

# Player class for handling hero movements
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = HERO_IMAGE
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - 150
        self.speed = 5
        self.jump_speed = -15
        self.gravity = 1
        self.vel_y = 0
        self.health = 100
        self.lives = 3
        self.score = 0  # Player score initialized to 0
        self.on_ground = False

    def update(self, platforms):
        # Player movement (running)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Jumping
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_speed

        # Apply gravity
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Check for collision with ground/platform
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                self.on_ground = True
                self.vel_y = 0
                self.rect.bottom = platform.rect.top

    def shoot(self, projectiles):
        projectile = Projectile(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2)
        projectiles.add(projectile)

# Projectile class for hero's attack
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = PROJECTILE_IMAGE
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > SCREEN_WIDTH:
            self.kill()  # Remove projectile if out of screen bounds

# Enemy class for the human enemies
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ENEMY_IMAGE
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.randint(2, 4)
        self.health = 50

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# Platform class for ground and platforms
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Collectible class for health and life boosts
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.kind = kind  # Type of collectible ('health' or 'life')
        if self.kind == 'health':
            self.image.fill(GREEN)
        else:
            self.image.fill(RED)

# Main game function
def main_game():
    # Create groups for sprites
    player_group = pygame.sprite.Group()
    projectile_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    collectible_group = pygame.sprite.Group()

    # Create player and add to group
    player = Player()
    player_group.add(player)

    # Create platforms (ground)
    ground = Platform(0, SCREEN_HEIGHT - 50, 20000, 50)
    platform_group.add(ground)

    # Create camera object
    camera = Camera(SCREEN_WIDTH * 3, SCREEN_HEIGHT)

    # Create enemies and collectibles
    for i in range(10):
        enemy = Enemy(random.randint(900, 1500), SCREEN_HEIGHT - 100)
        enemy_group.add(enemy)

        collectible = Collectible(random.randint(500, 1500), SCREEN_HEIGHT - 100, random.choice(['health', 'life']))
        collectible_group.add(collectible)

    running = True
    while running:
        # FPS control
        clock.tick(60)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    player.shoot(projectile_group)

        # Update player, enemies, projectiles
        player_group.update(platform_group)
        projectile_group.update()
        enemy_group.update()
        collectible_group.update()

        # Check for collisions between projectiles and enemies
        for projectile in pygame.sprite.groupcollide(projectile_group, enemy_group, True, True):
            player.score += 10  # Add 10 points for each enemy defeated

        # Check for collisions between player and collectibles
        for collectible in pygame.sprite.spritecollide(player, collectible_group, True):
            if collectible.kind == 'health':
                player.score += 5  # Add 5 points for health collectible
            elif collectible.kind == 'life':
                player.score += 20  # Add 20 points for life collectible

        # Update camera to follow player
        camera.update(player)

        # Drawing all elements
        screen.fill(BLACK)
        for platform in platform_group:
            screen.blit(platform.image, camera.apply(platform))
        for collectible in collectible_group:
            screen.blit(collectible.image, camera.apply(collectible))
        for enemy in enemy_group:
            screen.blit(enemy.image, camera.apply(enemy))
        for projectile in projectile_group:
            screen.blit(projectile.image, camera.apply(projectile))
        screen.blit(player.image, camera.apply(player))

        # Display score on screen
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(score_text, (20, 20))

        # Update the display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main_game()
