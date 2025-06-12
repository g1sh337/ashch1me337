from safe_loader import safe_load_image, safe_font
import pygame
import random
from ghost import Ghost

class BossStrong:
    def __init__(self, x, y, power_level=1):
        self.x = x
        self.y = y
        self.power_level = power_level
        self.rect = pygame.Rect(x, y, 64, 64)

        self.walk_right_sheet = safe_load_image("assets/strong_boss_walk_right.png")
        self.walk_left_sheet = safe_load_image("assets/strong_boss_walk_left.png")
        self.attack_right_sheet = safe_load_image("assets/strong_boss_attack_right.png")
        self.attack_left_sheet = safe_load_image("assets/strong_boss_attack_left.png")

        self.hp_bar_sheet = safe_load_image("assets/bosshp.png")
        self.hp_bar_frames = self.load_hp_bar_frames(self.hp_bar_sheet, 11, scale=2)

        self.scale = 2
        # Скорость увеличивается с уровнем силы
        self.speed = 40 + power_level * 15
        self.facing = "right"

        self.walk_right_frames = self.load_frames(self.walk_right_sheet, 8)
        self.walk_left_frames = self.load_frames(self.walk_left_sheet, 8)
        self.attack_right_frames = self.load_frames(self.attack_right_sheet, 11)
        self.attack_left_frames = self.load_frames(self.attack_left_sheet, 11)

        self.walk_anim_index = 0
        self.attack_anim_index = 0
        self.anim_timer = 0
        self.anim_speed = max(0.1, 0.15 - power_level * 0.01)  # Быстрее анимация

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

        # Логика атаки
        if not self.attacking:
            self.attack_timer += dt
            distance_to_player = pygame.Vector2(
                player.rect.centerx - self.rect.centerx,
                player.rect.centery - self.rect.centery
            ).length()
            
            # Проверяем атаку в ближнем бою
            if (self.attack_timer >= self.attack_cooldown_max and 
                distance_to_player < 80):  # Увеличенная дальность атаки
                
                player.take_damage(self.get_current_damage())
                self.attacking = True
                self.attack_anim_index = 0
                self.attack_timer = 0
                
                # В режиме ярости может атаковать по площади
                if self.rage_mode and distance_to_player < 120:
                    # Дополнительный урон если очень близко
                    player.take_damage(self.get_current_damage() // 2)

        # Движение к игроку
        if not self.attacking:
            direction = pygame.Vector2(player.rect.centerx - self.rect.centerx,
                                       player.rect.centery - self.rect.centery)
            if direction.length() > 0:
                direction.normalize_ip()
                current_speed = self.get_current_speed()
                self.rect.x += direction.x * current_speed * dt
                self.rect.y += direction.y * current_speed * dt
                self.facing = "right" if direction.x >= 0 else "left"

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
        
        # В режиме ярости добавляем красный оттенок
        if self.rage_mode:
            frame = frame.copy()
            red_overlay = pygame.Surface(frame.get_size())
            red_overlay.fill((255, 100, 100))
            red_overlay.set_alpha(80)
            frame.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
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