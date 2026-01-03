from safe_loader import safe_load_image, safe_font
import pygame
import random
from ghost import Ghost
import math

def load_single_image(image_path, target_size=(128, 128), scale=1.5):
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
        fallback.fill((255, 100, 100))  # Красный цвет для Сильного Босса
        return fallback

class BossStrong:
    def __init__(self, x, y, power_level=1):
        self.x = x
        self.y = y
        self.power_level = power_level
        self.rect = pygame.Rect(x, y, 64, 64)

        # НОВЫЙ КОД: Загружаем отдельные изображения
        self.image_left = load_single_image("assets/boss_strong_left.png")   # Смотрит влево
        self.image_right = load_single_image("assets/boss_strong_right.png") # Смотрит вправо
        
        # Текущее изображение и состояние
        self.current_image = self.image_right
        self.facing = "right"  # Направление, куда смотрит босс
        
        # Анимация и эффекты
        self.animation_timer = 0
        self.bob_offset = 0  # Для эффекта покачивания
        self.attack_effect_timer = 0  # Для эффекта при атаке
        self.is_attacking_visually = False

        # СТАРЫЙ КОД ДЛЯ СОВМЕСТИМОСТИ (загрузка HP бара)
        try:
            self.hp_bar_sheet = safe_load_image("assets/bosshp.png")
            self.hp_bar_frames = self.load_hp_bar_frames(self.hp_bar_sheet, 11, scale=2)
        except Exception as e:
            print(f"Failed to load HP bar: {e}")
            # Создаем простые HP бары
            self.hp_bar_frames = []
            for i in range(11):
                frame = pygame.Surface((60, 12))
                frame.fill((100, 0, 0))
                self.hp_bar_frames.append(frame)

        self.scale = 2
        # Скорость увеличивается с уровнем силы
        self.speed = 40 + power_level * 15
        
        self.mode = "walk"
        # Кулдаун атаки уменьшается с уровнем
        self.attack_cooldown_max = max(1.0, 2.0 - power_level * 0.2)
        self.attack_timer = 0
        self.attack_duration = 1
        self.attacking = False
        self.attack_time = 0

        # Кулдаун призыва уменьшается
        self.summon_cooldown = max(3.0, 5.0 - power_level * 0.3)
        self.summon_timer = 0
        
        # HP увеличивается с уровнем
        base_hp = 30 + power_level * 15
        self.hp = base_hp
        self.max_hp = base_hp
        self.active = True
        
        # Урон увеличивается с уровнем
        self.damage = 15 + power_level * 5
        
        # Дополнительные способности на высоких уровнях
        self.rage_mode = False
        self.rage_threshold = 0.3  # Включается при 30% HP
        self.rage_speed_multiplier = 1.5
        self.rage_damage_multiplier = 1.5
        
        # Количество призываемых призраков
        self.ghosts_per_summon = 1 + (power_level - 1) // 2
        
        print(f"BossStrong spawned! Level: {power_level}, HP: {self.max_hp}, Damage: {self.damage}, Speed: {self.speed}")

    def load_hp_bar_frames(self, sheet, frame_count, scale=1):
        """Загружает кадры HP бара"""
        try:
            frame_w = sheet.get_width() // frame_count
            frame_h = sheet.get_height()
            return [
                pygame.transform.scale(
                    sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
                    (frame_w * scale, frame_h * scale)
                ) for i in range(frame_count)
            ]
        except:
            # Fallback HP бары
            frames = []
            for i in range(frame_count):
                frame = pygame.Surface((60, 12))
                frame.fill((100, 0, 0))
                frames.append(frame)
            return frames

    def update_current_image(self):
        """Обновляет текущее изображение на основе направления"""
        if self.facing == "right":
            self.current_image = self.image_right
        else:
            self.current_image = self.image_left

    def take_damage(self, amount):
        if not self.active:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.active = False
        
        # Активируем режим ярости при низком HP
        if self.hp / self.max_hp <= self.rage_threshold and not self.rage_mode:
            self.rage_mode = True
            print(f"BossStrong enters RAGE MODE! (Level {self.power_level})")

    def get_current_speed(self):
        """Возвращает текущую скорость с учетом ярости"""
        base_speed = self.speed
        if self.rage_mode:
            return base_speed * self.rage_speed_multiplier
        return base_speed

    def get_current_damage(self):
        """Возвращает текущий урон с учетом ярости"""
        base_damage = self.damage
        if self.rage_mode:
            return int(base_damage * self.rage_damage_multiplier)
        return base_damage

    def update(self, dt, player, ghosts):
        if not self.active:
            return

        # Простая анимация покачивания
        self.animation_timer += dt
        self.bob_offset = int(3 * math.sin(self.animation_timer * 4)) # Более сильное покачивание чем у Пепе

        # Эффект атаки
        if self.is_attacking_visually:
            self.attack_effect_timer += dt
            if self.attack_effect_timer >= 0.3:  # Эффект длится 0.3 секунды
                self.is_attacking_visually = False
                self.attack_effect_timer = 0

        # Направление к игроку
        direction = pygame.Vector2(player.rect.centerx - self.rect.centerx,
                                   player.rect.centery - self.rect.centery)
        
        # НОВОЕ: Определяем направление взгляда
        if direction.x > 0:
            self.facing = "right"
        else:
            self.facing = "left"

        # Логика атаки
        if not self.attacking:
            self.attack_timer += dt
            distance_to_player = direction.length()
            
            # Проверяем атаку в ближнем бою
            if (self.attack_timer >= self.attack_cooldown_max and 
                distance_to_player < 80):  # Увеличенная дальность атаки
                
                player.take_damage(self.get_current_damage())
                self.attacking = True
                self.attack_timer = 0
                
                # НОВОЕ: Запускаем визуальный эффект атаки
                self.is_attacking_visually = True
                self.attack_effect_timer = 0
                
                # В режиме ярости может атаковать по площади
                if self.rage_mode and distance_to_player < 120:
                    # Дополнительный урон если очень близко
                    player.take_damage(self.get_current_damage() // 2)

        # Движение к игроку
        if not self.attacking:
            if direction.length() > 0:
                direction.normalize_ip()
                current_speed = self.get_current_speed()
                self.rect.x += direction.x * current_speed * dt
                self.rect.y += direction.y * current_speed * dt

        # Управление атакой
        if self.attacking:
            self.attack_time += dt
            if self.attack_time >= self.attack_duration:
                self.attacking = False
                self.attack_time = 0

        # Призыв призраков
        self.summon_timer += dt
        if self.summon_timer >= self.summon_cooldown:
            self.summon_timer = 0
            
            # В режиме ярости призывает больше и сильнее
            ghost_count = self.ghosts_per_summon
            if self.rage_mode:
                ghost_count += 1
                
            for _ in range(ghost_count):
                ghost_x = self.rect.centerx + random.randint(-100, 100)
                ghost_y = self.rect.centery + random.randint(-100, 100)
                
                # На высоких уровнях или в ярости призывает сильных призраков
                if self.power_level >= 3 or self.rage_mode:
                    from tank_ghost import TankGhost
                    from shooter_ghost import ShooterGhost
                    
                    if self.rage_mode:
                        # В ярости больше танков
                        ghost_types = [TankGhost, TankGhost, ShooterGhost]
                    else:
                        ghost_types = [Ghost, TankGhost, ShooterGhost]
                    
                    ghost_class = random.choice(ghost_types)
                    ghosts.append(ghost_class(ghost_x, ghost_y))
                else:
                    ghosts.append(Ghost(ghost_x, ghost_y))

        # Обновляем текущее изображение
        self.update_current_image()

    def draw(self, surface, camera_offset):
        if not self.active:
            return

        # Рисуем с эффектом покачивания
        draw_x = self.rect.x - camera_offset.x
        draw_y = self.rect.y - camera_offset.y + self.bob_offset
        
        current_image = self.current_image
        
        # В режиме ярости добавляем красный оттенок
        if self.rage_mode:
            current_image = current_image.copy()
            red_overlay = pygame.Surface(current_image.get_size())
            red_overlay.fill((255, 100, 100))
            red_overlay.set_alpha(80)
            current_image.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Эффект вспышки при атаке
        if self.is_attacking_visually:
            current_image = current_image.copy()
            flash_overlay = pygame.Surface(current_image.get_size())
            flash_overlay.fill((255, 255, 255))
            flash_overlay.set_alpha(60)
            current_image.blit(flash_overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        surface.blit(current_image, (draw_x, draw_y))

        # Draw boss HP bar at top center
        if self.active:
            hp_ratio = self.hp / self.max_hp
            bar_index = int((1 - hp_ratio) * (len(self.hp_bar_frames) - 1))
            bar_index = min(bar_index, len(self.hp_bar_frames) - 1)
            hp_bar_image = self.hp_bar_frames[bar_index]
            bar_x = (surface.get_width() - hp_bar_image.get_width()) // 2
            bar_y = 20
            surface.blit(hp_bar_image, (bar_x, bar_y))
            
            # Текст с уровнем босса
            if hasattr(pygame.font, 'Font'):
                try:
                    font = safe_font(10)
                    level_text = f"STRONG BOSS LV.{self.power_level}"
                    if self.rage_mode:
                        level_text += " [RAGE]"
                    level_surface = font.render(level_text, True, (255, 255, 255))
                    text_x = (surface.get_width() - level_surface.get_width()) // 2
                    text_y = bar_y + hp_bar_image.get_height() + 5
                    surface.blit(level_surface, (text_x, text_y))
                except:
                    pass  # Если шрифт не найден, пропускаем