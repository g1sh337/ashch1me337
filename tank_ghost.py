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
        fallback.fill((200, 100, 100))  # Красный цвет для танк-призрака
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

class TankGhost:
    def __init__(self, x, y):
        scale = 2

        # НОВЫЙ КОД: Загружаем отдельные изображения
        self.image_left = load_single_image("assets/tank_ghost_left.png")  # Смотрит влево
        self.image_right = load_single_image("assets/tank_ghost_right.png")  # Смотрит вправо
        
        # Текущее изображение и состояние
        self.current_image = self.image_right
        self.facing = "right"  # Направление, куда смотрит танк-призрак

        # СТАРЫЙ КОД ДЛЯ СОВМЕСТИМОСТИ
        try:
            self.idle_sheet = safe_load_image("assets/Ghost walks.png")
            self.idle_frames = scale_frames(self.idle_sheet, 12, 32, 32, scale)

            self.frame_index = 0
            self.animation_speed = 0.15
            self.animation_timer = 0
        except Exception as e:
            print(f"Fallback for old tank ghost sprites: {e}")
            # Если старые спрайты не загрузились, используем новые изображения
            self.idle_frames = [self.image_right]
            self.frame_index = 0
            self.animation_speed = 0.15
            self.animation_timer = 0

        # ИСПРАВЛЕНО: используем current_image
        self.rect = self.current_image.get_rect(center=(x, y))
        self.speed = 50  # Медленнее обычного призрака
        self.hp = 5     # Больше здоровья
        self.attack_cooldown = 0

    def update_current_image(self):
        """Обновляет текущее изображение на основе направления"""
        if self.facing == "right":
            self.current_image = self.image_right
        else:
            self.current_image = self.image_left

    def update(self, dt, player):
        # СТАРАЯ СИСТЕМА ДЛЯ СОВМЕСТИМОСТИ
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.idle_frames)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        direction = pygame.Vector2(
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
            self.attack_cooldown = 1.5  # Дольше кулдаун чем у обычного призрака

        # Обновляем текущее изображение
        self.update_current_image()

    def draw(self, surface, camera_offset):
        # Используем новую систему изображений
        surface.blit(self.current_image, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))
        
        # Можно добавить индикатор HP над танк-призраком
        if hasattr(self, 'hp') and self.hp < 5:  # Показываем HP только если поврежден
            hp_bar_width = 40
            hp_bar_height = 4
            hp_ratio = self.hp / 5.0  # Максимальное HP = 5
            
            # Фон полосы здоровья
            bg_rect = pygame.Rect(
                self.rect.centerx - hp_bar_width // 2 - camera_offset.x,
                self.rect.top - 10 - camera_offset.y,
                hp_bar_width,
                hp_bar_height
            )
            pygame.draw.rect(surface, (100, 0, 0), bg_rect)
            
            # Полоса здоровья
            hp_rect = pygame.Rect(
                self.rect.centerx - hp_bar_width // 2 - camera_offset.x,
                self.rect.top - 10 - camera_offset.y,
                int(hp_bar_width * hp_ratio),
                hp_bar_height
            )
            pygame.draw.rect(surface, (255, 100, 100), hp_rect)