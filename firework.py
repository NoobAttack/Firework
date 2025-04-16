import pygame
import random
import math
import sys


# Initialize Pygame
pygame.init()
pygame.display.set_caption("Fireworks Display")

# Screen dimensions
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
STAR_COLORS = [
    (255, 215, 0),
    (255, 69, 0),
    (0, 191, 255),
    (50, 205, 50),
    (238, 130, 238)
]

# Explosion parameters
NUM_PARTICLES = 50
PARTICLE_LIFESPAN = 100
EXPLOSION_SPEED = 5
GRAVITY = 0.1

class Rocket:
    def __init__(self):
        # Start from bottom of screen at random x position
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT
        # Initial velocity
        self.speed = random.uniform(15, 20)
        self.angle = -math.pi / 2 + random.uniform(-0.2, 0.2)  # Mostly upward
        # Trail properties
        self.trail = []
        self.color = (255, 255, 255)  # White trail for rocket
        self.exploded = False
        # Target height for explosion
        self.target_height = random.randint(HEIGHT // 4, 3 * HEIGHT // 4)
        # Smoke particles for visual effect
        self.smoke_particles = []

    def update(self):
        # Update position based on angle and speed
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Add smoke effect with a 50% chance each frame
        if random.random() < 0.5:
            self.smoke_particles.append({
                'x': self.x + random.uniform(-2, 2),
                'y': self.y + random.uniform(-2, 2),
                'alpha': 255,
                'size': random.uniform(2, 3)
            })

        # Update smoke particles
        for smoke in self.smoke_particles[:]:
            smoke['alpha'] -= 5
            if smoke['alpha'] <= 0:
                self.smoke_particles.remove(smoke)

        # Update trail points
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

        # Check if rocket has reached the target height to explode
        if self.y <= self.target_height:
            self.exploded = True
            return True
        return False

    def draw(self, surface):
        # Draw smoke particles
        for smoke in self.smoke_particles:
            pygame.draw.circle(
                surface,
                (100, 100, 100),
                (int(smoke['x']), int(smoke['y'])),
                int(smoke['size'])
            )
        # Draw trail points with fading effect
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            pygame.draw.circle(surface, self.color, (int(tx), int(ty)), 2)
        # Draw the rocket
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(2, EXPLOSION_SPEED)
        self.lifespan = PARTICLE_LIFESPAN
        self.color = color
        self.gravity_effect = random.uniform(0.05, GRAVITY)
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed + self.gravity_effect

        self.lifespan -= 1
        # Gradually darken the color over time
        self.color = (
            max(0, self.color[0] - 2),
            max(0, self.color[1] - 2),
            max(0, self.color[2] - 2),
        )

    def draw(self, surface):
        # Draw the particle trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = max(255 - (i * 25), 0)
            pygame.draw.circle(surface, self.color, (int(tx), int(ty)), 2)
        # Draw the particle itself with a bit of sparkle
        if self.lifespan > 0:
            sparkle_factor = random.choice([0, 50, 100])
            spark_color = (
                min(255, self.color[0] + sparkle_factor),
                min(255, self.color[1] + sparkle_factor),
                min(255, self.color[2] + sparkle_factor),
            )
            pygame.draw.circle(surface, spark_color, (int(self.x), int(self.y)), 4)

def main():
    global NUM_PARTICLES, EXPLOSION_SPEED, PARTICLE_LIFESPAN

    clock = pygame.time.Clock()
    particles = []
    rockets = []
    last_rocket_time = 0
    rocket_interval = 30  # Frames between rocket launches

    running = True

    # Define a custom event for quitting after 30 seconds
    QUIT_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(QUIT_EVENT, 15000)

    while running:
        current_time = pygame.time.get_ticks()
        screen.fill(BLACK)

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == QUIT_EVENT:
                print("15 seconds elapsed. Quitting the game...")
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    NUM_PARTICLES += 10
                elif event.key == pygame.K_DOWN:
                    NUM_PARTICLES = max(10, NUM_PARTICLES - 10)
                elif event.key == pygame.K_LEFT:
                    EXPLOSION_SPEED = max(2, EXPLOSION_SPEED - 1)
                elif event.key == pygame.K_RIGHT:
                    EXPLOSION_SPEED += 1
                elif event.key == pygame.K_w:
                    PARTICLE_LIFESPAN += 10
                elif event.key == pygame.K_s:
                    PARTICLE_LIFESPAN = max(10, PARTICLE_LIFESPAN - 10)
                elif event.key == pygame.K_SPACE:
                    rockets.append(Rocket())
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Automatically launch rockets on random intervals
        if current_time - last_rocket_time > rocket_interval:
            rockets.append(Rocket())
            last_rocket_time = current_time
            rocket_interval = random.randint(20, 60)

        # Update and draw rockets; trigger explosion when necessary
        for rocket in rockets[:]:
            if rocket.update():
                color = random.choice(STAR_COLORS)
                particles.extend([Particle(rocket.x, rocket.y, color) for _ in range(NUM_PARTICLES)])
                rockets.remove(rocket)
            else:
                rocket.draw(screen)

        # Update and draw explosion particles
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.lifespan <= 0:
                particles.remove(particle)

        # Display control parameters
        font = pygame.font.Font(None, 24)
        params_text = font.render(
            f"Particles: {NUM_PARTICLES}, Speed: {EXPLOSION_SPEED}, Lifespan: {PARTICLE_LIFESPAN}",
            True,
            WHITE
        )
        screen.blit(params_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    # Cleanup and exit after leaving the loop
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
