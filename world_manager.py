import pygame

class WorldManager:
    def __init__(self, background_path, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        
        self.original_background = pygame.image.load(background_path).convert()
        self.original_width, self.original_height = self.original_background.get_size()
        
        # Определяем нужен ли мир больше экрана
        self.world_width = max(self.original_width, screen_width + 400)  # +400 для буферной зоны
        self.world_height = max(self.original_height, screen_height + 400)
        
        # Создаем расширенный фон если нужно
        self.background = self.create_extended_background()
        
    def create_extended_background(self):
        """Создает расширенный фон, заполняя пустые области"""
        if (self.world_width <= self.original_width and 
            self.world_height <= self.original_height):
            return self.original_background
            
        # Создаем новую поверхность
        extended_bg = pygame.Surface((self.world_width, self.world_height))
        
        # Заполняем базовым цветом (берем цвет из угла фона)
        base_color = self.original_background.get_at((0, 0))
        extended_bg.fill(base_color)
        
        # Размещаем оригинальный фон в центре
        offset_x = (self.world_width - self.original_width) // 2
        offset_y = (self.world_height - self.original_height) // 2
        extended_bg.blit(self.original_background, (offset_x, offset_y))
        
        # Создаем паттерн для заполнения краев
        self.fill_edges(extended_bg, offset_x, offset_y)
        
        return extended_bg
    
    def fill_edges(self, surface, offset_x, offset_y):
        """Заполняет края поверхности паттерном из оригинального фона"""
        # Получаем образцы краев для заполнения
        
        # Левый край
        if offset_x > 0:
            edge_sample = self.original_background.subsurface((0, 0, 1, self.original_height))
            edge_scaled = pygame.transform.scale(edge_sample, (offset_x, self.original_height))
            surface.blit(edge_scaled, (0, offset_y))
            
        # Правый край
        if offset_x + self.original_width < self.world_width:
            edge_sample = self.original_background.subsurface((self.original_width-1, 0, 1, self.original_height))
            right_width = self.world_width - (offset_x + self.original_width)
            edge_scaled = pygame.transform.scale(edge_sample, (right_width, self.original_height))
            surface.blit(edge_scaled, (offset_x + self.original_width, offset_y))
            
        # Верхний край
        if offset_y > 0:
            edge_sample = self.original_background.subsurface((0, 0, self.original_width, 1))
            edge_scaled = pygame.transform.scale(edge_sample, (self.original_width, offset_y))
            surface.blit(edge_scaled, (offset_x, 0))
            
        # Нижний край
        if offset_y + self.original_height < self.world_height:
            edge_sample = self.original_background.subsurface((0, self.original_height-1, self.original_width, 1))
            bottom_height = self.world_height - (offset_y + self.original_height)
            edge_scaled = pygame.transform.scale(edge_sample, (self.original_width, bottom_height))
            surface.blit(edge_scaled, (offset_x, offset_y + self.original_height))
            
        # Углы заполняем средним цветом
        corner_color = self.get_average_corner_color()
        
        # Левый верхний угол
        if offset_x > 0 and offset_y > 0:
            pygame.draw.rect(surface, corner_color, (0, 0, offset_x, offset_y))
            
        # Правый верхний угол
        if offset_x + self.original_width < self.world_width and offset_y > 0:
            right_width = self.world_width - (offset_x + self.original_width)
            pygame.draw.rect(surface, corner_color, (offset_x + self.original_width, 0, right_width, offset_y))
            
        # Левый нижний угол
        if offset_x > 0 and offset_y + self.original_height < self.world_height:
            bottom_height = self.world_height - (offset_y + self.original_height)
            pygame.draw.rect(surface, corner_color, (0, offset_y + self.original_height, offset_x, bottom_height))
            
        # Правый нижний угол
        if (offset_x + self.original_width < self.world_width and 
            offset_y + self.original_height < self.world_height):
            right_width = self.world_width - (offset_x + self.original_width)
            bottom_height = self.world_height - (offset_y + self.original_height)
            pygame.draw.rect(surface, corner_color, 
                           (offset_x + self.original_width, offset_y + self.original_height, 
                            right_width, bottom_height))
    
    def get_average_corner_color(self):
        """Получает средний цвет углов фона"""
        corners = [
            self.original_background.get_at((0, 0)),
            self.original_background.get_at((self.original_width-1, 0)),
            self.original_background.get_at((0, self.original_height-1)),
            self.original_background.get_at((self.original_width-1, self.original_height-1))
        ]
        
        avg_r = sum(c[0] for c in corners) // 4
        avg_g = sum(c[1] for c in corners) // 4
        avg_b = sum(c[2] for c in corners) // 4
        
        return (avg_r, avg_g, avg_b)
    
    def get_spawn_bounds(self):
        """Возвращает границы для спавна объектов"""
        return (0, 0, self.world_width, self.world_height)
    
    def draw(self, surface, camera_offset):
        """Отрисовывает фон с учетом камеры"""
        surface.blit(self.background, (-camera_offset.x, -camera_offset.y))
    
    def is_position_valid(self, x, y, margin=50):
        """Проверяет, находится ли позиция в пределах мира"""
        return (margin <= x <= self.world_width - margin and 
                margin <= y <= self.world_height - margin)