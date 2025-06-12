import pygame
from safe_loader import safe_load_image

class DamageNumber:
    def __init__(self, x, y, sprite_path="1HP.png"):
        
        if not sprite_path.startswith("assets/"):
            sprite_path = f"assets/{sprite_path}"
            
        
        self.sheet = safe_load_image(sprite_path, (320, 32))  
        
        
        sheet_width = self.sheet.get_width()
        frame_width = 32  
        frame_count = max(1, sheet_width // frame_width)  # Минимум 1 кадр
        
        # Создаем кадры
        self.frames = []
        for i in range(frame_count):
            if i * frame_width < sheet_width:
                try:
                    frame_rect = pygame.Rect(i * frame_width, 0, min(frame_width, sheet_width - i * frame_width), 32)
                    frame = self.sheet.subsurface(frame_rect)
                    self.frames.append(frame)
                except:
                    # Если не удается создать subsurface, создаем простой кадр
                    fallback_frame = pygame.Surface((frame_width, 32), pygame.SRCALPHA)
                    fallback_frame.fill((255, 100, 100))  # Красный цвет для урона
                    
                    # Рисуем простой текст "-1"
                    try:
                        font = pygame.font.Font(None, 24)
                        text = font.render("-1", True, (255, 255, 255))
                        text_rect = text.get_rect(center=(frame_width//2, 16))
                        fallback_frame.blit(text, text_rect)
                    except:
                        pass
                    
                    self.frames.append(fallback_frame)
        
        # Если кадров нет, создаем один fallback кадр
        if not self.frames:
            fallback_frame = pygame.Surface((32, 32), pygame.SRCALPHA)
            fallback_frame.fill((255, 0, 0))
            try:
                font = pygame.font.Font(None, 20)
                text = font.render("-1", True, (255, 255, 255))
                text_rect = text.get_rect(center=(16, 16))
                fallback_frame.blit(text, text_rect)
            except:
                pass
            self.frames.append(fallback_frame)
        
        self.frame_index = 0
        self.animation_speed = 0.1
        self.timer = 0
        self.pos = pygame.Vector2(x, y)
        self.offset = 0
        self.finished = False

    def update(self, dt):
        self.timer += dt
        self.offset -= 20 * dt  
        
        if self.timer >= self.animation_speed:
            self.timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.finished = True

    def draw(self, surface, camera_offset):
        if not self.finished and self.frames:
            frame_index = min(self.frame_index, len(self.frames) - 1)
            frame = self.frames[frame_index]
            draw_x = self.pos.x - camera_offset.x
            draw_y = self.pos.y - camera_offset.y + self.offset
            surface.blit(frame, (draw_x, draw_y))