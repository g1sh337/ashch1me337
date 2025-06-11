import pygame
from safe_loader import safe_load_image, safe_font

class AnimatedIcon:
    def __init__(self, path, frame_count, frame_width, frame_height, scale=1):
        self.sheet = safe_load_image(path, (frame_width * frame_count, frame_height))
        self.frames = [
            pygame.transform.scale(
                self.sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)),
                (frame_width * scale, frame_height * scale)
            ) for i in range(frame_count)
        ]
        self.index = 0
        self.timer = 0
        self.speed = 0.15

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.speed:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)

    def get_frame(self):
        return self.frames[self.index]


class Inventory:
    def __init__(self, scale=1):
        self.scale = scale
        self.frame_width = 128
        self.frame_height = 128
        self.frame_count = 5

        sheet = safe_load_image("assets/invent.png", (self.frame_width * self.frame_count, self.frame_height))
        self.frames = [
            pygame.transform.scale(
                sheet.subsurface(pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)),
                (self.frame_width * scale, self.frame_height * scale)
            ) for i in range(self.frame_count)
        ]

        self.timer = 0
        self.index = 0
        self.speed = 0.15

        # Данные иконок с безопасными путями
        icon_data = {
            "faerball": ("faerball_inv.png", (36, -22)),
            "molnia": ("molnia_inv.png", (22, -22)),
            "shield": ("shield_inv.png", (9, -22)),
            "hilka": ("hilka_inv.png", (-20, -22)),
            "mana": ("mana_inv.png", (-7, -22))
        }

        self.slots = list(icon_data.keys())

        # Создаем иконки с fallback
        self.icons = {}
        for name, (filename, _) in icon_data.items():
            try:
                self.icons[name] = AnimatedIcon(f"assets/{filename}", 5, 128, 128, scale=0.9 * scale)
                print(f"Loaded icon: {name}")
            except Exception as e:
                print(f"Failed to load icon {name}: {e}")
                # Создаем простую цветную иконку как fallback
                self.icons[name] = self.create_fallback_icon(name, scale)

        self.icon_offsets = {
            name: offset for name, (_, offset) in icon_data.items()
        }

        self.unlocked = {
            "faerball": True,
            "molnia": True,
            "shield": True,
            "hilka": True,
            "mana": True
        }

        self.item_counts = {
            "hilka": 0,
            "mana": 0
        }
        self.max_count = 5

    def create_fallback_icon(self, icon_name, scale):
        """Создает простую цветную иконку как fallback"""
        colors = {
            "faerball": (255, 100, 0),    # Оранжевый
            "molnia": (255, 255, 0),      # Желтый
            "shield": (0, 100, 255),      # Синий
            "hilka": (255, 0, 100),       # Розовый
            "mana": (100, 0, 255)         # Фиолетовый
        }
        
        color = colors.get(icon_name, (100, 100, 100))
        
        # Создаем простую иконку
        class FallbackIcon:
            def __init__(self, color, scale):
                self.frame = pygame.Surface((int(128 * 0.9 * scale), int(128 * 0.9 * scale)), pygame.SRCALPHA)
                pygame.draw.circle(self.frame, color, 
                                 (int(64 * 0.9 * scale), int(64 * 0.9 * scale)), 
                                 int(32 * 0.9 * scale))
                pygame.draw.circle(self.frame, (255, 255, 255), 
                                 (int(64 * 0.9 * scale), int(64 * 0.9 * scale)), 
                                 int(32 * 0.9 * scale), 2)
            
            def update(self, dt):
                pass
            
            def get_frame(self):
                return self.frame
        
        return FallbackIcon(color, scale)

    def add_item(self, item_type):
        if item_type in self.item_counts:
            if self.item_counts[item_type] < self.max_count:
                self.item_counts[item_type] += 1

    def use_item(self, item_type):
        if self.item_counts.get(item_type, 0) > 0:
            self.item_counts[item_type] -= 1
            return True
        return False

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.speed:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)

        for icon in self.icons.values():
            if hasattr(icon, 'update'):
                icon.update(dt)

    def draw(self, surface):
        screen_w, screen_h = surface.get_size()
        frame = self.frames[self.index]
        inv_w, inv_h = frame.get_size()
        x = (screen_w - inv_w) // 2
        y = screen_h - inv_h - 10

        surface.blit(frame, (x, y))

        base_centers = [(24, 88), (39, 88), (55, 88), (72, 88), (87, 88)]

        for i, name in enumerate(self.slots):
            if self.unlocked.get(name, False) and i < len(base_centers):
                icon = self.icons.get(name)
                offset_x, offset_y = self.icon_offsets.get(name, (0, 0))
                if icon:
                    frame_icon = icon.get_frame()
                    cx = x + (base_centers[i][0] + offset_x) * self.scale
                    cy = y + (base_centers[i][1] + offset_y) * self.scale
                    ix = int(cx - frame_icon.get_width() / 2)
                    iy = int(cy - frame_icon.get_height() / 2)
                    surface.blit(frame_icon, (ix, iy))

                    if name in self.item_counts:
                        try:
                            font = safe_font(int(6 * self.scale))
                            value = str(self.item_counts[name])
                            spacing = 1
                            start_x = ix + 150
                            text_y = iy + 175

                            for j, digit in enumerate(value):
                                digit_surface = font.render(digit, True, (255, 255, 255))
                                surface.blit(digit_surface, (start_x + j * spacing, text_y))
                        except Exception as e:
                            print(f"Error rendering item count: {e}")