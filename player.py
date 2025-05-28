import pygame
from damage_number import DamageNumber
from shield_spell import ShieldSpell

def scale_frames(sheet, frame_count, frame_w, frame_h, scale):
    return [
        pygame.transform.scale(
            sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
            (int(frame_w * scale), int(frame_h * scale))
        )
        for i in range(frame_count)
    ]

class Player:
    def __init__(self, x, y):
        scale = 2

        self.idle_right_sheet = pygame.image.load("assets/mag stay sprite.png").convert_alpha()
        self.idle_left_sheet = pygame.image.load("assets/image_2025-05-09_17-50-33.png").convert_alpha()
        self.shoot_right_sheet = pygame.image.load("assets/mag shoot.png").convert_alpha()
        self.shoot_left_sheet = pygame.image.load("assets/image_2025-05-09_19-26-15.png").convert_alpha()
        self.run_right_sheet = pygame.image.load("assets/mag run right.png").convert_alpha()
        self.run_left_sheet = pygame.image.load("assets/image_2025-05-09_17-28-58.png").convert_alpha()

        self.idle_right_frames = scale_frames(self.idle_right_sheet, 7, 32, 32, scale)
        self.idle_left_frames = scale_frames(self.idle_left_sheet, 7, 32, 32, scale)
        self.shoot_right_frames = scale_frames(self.shoot_right_sheet, 10, 32, 32, scale)
        self.shoot_left_frames = scale_frames(self.shoot_left_sheet, 10, 32, 32, scale)
        self.run_right_frames = scale_frames(self.run_right_sheet, 10, 32, 32, scale)
        self.run_left_frames = scale_frames(self.run_left_sheet, 10, 32, 32, scale)

        self.frame_index = 0
        self.animation_speed = 0.1
        self.animation_timer = 0
        self.current_animation = "idle_right"
        self.facing = "right"
        self.shooting = False

        self.rect = self.idle_right_frames[0].get_rect(center=(x, y))
        self.speed = 200

        self.max_hp = 45
        self.hp = 45
        self.max_mana = 45
        self.mana = 45
        self.mana_regen_rate = 2

        self.show_hp_timer = 0
        self.damage_cooldown = 0
        self.taking_damage = False

        hp_bar_sheet = pygame.image.load("assets/Sprite-0001-Sheet.png").convert_alpha()
        self.hp_bar_frames = [
            hp_bar_sheet.subsurface(pygame.Rect(i * 32, 0, 32, 32))
            for i in range(9)
        ]

        self.damage_numbers = []

        self.shield = ShieldSpell(self)
        self.shield_cooldown = 0

    def start_shoot_animation(self, direction_x):
        self.facing = "right" if direction_x >= 0 else "left"
        self.current_animation = f"shoot_{self.facing}"
        self.frame_index = 0
        self.animation_timer = 0
        self.shooting = True

    def take_damage(self, amount, sprite="1HP.png"):
        if self.shield.absorb_damage(amount):
            return

        if not self.taking_damage:
            self.hp = max(0, self.hp - amount)
            self.show_hp_timer = 2
            self.taking_damage = True
            self.damage_cooldown = 0.3
            self.damage_numbers.append(DamageNumber(self.rect.centerx, self.rect.top, sprite))

    def recover_mana(self, dt):
        if self.mana < self.max_mana:
            self.mana += self.mana_regen_rate * dt
            if self.mana > self.max_mana:
                self.mana = self.max_mana

    def update(self, keys, dt, walls):
        dx = dy = 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        direction = pygame.math.Vector2(dx, dy)

        if direction.length() > 0:
            direction.normalize_ip()
            new_rect = self.rect.move(direction.x * self.speed * dt, 0)
            if not any(new_rect.colliderect(w) for w in walls):
                self.rect.x = new_rect.x
            new_rect = self.rect.move(0, direction.y * self.speed * dt)
            if not any(new_rect.colliderect(w) for w in walls):
                self.rect.y = new_rect.y
            if dx > 0:
                self.current_animation = "run_right"
                self.facing = "right"
            elif dx < 0:
                self.current_animation = "run_left"
                self.facing = "left"
        elif not self.shooting:
            self.current_animation = f"idle_{self.facing}"

        self.animation_timer += dt

        if self.current_animation.startswith("shoot"):
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index += 1
                if self.frame_index >= len(self.shoot_right_frames):
                    self.shooting = False
                    self.current_animation = f"idle_{self.facing}"
                    self.frame_index = 0
        else:
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                frames = {
                    "idle_right": self.idle_right_frames,
                    "idle_left": self.idle_left_frames,
                    "run_right": self.run_right_frames,
                    "run_left": self.run_left_frames,
                }[self.current_animation]
                self.frame_index = (self.frame_index + 1) % len(frames)

        if self.show_hp_timer > 0:
            self.show_hp_timer -= dt
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

        self.shield.update(dt)

        for dn in self.damage_numbers[:]:
            dn.update(dt)
            if dn.finished:
                self.damage_numbers.remove(dn)

    def draw(self, surface, camera_offset):
        if self.current_animation == "shoot_right":
            frames = self.shoot_right_frames
        elif self.current_animation == "shoot_left":
            frames = self.shoot_left_frames
        elif self.current_animation == "run_right":
            frames = self.run_right_frames
        elif self.current_animation == "run_left":
            frames = self.run_left_frames
        elif self.current_animation == "idle_left":
            frames = self.idle_left_frames
        else:
            frames = self.idle_right_frames

        self.frame_index %= len(frames)
        frame = frames[self.frame_index]

        if self.damage_cooldown > 0:
            frame = frame.copy()
            frame.set_alpha(128)

        surface.blit(frame, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))

        self.shield.draw(surface, camera_offset)

        if self.show_hp_timer > 0:
            hp_ratio = self.hp / self.max_hp
            frame_index = int((1 - hp_ratio) * (len(self.hp_bar_frames) - 1))
            frame_index = min(frame_index, len(self.hp_bar_frames) - 1)
            hp_image = self.hp_bar_frames[frame_index]
            bar_x = self.rect.centerx - hp_image.get_width() // 2 - camera_offset.x
            bar_y = self.rect.top - 12 - camera_offset.y
            surface.blit(hp_image, (bar_x, bar_y))

        for dn in self.damage_numbers:
            dn.draw(surface, camera_offset)
