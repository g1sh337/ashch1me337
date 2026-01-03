from safe_loader import safe_load_image, safe_font
import pygame
import random
from ghost import Ghost
import math

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
        fallback.fill((255, 255, 0))  # Желтый цвет для Босс Пепе
        return fallback

class BossPepe:
    def __init__(self, x, y, power_level=1):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 64, 64)  # Увеличиваем размер коллизии для босса
        self.power_level = power_level  

        # НОВЫЙ КОД: Загружаем отдельные изображения
        self.image_left = load_single_image("assets/boss_pepe_left.png")   # Смотрит влево
        self.image_right = load_single_image("assets/boss_pepe_right.png") # Смотрит вправо
        
        # Текущее изображение и состояние
        self.current_image = self.image_right
        self.facing = "right"  # Направление, куда смотрит босс

        # Простая анимация покачивания для живости
        self.animation_timer = 0
        self.bob_offset = 0  # Для эффекта покачивания
        self.summon_effect_timer = 0  # Для эффекта при призыве

        self.scale = 2
        self.speed = 100 + (power_level - 1) * 15  
        
        self.mode = "walk"
        
        self.summon_cooldown = max(1.5, 3.5 - (power_level - 1) * 0.4)
        self.summon_timer = 0
        
        self.ghosts_per_summon = power_level
        self.max_ghosts_summoned = 15 + power_level * 5  

        self.active = True
        self.ghosts_killed = 0
        self.summon_duration = 1.5
        self.summoning = False
        self.summon_time = 0

        self.running_away = False
        
        if power_level > 3:
            self.has_hp = True
            self.max_hp = (power_level - 3) * 20
            self.hp = self.max_hp
        else:
            self.has_hp = False

        self.damage = 3 + power_level

        print(f"BossPepe spawned! Level: {power_level}, Speed: {self.speed}, Ghosts per summon: {self.ghosts_per_summon}")

    def update_current_image(self):
        """Обновляет текущее изображение на основе направления"""
        if self.facing == "right":
            self.current_image = self.image_right
        else:
            self.current_image = self.image_left

    def take_damage(self, amount):
        """Урон боссу (только если у него есть HP)"""
        if self.has_hp and self.active:
            self.hp -= amount
            if self.hp <= 0:
                self.hp = 0
                self.running_away = True
                self.mode = "run"

    def update(self, dt, player, ghosts):
        if not self.active:
            return

        # Простая анимация покачивания
        self.animation_timer += dt
        self.bob_offset = int(2 * math.sin(self.animation_timer * 3))

        # Эффект мерцания при призыве
        if self.summoning:
            self.summon_effect_timer += dt
        else:
            self.summon_effect_timer = 0

        # Проверяем условия для бегства
        if ((not self.has_hp and self.ghosts_killed >= self.max_ghosts_summoned) or 
            (self.has_hp and self.hp <= 0)):
            self.running_away = True
            self.mode = "run"

        if self.running_away:
            # Убегает вправо
            escape_speed = self.speed * 1.5
            self.rect.x += escape_speed * dt
            self.facing = "right"  # Смотрит в сторону бегства
            if self.rect.x > 2000:
                self.active = False
            self.update_current_image()
            return

        self.summon_timer += dt

        if self.summoning:
            self.summon_time += dt
            if self.summon_time >= self.summon_duration:
                self.summoning = False
                self.summon_time = 0
                
                # Призываем призраков
                for _ in range(self.ghosts_per_summon):
                    ghost_x = self.rect.centerx + random.randint(-80, 80)
                    ghost_y = self.rect.centery + random.randint(-80, 80)
                    
                    if self.power_level >= 3:
                        from tank_ghost import TankGhost
                        from shooter_ghost import ShooterGhost
                        ghost_types = [Ghost, Ghost, TankGhost] if self.power_level < 5 else [Ghost, TankGhost, ShooterGhost]
                        ghost_class = random.choice(ghost_types)
                        ghosts.append(ghost_class(ghost_x, ghost_y))
                    else:
                        ghosts.append(Ghost(ghost_x, ghost_y))
                        
        elif self.summon_timer >= self.summon_cooldown:
            self.summon_timer = 0
            self.summoning = True
            self.mode = "summon"
        else:
            self.mode = "walk"
            
            direction = pygame.Vector2(player.rect.centerx - self.rect.centerx,
                                       player.rect.centery - self.rect.centery)
            target_distance = 120 + self.power_level * 10  
            
            if direction.length() > target_distance:
                # Приближается к игроку
                direction.normalize_ip()
                self.rect.x += direction.x * self.speed * dt * 0.6
                self.rect.y += direction.y * self.speed * dt * 0.6
                
                # НОВОЕ: Поворачивается в сторону движения
                if direction.x > 0:
                    self.facing = "right"
                else:
                    self.facing = "left"
                    
            elif direction.length() < target_distance - 20:
                # Отходит если игрок слишком близко
                direction.normalize_ip()
                self.rect.x -= direction.x * self.speed * dt * 0.4
                self.rect.y -= direction.y * self.speed * dt * 0.4
                
                # НОВОЕ: Поворачивается лицом к игроку при отступлении
                if direction.x > 0:
                    self.facing = "right"
                else:
                    self.facing = "left"
                
            # Атака в ближнем бою (редко)
            if direction.length() < 40 and random.random() < 0.01:  # 1% шанс каждый кадр
                player.take_damage(self.damage)

        # Обновляем текущее изображение
        self.update_current_image()

    def draw(self, surface, camera_offset):
        if not self.active:
            return
            
        # Рисуем с эффектом покачивания
        draw_x = self.rect.x - camera_offset.x
        draw_y = self.rect.y - camera_offset.y + self.bob_offset
        
        current_image = self.current_image
        
        # Эффект мерцания при призыве
        if self.summoning and self.summon_effect_timer > 0:
            # Создаем мерцающий эффект
            if int(self.summon_effect_timer * 10) % 2 == 0:  # Мерцание каждые 0.1 секунды
                current_image = current_image.copy()
                # Добавляем желтое свечение
                glow_overlay = pygame.Surface(current_image.get_size())
                glow_overlay.fill((255, 255, 100))
                glow_overlay.set_alpha(80)
                current_image.blit(glow_overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        surface.blit(current_image, (draw_x, draw_y))
        
        # Отображаем HP если есть
        if self.has_hp and self.active:
            hp_bar_width = 60
            hp_bar_height = 6
            hp_ratio = self.hp / self.max_hp
            
            # Фон полосы здоровья
            bg_rect = pygame.Rect(
                self.rect.centerx - hp_bar_width // 2 - camera_offset.x,
                self.rect.top - 15 - camera_offset.y,
                hp_bar_width,
                hp_bar_height
            )
            pygame.draw.rect(surface, (100, 0, 0), bg_rect)
            
            # Полоса здоровья
            hp_rect = pygame.Rect(
                self.rect.centerx - hp_bar_width // 2 - camera_offset.x,
                self.rect.top - 15 - camera_offset.y,
                int(hp_bar_width * hp_ratio),
                hp_bar_height
            )
            pygame.draw.rect(surface, (255, 0, 0), hp_rect)

    def notify_ghost_killed(self):
        if not self.running_away:
            self.ghosts_killed += 1