from safe_loader import safe_load_image, safe_font
import pygame
from ghost import scale_frames

class TankGhost:
    def __init__(self, x, y):
        scale = 2
        self.idle_sheet = safe_load_image("assets/Ghost walks.png")
        self.idle_frames = scale_frames(self.idle_sheet, 12, 32, 32, scale)

        self.frame_index = 0
        self.animation_speed = 0.15
        self.animation_timer = 0

        self.rect = self.idle_frames[0].get_rect(center=(x, y))
        self.speed = 50  
        self.hp = 5
        self.attack_cooldown = 0

    def update(self, dt, player):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.idle_frames)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        direction = pygame.Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery
        )
        if direction.length() > 0:
            direction.normalize_ip()
            self.rect.x += direction.x * self.speed * dt
            self.rect.y += direction.y * self.speed * dt

        if self.rect.colliderect(player.rect) and self.attack_cooldown <= 0:
            player.take_damage(1)
            self.attack_cooldown = 1.5

    def draw(self, surface, camera_offset):
        frame = self.idle_frames[self.frame_index]
        surface.blit(frame, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))
