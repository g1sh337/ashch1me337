from safe_loader import safe_load_image, safe_font
import pygame

class LightningSpell:
    def __init__(self, x, y):
        self.sheet = safe_load_image("assets/Sprite-sheet.png")
        self.frames = [
            self.sheet.subsurface(pygame.Rect(i * 256, 0, 256, 128))
            for i in range(4)
        ]
        self.frame_index = 0
        self.animation_speed = 0.1
        self.timer = 0
        self.finished = False
        self.rect = self.frames[0].get_rect(center=(x, y))

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.animation_speed:
            self.timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.finished = True

    def draw(self, surface, camera_offset):
        if not self.finished:
            frame = self.frames[self.frame_index]
            draw_x = self.rect.x - camera_offset.x
            draw_y = self.rect.y - camera_offset.y
            surface.blit(frame, (draw_x, draw_y))
