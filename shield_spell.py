import pygame
from safe_loader import safe_load_image

class ShieldSpell:
    def __init__(self, player, sprite_path="assets/shield_spell.png", scale=2):
        self.player = player
        
        
        try:
            self.sheet = safe_load_image(sprite_path, (192, 32))
            print(f"Shield sprite loaded from: {sprite_path}")
        except:
            print(f"Creating fallback shield sprites")
            
            self.sheet = pygame.Surface((192, 32), pygame.SRCALPHA)
            colors = [(100, 150, 255), (80, 130, 235), (60, 110, 215), 
                     (40, 90, 195), (20, 70, 175), (100, 100, 100)]
            for i, color in enumerate(colors):
                pygame.draw.circle(self.sheet, color, (i * 32 + 16, 16), 12)
        
        self.frames = [
            pygame.transform.scale(
                self.sheet.subsurface(pygame.Rect(i * 32, 0, 32, 32)),
                (32 * scale, 32 * scale)
            ) for i in range(6)
        ]
        
        self.active = False
        self.appearing = True
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_duration = 0.1
        self.shield_hp = 0
        self.max_shield_hp = 0

    def activate(self):
        if not self.active and self.player.mana >= 15:
            self.player.mana -= 15
            self.active = True
            self.appearing = True
            self.current_frame = 0
            self.frame_timer = 0
            self.max_shield_hp = max(1, self.player.max_hp // 2)
            self.shield_hp = self.max_shield_hp
            print(f"Shield activated with {self.shield_hp} HP")

    def absorb_damage(self, amount):
        if self.active and not self.appearing and self.shield_hp > 0:
            self.shield_hp -= amount
            print(f"Shield absorbed {amount} damage, {self.shield_hp} HP remaining")
            if self.shield_hp <= 0:
                self.shield_hp = 0
                self.active = False
                print("Shield destroyed")
            return True
        return False

    def update(self, dt):
        if self.active:
            self.frame_timer += dt
            if self.appearing:
                if self.frame_timer >= self.frame_duration:
                    self.frame_timer = 0
                    self.current_frame += 1
                    if self.current_frame >= 3:
                        self.current_frame = 3
                        self.appearing = False
            else:
                if self.shield_hp <= 0:
                    self.current_frame = 5
                else:
                    progress = self.shield_hp / self.max_shield_hp
                    if progress > 0.66:
                        self.current_frame = 3
                    elif progress > 0.33:
                        self.current_frame = 4
                    else:
                        self.current_frame = 5

    def draw(self, surface, camera_offset):
        if self.active and self.current_frame < len(self.frames):
            shield_image = self.frames[self.current_frame]
            shield_rect = shield_image.get_rect(center=self.player.rect.center - camera_offset)
            surface.blit(shield_image, shield_rect)


class PlayerLevel:
    def __init__(self):
        self.level = 1
        self.unlock_lightning = False
        self.unlock_shield = False

    def level_up(self):
        self.level += 1
        if self.level == 2:
            self.unlock_lightning = True
        elif self.level == 3:
            self.unlock_shield = True