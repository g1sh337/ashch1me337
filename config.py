import pygame
import json
import os

class GameConfig:
    def __init__(self):
        # Базовые настройки экрана
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800
        self.FULLSCREEN = False
        self.FPS = 60
        
        # Настройки геймплея
        self.SHOW_FPS = False
        self.SHOW_CONTROLS = True
        self.DIFFICULTY_MULTIPLIER = 1.0  # Множитель сложности
        
        # Настройки звука (для будущего использования)
        self.MASTER_VOLUME = 0.7
        self.SFX_VOLUME = 0.8
        self.MUSIC_VOLUME = 0.6
        
        # Баланс игры
        self.PLAYER_START_HP = 45
        self.PLAYER_START_MANA = 45
        self.BOSS_SPAWN_SCORE_START = 100
        self.WAVE_DIFFICULTY_INCREASE = 1.2
        
        # Файл для сохранения настроек
        self.config_file = "game_settings.json"
        
        # Загружаем настройки при инициализации
        self.load_settings()
    
    def get_screen_mode(self):
        """Возвращает режим экрана для pygame"""
        if self.FULLSCREEN:
            return pygame.FULLSCREEN
        return 0
    
    def get_resolution(self):
        """Возвращает разрешение экрана"""
        if self.FULLSCREEN:
            # Получаем разрешение монитора
            info = pygame.display.Info()
            return (info.current_w, info.current_h)
        return (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
    
    def toggle_fullscreen(self):
        """Переключает полноэкранный режим"""
        self.FULLSCREEN = not self.FULLSCREEN
        return self.FULLSCREEN
    
    def save_settings(self):
        """Сохраняет настройки в файл"""
        settings = {
            'screen_width': self.SCREEN_WIDTH,
            'screen_height': self.SCREEN_HEIGHT,
            'fullscreen': self.FULLSCREEN,
            'fps': self.FPS,
            'show_fps': self.SHOW_FPS,
            'show_controls': self.SHOW_CONTROLS,
            'difficulty_multiplier': self.DIFFICULTY_MULTIPLIER,
            'master_volume': self.MASTER_VOLUME,
            'sfx_volume': self.SFX_VOLUME,
            'music_volume': self.MUSIC_VOLUME
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
            print("Settings saved successfully!")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        """Загружает настройки из файла"""
        if not os.path.exists(self.config_file):
            print("No config file found, using defaults")
            return
        
        try:
            with open(self.config_file, 'r') as f:
                settings = json.load(f)
            
            self.SCREEN_WIDTH = settings.get('screen_width', self.SCREEN_WIDTH)
            self.SCREEN_HEIGHT = settings.get('screen_height', self.SCREEN_HEIGHT)
            self.FULLSCREEN = settings.get('fullscreen', self.FULLSCREEN)
            self.FPS = settings.get('fps', self.FPS)
            self.SHOW_FPS = settings.get('show_fps', self.SHOW_FPS)
            self.SHOW_CONTROLS = settings.get('show_controls', self.SHOW_CONTROLS)
            self.DIFFICULTY_MULTIPLIER = settings.get('difficulty_multiplier', self.DIFFICULTY_MULTIPLIER)
            self.MASTER_VOLUME = settings.get('master_volume', self.MASTER_VOLUME)
            self.SFX_VOLUME = settings.get('sfx_volume', self.SFX_VOLUME)
            self.MUSIC_VOLUME = settings.get('music_volume', self.MUSIC_VOLUME)
            
            print("Settings loaded successfully!")
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def reset_to_defaults(self):
        """Сбрасывает настройки к значениям по умолчанию"""
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800
        self.FULLSCREEN = False
        self.FPS = 60
        self.SHOW_FPS = False
        self.SHOW_CONTROLS = True
        self.DIFFICULTY_MULTIPLIER = 1.0
        self.MASTER_VOLUME = 0.7
        self.SFX_VOLUME = 0.8
        self.MUSIC_VOLUME = 0.6
        
        self.save_settings()
        print("Settings reset to defaults!")

# Доступные разрешения экрана
AVAILABLE_RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1200, 800),
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
    (2560, 1440)
]

def get_optimal_resolution():
    """Определяет оптимальное разрешение для монитора"""
    pygame.init()
    info = pygame.display.Info()
    monitor_w, monitor_h = info.current_w, info.current_h
    
    # Ищем наибольшее подходящее разрешение (80% от размера монитора)
    target_w = int(monitor_w * 0.8)
    target_h = int(monitor_h * 0.8)
    
    best_resolution = (800, 600)  # Минимальное по умолчанию
    
    for res_w, res_h in AVAILABLE_RESOLUTIONS:
        if res_w <= target_w and res_h <= target_h:
            best_resolution = (res_w, res_h)
    
    return best_resolution

# Глобальный экземпляр конфигурации
config = GameConfig()