from safe_loader import safe_load_image, safe_font
import pygame
import sys
import os
from damage_number import DamageNumber
from shield_spell import ShieldSpell

def resource_path(relative_path):
    """ Получает путь к ресурсу для PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def safe_load_image(path, fallback_size=(64, 64)):
    """Безопасная загрузка изображения"""
    try:
        full_path = resource_path(path)
        if os.path.exists(full_path):
            return pygame.image.load(full_path).convert_alpha()
        else:
            print(f"Image not found: {full_path}, creating fallback")
            surface = pygame.Surface(fallback_size)
            surface.fill((100, 100, 200))  # Синий цвет для игрока
            return surface.convert_alpha()
    except Exception as e:
        print(f"Error loading image {path}: {e}, creating fallback")
        surface = pygame.Surface(fallback_size)
        surface.fill((100, 100, 200))
        return surface.convert_alpha()

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

        
        self.idle_right_sheet = safe_load_image("assets/mag stay sprite.png", (320, 32))
        self.idle_left_sheet = safe_load_image("assets/image_2025-05-09_17-50-33.png", (320, 32))
        self.shoot_right_sheet = safe_load_image("assets/mag shoot.png", (320, 32))
        self.shoot_left_sheet = safe_load_image("assets/image_2025-05-09_19-26-15.png", (320, 32))
        self.run_right_sheet = safe_load_image("assets/mag run right.png", (320, 32))
        self.run_left_sheet = safe_load_image("assets/image_2025-05-09_17-28-58.png", (320, 32))

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
        
        # Фикс анимации стрельбы
        self.shooting = False
        self.shoot_animation_complete = False

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

        # Безопасная загрузка полосы здоровья
        hp_bar_sheet = safe_load_image("assets/Sprite-0001-Sheet.png", (288, 32))
        self.hp_bar_frames = [
            hp_bar_sheet.subsurface(pygame.Rect(i * 32, 0, 32, 32))
            for i in range(9)
        ]

        self.damage_numbers = []

        self.shield = ShieldSpell(self)
        self.shield_cooldown = 0

    def start_shoot_animation(self, direction_x):
        """Запускает анимацию стрельбы с правильным направлением"""
        if not self.shooting:  # Предотвращаем перезапуск анимации
            self.facing = "right" if direction_x >= 0 else "left"
            self.current_animation = f"shoot_{self.facing}"
            self.frame_index = 0
            self.animation_timer = 0
            self.shooting = True
            self.shoot_animation_complete = False

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
        # Движение
        dx = dy = 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        direction = pygame.math.Vector2(dx, dy)
        is_moving = direction.length() > 0

        # Физика движения
        if is_moving:
            direction.normalize_ip()
            new_rect = self.rect.move(direction.x * self.speed * dt, 0)
            if not any(new_rect.colliderect(w) for w in walls):
                self.rect.x = new_rect.x
            new_rect = self.rect.move(0, direction.y * self.speed * dt)
            if not any(new_rect.colliderect(w) for w in walls):
                self.rect.y = new_rect.y

        # Логика анимаций - ИСПРАВЛЕНО
        self.animation_timer += dt

        if self.shooting:
            # Анимация стрельбы имеет приоритет
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index += 1
                
                # Получаем правильные кадры для текущего направления
                current_frames = (self.shoot_right_frames if self.facing == "right" 
                                else self.shoot_left_frames)
                
                if self.frame_index >= len(current_frames):
                    # Анимация стрельбы завершена
                    self.shooting = False
                    self.shoot_animation_complete = True
                    self.frame_index = 0
                    # Переходим к анимации движения или idle
                    if is_moving:
                        if dx > 0:
                            self.current_animation = "run_right"
                            self.facing = "right"
                        elif dx < 0:
                            self.current_animation = "run_left"
                            self.facing = "left"
                        else:
                            # Движение только по Y, сохраняем направление
                            self.current_animation = f"run_{self.facing}"
                    else:
                        self.current_animation = f"idle_{self.facing}"
        else:
            # Обычная логика анимации (движение/idle)
            if is_moving:
                # Обновляем направление только если движемся по X
                if dx > 0:
                    self.current_animation = "run_right"
                    self.facing = "right"
                elif dx < 0:
                    self.current_animation = "run_left"
                    self.facing = "left"
                else:
                    # Движение только по Y, сохраняем направление
                    self.current_animation = f"run_{self.facing}"
            else:
                self.current_animation = f"idle_{self.facing}"

            # Обновляем кадры для движения/idle
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                current_frames = self.get_current_frames()
                self.frame_index = (self.frame_index + 1) % len(current_frames)

        # Обновляем остальные системы
        if self.show_hp_timer > 0:
            self.show_hp_timer -= dt
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

        self.shield.update(dt)

        for dn in self.damage_numbers[:]:
            dn.update(dt)
            if dn.finished:
                self.damage_numbers.remove(dn)

    def get_current_frames(self):
        """Возвращает текущие кадры анимации"""
        frames_map = {
            "idle_right": self.idle_right_frames,
            "idle_left": self.idle_left_frames,
            "run_right": self.run_right_frames,
            "run_left": self.run_left_frames,
            "shoot_right": self.shoot_right_frames,
            "shoot_left": self.shoot_left_frames,
        }
        return frames_map.get(self.current_animation, self.idle_right_frames)

    def draw(self, surface, camera_offset):
        # Получаем правильные кадры для текущей анимации
        current_frames = self.get_current_frames()
        
        # Убеждаемся, что индекс кадра не выходит за границы
        self.frame_index = min(self.frame_index, len(current_frames) - 1)
        frame = current_frames[self.frame_index]

        # Эффект мигания при получении урона
        if self.damage_cooldown > 0:
            frame = frame.copy()
            frame.set_alpha(128)

        surface.blit(frame, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))

        # Отрисовка щита
        self.shield.draw(surface, camera_offset)

        # Полоса здоровья над головой
        if self.show_hp_timer > 0:
            hp_ratio = self.hp / self.max_hp
            frame_index = int((1 - hp_ratio) * (len(self.hp_bar_frames) - 1))
            frame_index = min(frame_index, len(self.hp_bar_frames) - 1)
            hp_image = self.hp_bar_frames[frame_index]
            bar_x = self.rect.centerx - hp_image.get_width() // 2 - camera_offset.x
            bar_y = self.rect.top - 12 - camera_offset.y
            surface.blit(hp_image, (bar_x, bar_y))