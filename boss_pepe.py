from safe_loader import safe_load_image, safe_font
import pygame
import random
from ghost import Ghost

class BossPepe:
    def __init__(self, x, y, power_level=1):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 32, 32)
        self.power_level = power_level  # Уровень силы босса

        self.sheet_right = safe_load_image("assets/boss_pepe_walk_right.png")
        self.sheet_left = safe_load_image("assets/boss_pepe_walk_left.png")
        self.summon_right = safe_load_image("assets/boss_pepe_summon_right.png")
        self.summon_left = safe_load_image("assets/boss_pepe_summon_left.png")

        self.scale = 2
        self.speed = 100 + (power_level - 1) * 15  # Увеличиваем скорость с уровнем
        self.facing = "right"
        self.frames = self.load_frames(self.sheet_right)
        self.summon_frames = self.load_frames(self.summon_right)
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.15

        self.mode = "walk"
        # Кулдаун призыва зависит от уровня силы
        self.summon_cooldown = max(1.5, 3.5 - (power_level - 1) * 0.4)
        self.summon_timer = 0
        
        # Количество призываемых призраков зависит от уровня силы
        self.ghosts_per_summon = power_level
        self.max_ghosts_summoned = 15 + power_level * 5  # Увеличиваем лимит

        self.active = True
        self.ghosts_killed = 0
        self.summon_duration = 1.5
        self.summoning = False
        self.summon_time = 0

        self.running_away = False
        
        # Добавляем здоровье боссу на высоких уровнях
        if power_level > 3:
            self.has_hp = True
            self.max_hp = (power_level - 3) * 20
            self.hp = self.max_hp
        else:
            self.has_hp = False

        # Урон который наносит босс
        self.damage = 3 + power_level

        print(f"BossPepe spawned! Level: {power_level}, Speed: {self.speed}, Ghosts per summon: {self.ghosts_per_summon}")

    def load_frames(self, sheet):
        frame_w = sheet.get_width() // 10
        frame_h = sheet.get_height()
        return [
            pygame.transform.scale(sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
                                   (frame_w * self.scale, frame_h * self.scale))
            for i in range(10)
        ]

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

        # Проверяем условие побега (по убитым призракам или урону)
        if ((not self.has_hp and self.ghosts_killed >= self.max_ghosts_summoned) or 
            (self.has_hp and self.hp <= 0)):
            self.running_away = True
            self.mode = "run"

        self.anim_timer += dt

        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(self.frames)

        if self.running_away:
            # Убегает быстрее
            escape_speed = self.speed * 1.5
            self.rect.x += escape_speed * dt
            if self.rect.x > 2000:
                self.active = False
            return

        self.summon_timer += dt

        if self.summoning:
            self.summon_time += dt
            if self.summon_time >= self.summon_duration:
                self.summoning = False
                self.summon_time = 0
                
                # Призываем призраков в зависимости от уровня силы
                for _ in range(self.ghosts_per_summon):
                    ghost_x = self.rect.centerx + random.randint(-80, 80)
                    ghost_y = self.rect.centery + random.randint(-80, 80)
                    
                    # На высоких уровнях может призывать разные типы призраков
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
            # Движение к игроку (но держится на расстоянии)
            direction = pygame.Vector2(player.rect.centerx - self.rect.centerx,
                                       player.rect.centery - self.rect.centery)
            target_distance = 120 + self.power_level * 10  # Дистанция зависит от уровня
            
            if direction.length() > target_distance:
                direction.normalize_ip()
                self.rect.x += direction.x * self.speed * dt * 0.6
                self.rect.y += direction.y * self.speed * dt * 0.6
                self.facing = "right" if direction.x >= 0 else "left"
            elif direction.length() < target_distance - 20:
                # Отходит если игрок слишком близко
                direction.normalize_ip()
                self.rect.x -= direction.x * self.speed * dt * 0.4
                self.rect.y -= direction.y * self.speed * dt * 0.4
                self.facing = "right" if direction.x >= 0 else "left"
                
            # Атака в ближнем бою (редко)
            if direction.length() < 40 and random.random() < 0.01:  # 1% шанс каждый кадр
                player.take_damage(self.damage)

    def draw(self, surface, camera_offset):
        if not self.active:
            return
            
        if self.mode == "summon" or self.summoning:
            frames = self.summon_frames if self.facing == "right" else self.load_frames(self.summon_left)
        else:
            frames = self.frames if self.facing == "right" else self.load_frames(self.sheet_left)
            
        frame = frames[self.anim_index % len(frames)]
        surface.blit(frame, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))
        
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