import pygame
import random
from ghost import Ghost

class BossPepe:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 32, 32)

        self.sheet_right = pygame.image.load("assets/boss_pepe_walk_right.png").convert_alpha()
        self.sheet_left = pygame.image.load("assets/boss_pepe_walk_left.png").convert_alpha()
        self.summon_right = pygame.image.load("assets/boss_pepe_summon_right.png").convert_alpha()
        self.summon_left = pygame.image.load("assets/boss_pepe_summon_left.png").convert_alpha()

        self.scale = 2
        self.speed = 100
        self.facing = "right"
        self.frames = self.load_frames(self.sheet_right)
        self.summon_frames = self.load_frames(self.summon_right)
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.15

        self.mode = "walk"
        self.summon_cooldown = 3
        self.summon_timer = 0
        self.ghosts_summoned = 0

        self.active = True
        self.ghosts_killed = 0
        self.summon_duration = 1.5
        self.summoning = False
        self.summon_time = 0

        self.running_away = False

    def load_frames(self, sheet):
        frame_w = sheet.get_width() // 10
        frame_h = sheet.get_height()
        return [
            pygame.transform.scale(sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
                                   (frame_w * self.scale, frame_h * self.scale))
            for i in range(10)
        ]

    def update(self, dt, player, ghosts):
        if not self.active:
            return

        if self.ghosts_killed >= 30:
            self.running_away = True
            self.mode = "run"

        self.anim_timer += dt

        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(self.frames)

        if self.running_away:
            self.rect.x += self.speed * dt
            if self.rect.x > 2000:
                self.active = False
            return

        self.summon_timer += dt

        if self.summoning:
            self.summon_time += dt
            if self.summon_time >= self.summon_duration:
                self.summoning = False
                self.summon_time = 0
                for _ in range(3):
                    ghost_x = self.rect.centerx + random.randint(-50, 50)
                    ghost_y = self.rect.centery + random.randint(-50, 50)
                    ghosts.append(Ghost(ghost_x, ghost_y))
        elif self.summon_timer >= self.summon_cooldown:
            self.summon_timer = 0
            self.summoning = True
            self.mode = "summon"
        else:
            self.mode = "walk"
            direction = pygame.Vector2(player.rect.centerx - self.rect.centerx,
                                       player.rect.centery - self.rect.centery)
            if direction.length() > 100:
                direction.normalize_ip()
                self.rect.x += direction.x * self.speed * dt * 0.5
                self.rect.y += direction.y * self.speed * dt * 0.5
                self.facing = "right" if direction.x >= 0 else "left"
            if self.rect.colliderect(player.rect):
                player.take_damage(5)

    def draw(self, surface, camera_offset):
        if not self.active:
            return
        if self.mode == "summon" or self.summoning:
            frames = self.summon_frames if self.facing == "right" else self.load_frames(self.summon_left)
        else:
            frames = self.frames if self.facing == "right" else self.load_frames(self.sheet_left)
        frame = frames[self.anim_index % len(frames)]
        surface.blit(frame, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))

    def notify_ghost_killed(self):
        self.ghosts_killed += 1
