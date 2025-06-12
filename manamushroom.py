from safe_loader import safe_load_image, safe_font
import pygame

class ManaMushroom:
    def __init__(self, x, y):
        self.sheet = safe_load_image("assets/managrib.png")
        self.frames = [
            self.sheet.subsurface(pygame.Rect(i * 128, 0, 128, 128))
            for i in range(5)
        ]
        self.frame_index = 0
        self.animation_speed = 0.15
        self.timer = 0
        self.lifetime = 25  
        self.rect = self.frames[0].get_rect(topleft=(x, y))
        self.active = True

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.animation_speed:
            self.timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False

    def draw(self, surface, camera_offset):
        if not self.active:
            return
        frame = self.frames[self.frame_index]
        surface.blit(frame, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))
