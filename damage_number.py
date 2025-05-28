import pygame

class DamageNumber:
    def __init__(self, x, y, sprite_path="1HP.png"):
        self.sheet = pygame.image.load(f"assets/{sprite_path}").convert_alpha()
        self.frames = [
            self.sheet.subsurface(pygame.Rect(i * 32, 0, 32, 32))
            for i in range(self.sheet.get_width() // 32)
        ]
        self.frame_index = 0
        self.animation_speed = 0.1
        self.timer = 0
        self.pos = pygame.Vector2(x, y)
        self.offset = 0
        self.finished = False

    def update(self, dt):
        self.timer += dt
        self.offset -= 20 * dt
        if self.timer >= self.animation_speed:
            self.timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.finished = True

    def draw(self, surface, camera_offset):
        if not self.finished:
            frame = self.frames[self.frame_index]
            draw_x = self.pos.x - camera_offset.x
            draw_y = self.pos.y - camera_offset.y + self.offset
            surface.blit(frame, (draw_x, draw_y))
