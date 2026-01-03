from safe_loader import safe_load_image, safe_font
import pygame
import math

def load_single_image(image_path, target_size=(64, 64), scale=2):
    """Загружает одиночное изображение и масштабирует его"""
    try:
        image = safe_load_image(image_path, target_size)
        scaled_size = (int(target_size[0] * scale), int(target_size[1] * scale))
        return pygame.transform.scale(image, scaled_size)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        scaled_size = (int(target_size[0] * scale), int(target_size[1] * scale))
        fallback = pygame.Surface(scaled_size)
        fallback.fill((255, 255, 0))  # Желтая таблетка
        return fallback

class UpgradePill:
    def __init__(self, x, y, upgrade_type="triple_shot"):
        self.x = x
        self.y = y
        self.upgrade_type = upgrade_type
        
        # Загружаем изображение таблетки
        self.image = load_single_image("assets/upgrade_pill_triple.png", (64, 64), scale=1.5)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Анимация
        self.float_timer = 0
        self.float_amplitude = 10
        self.pulse_timer = 0
        self.original_y = y
        
        # Эффекты
        self.glow_particles = []
        self.create_glow_particles()
        
        self.active = True
        self.collected = False

    def create_glow_particles(self):
        """Создает светящиеся частицы вокруг таблетки"""
        import random
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(30, 60)
            particle = {
                'angle': angle,
                'distance': distance,
                'speed': random.uniform(0.5, 1.5),
                'size': random.randint(2, 4),
                'alpha': random.uniform(0.5, 1.0),
                'color': random.choice([(255, 255, 0), (255, 200, 0), (255, 255, 100)])
            }
            self.glow_particles.append(particle)

    def update(self, dt):
        if not self.active:
            return
            
        # Плавающая анимация
        self.float_timer += dt * 2
        float_offset = math.sin(self.float_timer) * self.float_amplitude
        self.rect.centery = self.original_y + float_offset
        
        # Пульсация
        self.pulse_timer += dt * 3
        
        # Обновление частиц
        for particle in self.glow_particles:
            particle['angle'] += particle['speed'] * dt
            particle['alpha'] = 0.3 + 0.7 * abs(math.sin(self.pulse_timer + particle['angle']))

    def draw(self, surface, camera_offset):
        if not self.active:
            return
            
        # Рисуем светящиеся частицы
        for particle in self.glow_particles:
            x = self.rect.centerx + math.cos(particle['angle']) * particle['distance'] - camera_offset.x
            y = self.rect.centery + math.sin(particle['angle']) * particle['distance'] - camera_offset.y
            
            color = tuple(int(c * particle['alpha']) for c in particle['color'])
            pygame.draw.circle(surface, color, (int(x), int(y)), particle['size'])
        
        # Рисуем пульсирующее свечение вокруг таблетки
        pulse_intensity = 0.5 + 0.5 * abs(math.sin(self.pulse_timer))
        
        # Рисуем несколько слоев свечения
        for radius in range(50, 20, -5):
            alpha = int(30 * pulse_intensity * (50 - radius) / 30)
            glow_surface = pygame.Surface((radius * 2, radius * 2))
            glow_surface.set_alpha(alpha)
            glow_surface.fill((255, 255, 0))
            glow_rect = glow_surface.get_rect(center=(
                self.rect.centerx - camera_offset.x,
                self.rect.centery - camera_offset.y
            ))
            surface.blit(glow_surface, glow_rect)
        
        # Рисуем саму таблетку
        draw_pos = (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y)
        surface.blit(self.image, draw_pos)
        
        # Рисуем текст подсказку
        if hasattr(pygame.font, 'Font'):
            try:
                font = safe_font(12)
                hint_text = "TRIPLE SHOT!"
                hint_surface = font.render(hint_text, True, (255, 255, 255))
                hint_rect = hint_surface.get_rect(center=(
                    self.rect.centerx - camera_offset.x,
                    self.rect.top - 30 - camera_offset.y
                ))
                
                # Фон для текста
                bg_rect = hint_rect.inflate(10, 4)
                pygame.draw.rect(surface, (0, 0, 0, 150), bg_rect)
                surface.blit(hint_surface, hint_rect)
            except:
                pass