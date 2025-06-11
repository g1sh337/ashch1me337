from safe_loader import safe_load_image, safe_font
import pygame

class Interface:
    def __init__(self, screen_width=1200, screen_height=800):
        # Адаптивный масштаб в зависимости от размера экрана
        self.scale = max(1, min(screen_width // 600, screen_height // 400))
        
        # Загружаем изображения интерфейса
        self.interface_img = safe_load_image("assets/Interface.png")
        interface_scale = self.scale * 1.5  # Немного больше для читаемости
        self.interface_img = pygame.transform.scale(
            self.interface_img, 
            (int(self.interface_img.get_width() * interface_scale), 
             int(self.interface_img.get_height() * interface_scale))
        )

        # Загрузка кадров полосы здоровья
        health_sheet = safe_load_image("assets/healthsheet.png")
        health_scale = self.scale * 1.5
        health_sheet = pygame.transform.scale(
            health_sheet, 
            (int(health_sheet.get_width() * health_scale), 
             int(health_sheet.get_height() * health_scale))
        )
        
        frame_width = health_sheet.get_width() // 9
        frame_height = health_sheet.get_height()
        self.health_frames = [
            health_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)) 
            for i in range(9)
        ]

        # Загрузка кадров полосы маны
        mana_sheet = safe_load_image("assets/manasheet.png")
        mana_scale = self.scale * 1.5
        mana_sheet = pygame.transform.scale(
            mana_sheet, 
            (int(mana_sheet.get_width() * mana_scale), 
             int(mana_sheet.get_height() * mana_scale))
        )
        
        mana_frame_width = mana_sheet.get_width() // 9
        mana_frame_height = mana_sheet.get_height()
        self.mana_frames = [
            mana_sheet.subsurface(pygame.Rect(i * mana_frame_width, 0, mana_frame_width, mana_frame_height)) 
            for i in range(9)
        ]
        
        # Позиция интерфейса адаптивная
        self.interface_x = 10
        self.interface_y = 10

    def draw(self, surface, player):
        # Отрисовка основного интерфейса
        surface.blit(self.interface_img, (self.interface_x, self.interface_y))

        # Вычисляем индексы для полос здоровья и маны
        hp_ratio = max(0, min(1, player.hp / player.max_hp))
        mana_ratio = max(0, min(1, player.mana / player.max_mana))
        
        hp_index = int(hp_ratio * 8)  # 0-8 для 9 кадров
        mana_index = int(mana_ratio * 8)
        
        hp_index = max(0, min(hp_index, 8))
        mana_index = max(0, min(mana_index, 8))

        # Отрисовка полос здоровья и маны
        surface.blit(self.health_frames[hp_index], (self.interface_x, self.interface_y))
        surface.blit(self.mana_frames[mana_index], (self.interface_x, self.interface_y))
        
    def draw_boss_warning(self, surface, boss_name, time_until_spawn):
        """Отображает предупреждение о приближающемся боссе"""
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        try:
            font = safe_font(16)
            warning_text = f"WARNING: {boss_name} APPROACHING!"
            time_text = f"ETA: {int(time_until_spawn)}s"
            
            warning_surface = font.render(warning_text, True, (255, 100, 100))
            time_surface = font.render(time_text, True, (255, 200, 100))
            
            # Мигающий эффект
            alpha = int(128 + 127 * abs(pygame.time.get_ticks() % 1000 - 500) / 500)
            warning_surface.set_alpha(alpha)
            time_surface.set_alpha(alpha)
            
            # Центрируем текст
            warning_x = (screen_width - warning_surface.get_width()) // 2
            warning_y = screen_height // 4
            time_x = (screen_width - time_surface.get_width()) // 2
            time_y = warning_y + 30
            
            surface.blit(warning_surface, (warning_x, warning_y))
            surface.blit(time_surface, (time_x, time_y))
            
        except Exception as e:
            # Fallback если шрифт не найден
            print(f"Font error: {e}")
            
    def draw_wave_info(self, surface, wave_number, ghosts_spawned, total_ghosts, time_left):
        """Отображает информацию о текущей волне"""
        try:
            font = safe_font(12)
            wave_text = f"Wave {wave_number}: {ghosts_spawned}/{total_ghosts}"
            time_text = f"Next wave: {int(time_left)}s"
            
            wave_surface = font.render(wave_text, True, (255, 255, 255))
            time_surface = font.render(time_text, True, (200, 200, 255))
            
            # Позиция в левом нижнем углу
            wave_x = 10
            wave_y = surface.get_height() - 60
            time_x = 10
            time_y = surface.get_height() - 40
            
            surface.blit(wave_surface, (wave_x, wave_y))
            surface.blit(time_surface, (time_x, time_y))
            
        except Exception as e:
            print(f"Font error in wave info: {e}")
            
    def draw_player_stats(self, surface, level, experience, exp_needed):
        """Отображает статистики игрока"""
        try:
            font = safe_font(10)
            level_text = f"Level: {level}"
            exp_text = f"EXP: {experience}/{exp_needed}"
            
            level_surface = font.render(level_text, True, (255, 255, 255))
            exp_surface = font.render(exp_text, True, (100, 255, 100))
            
            # Позиция в правом верхнем углу
            level_x = surface.get_width() - level_surface.get_width() - 10
            level_y = 10
            exp_x = surface.get_width() - exp_surface.get_width() - 10
            exp_y = 30
            
            surface.blit(level_surface, (level_x, level_y))
            surface.blit(exp_surface, (exp_x, exp_y))
            
            # Полоса опыта
            exp_bar_width = 150
            exp_bar_height = 8
            exp_ratio = experience / exp_needed
            
            # Фон полосы опыта
            exp_bg_rect = pygame.Rect(
                surface.get_width() - exp_bar_width - 10,
                50,
                exp_bar_width,
                exp_bar_height
            )
            pygame.draw.rect(surface, (50, 50, 50), exp_bg_rect)
            
            # Полоса опыта
            exp_rect = pygame.Rect(
                surface.get_width() - exp_bar_width - 10,
                50,
                int(exp_bar_width * exp_ratio),
                exp_bar_height
            )
            pygame.draw.rect(surface, (100, 255, 100), exp_rect)
            
        except Exception as e:
            print(f"Font error in player stats: {e}")
            
    def draw_fps_counter(self, surface, fps):
        """Отображает счетчик FPS (опционально)"""
        try:
            font = safe_font(8)
            fps_text = f"FPS: {int(fps)}"
            fps_surface = font.render(fps_text, True, (150, 150, 150))
            
            surface.blit(fps_surface, (surface.get_width() - 80, surface.get_height() - 20))
            
        except Exception as e:
            pass  # FPS counter is optional
            
    def draw_controls_help(self, surface):
        """Отображает помощь по управлению под интерфейсом"""
        try:
            font = safe_font(8)
            controls = [
                "WASD - Move",
                "SPACE - Fireball", 
                "Q - Lightning",
                "E - Shield",
                "1/2 - Use Items"
            ]
            
            # Позиционируем под интерфейсом (учитываем высоту интерфейса)
            start_y = self.interface_y + self.interface_img.get_height() + 10
            
            for i, control in enumerate(controls):
                control_surface = font.render(control, True, (200, 200, 200))
                surface.blit(control_surface, (self.interface_x, start_y + i * 15))
                
        except Exception as e:
            pass  # Controls help is optional