from safe_loader import safe_load_image, safe_font
import pygame

def scale_frames(sheet, frame_count, frame_w, frame_h, scale):
    return [
        pygame.transform.scale(
            sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
            (int(frame_w * scale), int(frame_h * scale))
        )
        for i in range(frame_count)
    ]

class Ghost:
    def __init__(self, x, y):
        scale = 2

        self.spawn_sheet = safe_load_image("assets/MiniGhost_Spawn.png")
        self.idle_sheet = safe_load_image("assets/MiniGhost_Idle.png")

        self.spawn_frames = scale_frames(self.spawn_sheet, 10, 32, 32, scale)
        self.idle_frames = scale_frames(self.idle_sheet, 8, 32, 32, scale)

        self.current_animation = "spawn"
        self.frame_index = 0
        self.animation_speed = 0.12
        self.animation_timer = 0

        self.rect = self.spawn_frames[0].get_rect(center=(x, y))
        self.speed = 100
        self.active = False
        self.attack_cooldown = 0

    def update(self, dt, player):
        self.animation_timer += dt
        if self.current_animation == "spawn":
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index += 1
                if self.frame_index >= len(self.spawn_frames):
                    self.current_animation = "idle"
                    self.frame_index = 0
                    self.active = True
        elif self.current_animation == "idle":
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.idle_frames)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if self.active:
            direction = pygame.math.Vector2(
                player.rect.centerx - self.rect.centerx,
                player.rect.centery - self.rect.centery
            )
            if direction.length() > 0:
                direction.normalize_ip()
                self.rect.x += direction.x * self.speed * dt
                self.rect.y += direction.y * self.speed * dt

            if self.rect.colliderect(player.rect) and self.attack_cooldown <= 0:
                player.take_damage(1)
                self.attack_cooldown = 1.0

    def draw(self, surface, camera_offset):
        if self.current_animation == "spawn":
            frame = self.spawn_frames[min(self.frame_index, len(self.spawn_frames) - 1)]
        else:
            frame = self.idle_frames[self.frame_index]
        surface.blit(frame, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))
