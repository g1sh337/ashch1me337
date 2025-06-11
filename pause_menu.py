# pause_menu.py - Pause menu system
import pygame
from safe_loader import safe_font

class PauseMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Pause menu options
        self.pause_options = [
            "Continue",
            "Settings", 
            "Main Menu"
        ]
        
        self.selected_option = 0
        self.font_large = safe_font(24)
        self.font_medium = safe_font(18)
        self.font_small = safe_font(12)
        
        # Colors
        self.white = (255, 255, 255)
        self.yellow = (255, 255, 0)
        self.gray = (128, 128, 128)
        self.green = (100, 255, 150)
        
        # State
        self.state = "pause"  # pause, settings
        
    def handle_events(self, events):
        """Handle pause menu input"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.state == "pause":
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.pause_options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.pause_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.execute_option()
                    elif event.key == pygame.K_ESCAPE:
                        return "continue"  # ESC to continue
                        
                elif self.state == "settings":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "pause"
                        return None
                    elif event.key == pygame.K_F11:
                        from config import config
                        config.toggle_fullscreen()
                        return "update_screen"
                    elif event.key == pygame.K_F3:
                        from config import config
                        config.SHOW_FPS = not config.SHOW_FPS
                    elif event.key == pygame.K_F1:
                        from config import config
                        config.SHOW_CONTROLS = not config.SHOW_CONTROLS
        
        return None
    
    def execute_option(self):
        """Execute selected pause option"""
        option = self.pause_options[self.selected_option]
        
        if option == "Continue":
            return "continue"
        elif option == "Settings":
            self.state = "settings"
            return None
        elif option == "Main Menu":
            return "main_menu"
    
    def draw_pause_menu(self, surface):
        """Draw pause menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Pause menu background
        menu_width = 400
        menu_height = 300
        menu_x = (self.screen_width - menu_width) // 2
        menu_y = (self.screen_height - menu_height) // 2
        
        # Menu background with gradient effect
        menu_bg = pygame.Surface((menu_width, menu_height))
        for y in range(menu_height):
            ratio = y / menu_height
            r = int(20 + ratio * 30)
            g = int(40 + ratio * 50)
            b = int(20 + ratio * 30)
            color = (r, g, b)
            pygame.draw.line(menu_bg, color, (0, y), (menu_width, y))
        
        surface.blit(menu_bg, (menu_x, menu_y))
        
        # Border with glow effect
        for i in range(3):
            border_color = tuple(c // (i + 1) for c in self.green)
            pygame.draw.rect(surface, border_color, (menu_x - i, menu_y - i, menu_width + 2*i, menu_height + 2*i), 2)
        
        # Title
        title_text = "⏸️ GAME PAUSED ⏸️"
        title_surface = self.font_large.render(title_text, True, self.yellow)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, menu_y + 60))
        surface.blit(title_surface, title_rect)
        
        # Menu options
        start_y = menu_y + 120
        option_spacing = 50
        
        for i, option in enumerate(self.pause_options):
            color = self.yellow if i == self.selected_option else self.white
            
            # Selection indicator with animation
            if i == self.selected_option:
                indicator = "▶"
                indicator_surface = self.font_medium.render(indicator, True, self.green)
                indicator_rect = indicator_surface.get_rect(center=(self.screen_width // 2 - 80, start_y + i * option_spacing))
                surface.blit(indicator_surface, indicator_rect)
                
                # Highlight background
                highlight_rect = pygame.Rect(menu_x + 20, start_y + i * option_spacing - 20, menu_width - 40, 40)
                highlight_surface = pygame.Surface((menu_width - 40, 40))
                highlight_surface.set_alpha(50)
                highlight_surface.fill(self.green)
                surface.blit(highlight_surface, highlight_rect)
            
            option_surface = self.font_medium.render(option, True, color)
            option_rect = option_surface.get_rect(center=(self.screen_width // 2, start_y + i * option_spacing))
            surface.blit(option_surface, option_rect)
        
        # Controls hint
        controls_text = "↑↓ Navigate • ENTER Select • ESC Continue"
        controls_surface = self.font_small.render(controls_text, True, self.gray)
        controls_rect = controls_surface.get_rect(center=(self.screen_width // 2, menu_y + menu_height - 30))
        surface.blit(controls_surface, controls_rect)
    
    def draw_settings_menu(self, surface):
        """Draw settings in pause menu"""
        from config import config
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Settings background
        menu_width = 500
        menu_height = 450
        menu_x = (self.screen_width - menu_width) // 2
        menu_y = (self.screen_height - menu_height) // 2
        
        # Background with gradient
        menu_bg = pygame.Surface((menu_width, menu_height))
        for y in range(menu_height):
            ratio = y / menu_height
            r = int(20 + ratio * 30)
            g = int(40 + ratio * 50)
            b = int(20 + ratio * 30)
            color = (r, g, b)
            pygame.draw.line(menu_bg, color, (0, y), (menu_width, y))
        
        surface.blit(menu_bg, (menu_x, menu_y))
        
        # Border
        for i in range(3):
            border_color = tuple(c // (i + 1) for c in self.green)
            pygame.draw.rect(surface, border_color, (menu_x - i, menu_y - i, menu_width + 2*i, menu_height + 2*i), 2)
        
        # Title
        title_surface = self.font_large.render("⚙️ SETTINGS ⚙️", True, self.yellow)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, menu_y + 50))
        surface.blit(title_surface, title_rect)
        
        # Current settings
        current_settings = [
            "📺 DISPLAY:",
            f"Screen: {'Fullscreen' if config.FULLSCREEN else 'Windowed'}",
            f"FPS Display: {'ON' if config.SHOW_FPS else 'OFF'}",
            f"Controls Help: {'ON' if config.SHOW_CONTROLS else 'OFF'}",
            "",
            "⌨️ HOTKEYS:",
            "F11 - Toggle Fullscreen",
            "F3 - Toggle FPS Display", 
            "F1 - Toggle Controls Help",
            "",
            "🎮 GAME CONTROLS:",
            "WASD - Move",
            "SPACE - Fireball",
            "Q - Lightning (unlocked at level 2)",
            "E - Shield (unlocked at level 3)",
            "1/2 - Use Health/Mana Potions",
            "",
            "Press ESC to return"
        ]
        
        start_y = menu_y + 90
        for i, text in enumerate(current_settings):
            if text:
                if ":" in text and not text.startswith("F") and not text.startswith("WASD"):
                    color = self.yellow  # Section headers
                elif text.startswith("F") or text.startswith("WASD") or text.startswith("SPACE") or text.startswith("Q") or text.startswith("E") or text.startswith("1/2"):
                    color = self.green  # Hotkeys
                elif text.startswith("Screen:") or text.startswith("FPS") or text.startswith("Controls"):
                    color = self.white  # Settings values
                else:
                    color = self.gray   # Regular text
                
                text_surface = self.font_small.render(text, True, color)
                if ":" in text and not text.startswith("F"):
                    # Center section headers
                    text_rect = text_surface.get_rect(center=(self.screen_width // 2, start_y + i * 20))
                else:
                    # Left-align other text
                    text_rect = text_surface.get_rect(center=(self.screen_width // 2, start_y + i * 20))
                surface.blit(text_surface, text_rect)
    
    def draw(self, surface):
        """Main draw method"""
        if self.state == "pause":
            self.draw_pause_menu(surface)
        elif self.state == "settings":
            self.draw_settings_menu(surface)