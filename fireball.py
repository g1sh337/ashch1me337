from safe_loader import safe_load_image, safe_font
import pygame

class Fireball:
    def __init__(self, x, y, direction):
        original = safe_load_image("assets/fireball.png")
        self.image_original = pygame.transform.scale(original, (32, 32))
        self.image = self.image_original
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction.normalize()
        self.speed = 500
        self.lifetime = 2  
        self.timer = 0

        
        angle = -self.direction.angle_to(pygame.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.image_original, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt
        self.timer += dt

    def draw(self, surface, camera_offset):
        surface.blit(self.image, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))