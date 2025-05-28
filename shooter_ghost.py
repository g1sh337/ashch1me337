import pygame
from ghost import scale_frames
from damage_number import DamageNumber

class ShooterGhost:
    def __init__(self, x, y):
        scale = 2
        self.idle_sheet = pygame.image.load("assets/ghost walks 2.png").convert_alpha()
        self.idle_frames = scale_frames(self.idle_sheet, 12, 32, 32, scale)

        self.frame_index = 0
        self.animation_speed = 0.15
        self.animation_timer = 0

        self.rect = self.idle_frames[0].get_rect(center=(x, y))
        self.speed = 60
        self.shoot_cooldown = 0
        self.projectiles = []
        self.attack_range = 200

    def update(self, dt, player):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.idle_frames)

        distance = pygame.Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery
        )

        if distance.length() > self.attack_range:
            direction = distance.normalize()
            self.rect.x += direction.x * self.speed * dt
            self.rect.y += direction.y * self.speed * dt

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        elif distance.length() <= self.attack_range:
            direction = distance.normalize()
            self.projectiles.append(ShooterProjectile(self.rect.centerx, self.rect.centery, direction))
            self.shoot_cooldown = 2.0

        for p in self.projectiles[:]:
            p.update(dt)
            if p.rect.colliderect(player.rect):
                player.take_damage(2, sprite="2HP.png")
                self.projectiles.remove(p)
            elif not (0 <= p.rect.x <= 2000 and 0 <= p.rect.y <= 2000):
                self.projectiles.remove(p)

    def draw(self, surface, camera_offset):
        frame = self.idle_frames[self.frame_index]
        surface.blit(frame, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))
        for p in self.projectiles:
            p.draw(surface, camera_offset)


class ShooterProjectile:
    def __init__(self, x, y, direction):
        self.direction = direction.normalize()
        self.speed = 300
        self.rect = pygame.Rect(x, y, 16, 16)

        try:
            if abs(self.direction.x) > abs(self.direction.y):
                if self.direction.x > 0:
                    self.image = pygame.image.load("assets/eye_right.png").convert_alpha()
                else:
                    self.image = pygame.image.load("assets/eye_left.png").convert_alpha()
            else:
                if self.direction.y > 0:
                    self.image = pygame.image.load("assets/eye_down.png").convert_alpha()
                else:
                    self.image = pygame.image.load("assets/eye_up.png").convert_alpha()
        except Exception as e:
            print("Failed to load eye projectile sprite:", e)
            self.image = pygame.Surface((8, 8))
            self.image.fill((255, 0, 0))

        self.image = pygame.transform.scale(self.image, (32, 32))

    def update(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt

    def draw(self, surface, camera_offset):
        surface.blit(self.image, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))
