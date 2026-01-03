from safe_loader import safe_load_image, safe_font
import pygame

def load_single_image(image_path, target_size=(128, 128), scale=1):
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
        fallback.fill((150, 255, 150))  # Зеленый цвет для призрака
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

class Ghost:
    def __init__(self, x, y):
        scale = 2

        # НОВЫЙ КОД: Загружаем отдельные изображения
        self.image_spawn = load_single_image("assets/ghost_spawn.png")
        self.image_left = load_single_image("assets/ghost_left.png")  # Смотрит влево
        self.image_right = load_single_image("assets/ghost_right.png")  # Смотрит вправо
        
        # Текущее изображение и состояние
        self.current_image = self.image_spawn
        self.facing = "right"  # Направление, куда смотрит призрак
        
        # Система спавна
        self.current_animation = "spawn"
        self.spawn_timer = 0
        self.spawn_duration = 1.0  # 1 секунда на спавн

        # СТАРЫЙ КОД ДЛЯ СОВМЕСТИМОСТИ
        try:
            self.spawn_sheet = safe_load_image("assets/MiniGhost_Spawn.png")
            self.idle_sheet = safe_load_image("assets/MiniGhost_Idle.png")

            self.spawn_frames = scale_frames(self.spawn_sheet, 10, 32, 32, scale)
            self.idle_frames = scale_frames(self.idle_sheet, 8, 32, 32, scale)

            self.frame_index = 0
            self.animation_speed = 0.12
            self.animation_timer = 0
        except Exception as e:
            print(f"Fallback for old ghost sprites: {e}")
            # Если старые спрайты не загрузились, используем новые изображения
            self.spawn_frames = [self.image_spawn]
            self.idle_frames = [self.image_right]
            self.frame_index = 0
            self.animation_speed = 0.12
            self.animation_timer = 0

        # ИСПРАВЛЕНО: используем current_image
        self.rect = self.current_image.get_rect(center=(x, y))
        self.speed = 100
        self.active = False
        self.attack_cooldown = 0

    def update_current_image(self):
        """Обновляет текущее изображение на основе состояния и направления"""
        if self.current_animation == "spawn":
            self.current_image = self.image_spawn
        else:
            # Активное состояние - выбираем направление
            if self.facing == "right":
                self.current_image = self.image_right
            else:
                self.current_image = self.image_left

    def update(self, dt, player):
        # НОВАЯ СИСТЕМА: Обновление спавна
        if self.current_animation == "spawn":
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_duration:
                self.current_animation = "idle"
                self.active = True
                
        # СТАРАЯ СИСТЕМА ДЛЯ СОВМЕСТИМОСТИ
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
                
                # НОВОЕ: Определяем направление взгляда
                if direction.x > 0:
                    self.facing = "right"
                else:
                    self.facing = "left"
                
                self.rect.x += direction.x * self.speed * dt
                self.rect.y += direction.y * self.speed * dt

            if self.rect.colliderect(player.rect) and self.attack_cooldown <= 0:
                player.take_damage(1)
                self.attack_cooldown = 1.0

        # Обновляем текущее изображение
        self.update_current_image()

    def draw(self, surface, camera_offset):
        # Используем новую систему изображений
        surface.blit(self.current_image, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))