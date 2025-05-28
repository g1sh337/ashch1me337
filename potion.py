import pygame

class Potion:
    def __init__(self, x, y):
        self.sheet = pygame.image.load("assets/health_potion.png").convert_alpha()
        self.frames = [
            self.sheet.subsurface(pygame.Rect(i * 128, 0, 128, 128))
            for i in range(8)
        ]
        self.frame_index = 0
        self.animation_speed = 0.15
        self.timer = 0
        self.lifetime = 25  # секунд
        self.rect = pygame.Rect(x, y, 64, 64)  # увеличенная зона подбора
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
        # print("[DRAW] Отрисовка зелья в:", self.rect.topleft)  # можно включить для отладки
