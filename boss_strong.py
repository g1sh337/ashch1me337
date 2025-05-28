import pygame
import random
from ghost import Ghost

class BossStrong:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 64, 64)

        self.walk_right_sheet = pygame.image.load("assets/strong_boss_walk_right.png").convert_alpha()
        self.walk_left_sheet = pygame.image.load("assets/strong_boss_walk_left.png").convert_alpha()
        self.attack_right_sheet = pygame.image.load("assets/strong_boss_attack_right.png").convert_alpha()
        self.attack_left_sheet = pygame.image.load("assets/strong_boss_attack_left.png").convert_alpha()

        self.hp_bar_sheet = pygame.image.load("assets/bosshp.png").convert_alpha()
        self.hp_bar_frames = self.load_hp_bar_frames(self.hp_bar_sheet, 11, scale=2)

        self.scale = 2
        self.speed = 60
        self.facing = "right"

        self.walk_right_frames = self.load_frames(self.walk_right_sheet, 8)
        self.walk_left_frames = self.load_frames(self.walk_left_sheet, 8)
        self.attack_right_frames = self.load_frames(self.attack_right_sheet, 11)
        self.attack_left_frames = self.load_frames(self.attack_left_sheet, 11)

        self.walk_anim_index = 0
        self.attack_anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.15

        self.mode = "walk"
        self.attack_cooldown = 2
        self.attack_timer = 0
        self.attack_duration = 1
        self.attacking = False
        self.attack_time = 0

        self.summon_cooldown = 5
        self.summon_timer = 0
        self.hp = 40
        self.max_hp = 40
        self.active = True

    def load_frames(self, sheet, frame_count):
        frame_w = sheet.get_width() // frame_count
        frame_h = sheet.get_height()
        return [
            pygame.transform.scale(
                sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
                (frame_w * self.scale, frame_h * self.scale)
            ) for i in range(frame_count)
        ]

    def load_hp_bar_frames(self, sheet, frame_count, scale=1):
        frame_w = sheet.get_width() // frame_count
        frame_h = sheet.get_height()
        return [
            pygame.transform.scale(
                sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
                (frame_w * scale, frame_h * scale)
            ) for i in range(frame_count)
        ]

    def take_damage(self, amount):
        if not self.active:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.active = False

    def update(self, dt, player, ghosts):
        if not self.active:
            return

        self.anim_timer += dt
        if self.attacking:
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                if self.attack_anim_index < len(self.attack_right_frames) - 1:
                    self.attack_anim_index += 1
                else:
                    self.attack_anim_index = 0
                    self.attacking = False
                    self.attack_time = 0
        else:
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.walk_anim_index = (self.walk_anim_index + 1) % len(self.walk_right_frames)

        if not self.attacking:
            self.attack_timer += dt
            if self.attack_timer >= self.attack_cooldown and self.rect.colliderect(player.rect):
                player.take_damage(20)
                self.attacking = True
                self.attack_anim_index = 0
                self.attack_timer = 0

        if not self.attacking:
            direction = pygame.Vector2(player.rect.centerx - self.rect.centerx,
                                       player.rect.centery - self.rect.centery)
            if direction.length() > 0:
                direction.normalize_ip()
                self.rect.x += direction.x * self.speed * dt
                self.rect.y += direction.y * self.speed * dt
                self.facing = "right" if direction.x >= 0 else "left"

        self.summon_timer += dt
        if self.summon_timer >= self.summon_cooldown:
            self.summon_timer = 0
            for _ in range(2):
                ghost_x = self.rect.centerx + random.randint(-60, 60)
                ghost_y = self.rect.centery + random.randint(-60, 60)
                ghosts.append(Ghost(ghost_x, ghost_y))

    def draw(self, surface, camera_offset):
        if not self.active:
            return

        if self.attacking:
            frames = self.attack_right_frames if self.facing == "right" else self.attack_left_frames
            frame_index = self.attack_anim_index
        else:
            frames = self.walk_right_frames if self.facing == "right" else self.walk_left_frames
            frame_index = self.walk_anim_index % len(frames)

        frame = frames[frame_index]
        draw_x = self.rect.x - camera_offset.x
        draw_y = self.rect.y - camera_offset.y
        surface.blit(frame, (draw_x, draw_y))

        # Draw boss HP bar at top center
        if self.active:
            hp_ratio = self.hp / self.max_hp
            bar_index = int((1 - hp_ratio) * (len(self.hp_bar_frames) - 1))
            bar_index = min(bar_index, len(self.hp_bar_frames) - 1)
            hp_bar_image = self.hp_bar_frames[bar_index]
            bar_x = (surface.get_width() - hp_bar_image.get_width()) // 2
            bar_y = 20
            surface.blit(hp_bar_image, (bar_x, bar_y))
