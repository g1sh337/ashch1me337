from safe_loader import safe_load_image, safe_font
import pygame
from damage_number import DamageNumber

def load_single_image(image_path, target_size=(128, 128), scale=0.8):
    """
    Загружает одиночное изображение и масштабирует его
    """
    try:
        image = safe_load_image(image_path, target_size)
        scaled_size = (int(target_size[0] * scale), int(target_size[1] * scale))
        return pygame.transform.scale(image, scaled_size)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        scaled_size = (int(target_size[0] * scale), int(target_size[1] * scale))
        fallback = pygame.Surface(scaled_size)
        fallback.fill((100, 100, 255))  # Синий цвет для стреляющего призрака
        return fallback

# СТАРАЯ ФУНКЦИЯ ДЛЯ СОВМЕСТИМОСТИ
def scale_frames(sheet, frame_count, frame_w, frame_h, scale):
    return [
        pygame.transform.scale(
            sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
            (int(frame_w * scale), int(frame_h * scale))
        )
        for i in range(frame_count)
    ]

class ShooterGhost:
    def __init__(self, x, y):
        scale = 2

        # НОВЫЙ КОД: Загружаем отдельные изображения
        self.image_idle_left = load_single_image("assets/shooter_ghost_idle_left.png")  # Обычное состояние влево
        self.image_idle_right = load_single_image("assets/shooter_ghost_idle_right.png")  # Обычное состояние вправо
        self.image_shoot_left = load_single_image("assets/shooter_ghost_shoot_left.png")  # Стреляет влево
        self.image_shoot_right = load_single_image("assets/shooter_ghost_shoot_right.png")  # Стреляет вправо
        
        # Текущее изображение и состояние
        self.current_image = self.image_idle_right
        self.facing = "right"  # Направление, куда смотрит стреляющий призрак
        self.is_shooting = False
        self.shoot_animation_timer = 0
        self.shoot_animation_duration = 0.5  # Как долго показывать анимацию стрельбы

        # СТАРЫЙ КОД ДЛЯ СОВМЕСТИМОСТИ
        try:
            self.idle_sheet = safe_load_image("assets/ghost walks 2.png")
            self.idle_frames = scale_frames(self.idle_sheet, 12, 32, 32, scale)

            self.frame_index = 0
            self.animation_speed = 0.15
            self.animation_timer = 0
        except Exception as e:
            print(f"Fallback for old shooter ghost sprites: {e}")
            # Если старые спрайты не загрузились, используем новые изображения
            self.idle_frames = [self.image_idle_right]
            self.frame_index = 0
            self.animation_speed = 0.15
            self.animation_timer = 0

        # ИСПРАВЛЕНО: используем current_image
        self.rect = self.current_image.get_rect(center=(x, y))
        self.speed = 60  # Средняя скорость
        self.shoot_cooldown = 0
        self.projectiles = []
        self.attack_range = 200  # Дистанция атаки

    def update_current_image(self):
        """Обновляет текущее изображение на основе состояния и направления"""
        if self.is_shooting:
            # Показываем анимацию стрельбы
            if self.facing == "right":
                self.current_image = self.image_shoot_right
            else:
                self.current_image = self.image_shoot_left
        else:
            # Обычное состояние
            if self.facing == "right":
                self.current_image = self.image_idle_right
            else:
                self.current_image = self.image_idle_left

    def update(self, dt, player):
        # СТАРАЯ СИСТЕМА ДЛЯ СОВМЕСТИМОСТИ
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.idle_frames)

        # НОВОЕ: Управление анимацией стрельбы
        if self.is_shooting:
            self.shoot_animation_timer += dt
            if self.shoot_animation_timer >= self.shoot_animation_duration:
                self.is_shooting = False
                self.shoot_animation_timer = 0

        distance = pygame.Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery
        )

        # НОВОЕ: Определяем направление взгляда на основе позиции игрока
        if distance.x > 0:
            self.facing = "right"
        else:
            self.facing = "left"

        # Движение к игроку если он далеко
        if distance.length() > self.attack_range:
            direction = distance.normalize()
            self.rect.x += direction.x * self.speed * dt
            self.rect.y += direction.y * self.speed * dt

        # Стрельба
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        elif distance.length() <= self.attack_range:
            # Стреляем!
            direction = distance.normalize()
            self.projectiles.append(ShooterProjectile(self.rect.centerx, self.rect.centery, direction))
            self.shoot_cooldown = 2.0
            
            # НОВОЕ: Запускаем анимацию стрельбы
            self.is_shooting = True
            self.shoot_animation_timer = 0

        # Обновляем снаряды
        for p in self.projectiles[:]:
            p.update(dt)
            if p.rect.colliderect(player.rect):
                player.take_damage(2, sprite="2HP.png")
                self.projectiles.remove(p)
            elif not (0 <= p.rect.x <= 2000 and 0 <= p.rect.y <= 2000):
                self.projectiles.remove(p)

        # Обновляем текущее изображение
        self.update_current_image()

    def draw(self, surface, camera_offset):
        # Используем новую систему изображений
        surface.blit(self.current_image, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))
        
        # Рисуем снаряды
        for p in self.projectiles:
            p.draw(surface, camera_offset)

        # Можно добавить индикатор дальности атаки при отладке
        # (закомментировано для обычной игры)
        """
        if hasattr(self, 'attack_range'):
            pygame.draw.circle(surface, (100, 100, 255, 50), 
                             (self.rect.centerx - camera_offset.x, self.rect.centery - camera_offset.y), 
                             self.attack_range, 2)
        """


class ShooterProjectile:
    def __init__(self, x, y, direction):
        self.direction = direction.normalize()
        self.speed = 300
        self.rect = pygame.Rect(x, y, 16, 16)

        # НОВЫЙ КОД: Загружаем отдельные изображения для снарядов
        try:
            if abs(self.direction.x) > abs(self.direction.y):
                if self.direction.x > 0:
                    self.image = load_single_image("assets/projectile_right.png", (32, 32), scale=1)
                else:
                    self.image = load_single_image("assets/projectile_left.png", (32, 32), scale=1)
            else:
                if self.direction.y > 0:
                    self.image = load_single_image("assets/projectile_down.png", (32, 32), scale=1)
                else:
                    self.image = load_single_image("assets/projectile_up.png", (32, 32), scale=1)
        except Exception as e:
            print(f"Failed to load projectile sprites, using fallback: {e}")
            # СТАРЫЙ КОД ДЛЯ СОВМЕСТИМОСТИ
            try:
                if abs(self.direction.x) > abs(self.direction.y):
                    if self.direction.x > 0:
                        self.image = safe_load_image("assets/eye_right.png")
                    else:
                        self.image = safe_load_image("assets/eye_left.png")
                else:
                    if self.direction.y > 0:
                        self.image = safe_load_image("assets/eye_down.png")
                    else:
                        self.image = safe_load_image("assets/eye_up.png")
                self.image = pygame.transform.scale(self.image, (32, 32))
            except Exception as e2:
                print("Failed to load eye projectile sprite:", e2)
                self.image = pygame.Surface((32, 32))
                self.image.fill((255, 255, 0))  # Желтый снаряд

    def update(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt

    def draw(self, surface, camera_offset):
        surface.blit(self.image, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))