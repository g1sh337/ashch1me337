# menu.py - Complete menu with nature background
import pygame
import sys
import os
from safe_loader import safe_load_image, safe_font
from config import config

class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create nature background
        self.create_background()
        
        # Load music
        self.load_music()
        
        # Menu options
        self.menu_options = [
            "New Game",
            "High Scores",
            "Exit"
        ]
        
        self.selected_option = 0
        self.font_large = safe_font(32)
        self.font_medium = safe_font(20)
        self.font_small = safe_font(14)
        
        # Colors
        self.white = (255, 255, 255)
        self.yellow = (255, 255, 0)
        self.gray = (128, 128, 128)
        self.green = (100, 255, 150)
        
        # Animation
        self.title_bounce = 0
        self.firefly_timer = 0
        self.fireflies = []
        self.create_fireflies()
        
        # Menu state
        self.state = "main"  # main, high_scores
        
    def create_background(self):
        """Create nature/forest background"""
        # Try to load custom background first
        if os.path.exists("assets/menu_background.png"):
            self.background = safe_load_image("assets/menu_background.png")
            self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
            return
        
        # Create forest gradient background
        self.background = pygame.Surface((self.screen_width, self.screen_height))
        
        # Forest gradient from dark green to lighter green
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(10 + ratio * 40)    # Dark green to forest green
            g = int(30 + ratio * 80)    # Main green component
            b = int(10 + ratio * 30)    # Minimal blue for natural look
            color = (r, g, b)
            pygame.draw.line(self.background, color, (0, y), (self.screen_width, y))
        
        # Add fireflies/magical lights
        import random
        for _ in range(60):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            size = random.randint(2, 6)
            
            # Yellow-green fireflies
            if random.random() < 0.7:
                color = (200, 255, 100)  # Yellow-green
            else:
                color = (100, 255, 200)  # Turquoise
            
            pygame.draw.circle(self.background, color, (x, y), size)
            # Add glow effect
            for r in range(size + 3, size, -1):
                fade_color = tuple(c // 3 for c in color)
                pygame.draw.circle(self.background, fade_color, (x, y), r)
    
    def create_fireflies(self):
        """Create animated fireflies"""
        import random
        for _ in range(15):
            firefly = {
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height),
                'dx': random.uniform(-20, 20),
                'dy': random.uniform(-20, 20),
                'size': random.randint(2, 4),
                'brightness': random.uniform(0.5, 1.0),
                'pulse_speed': random.uniform(2, 5),
                'color': random.choice([(200, 255, 100), (100, 255, 200), (255, 255, 150)])
            }
            self.fireflies.append(firefly)
    
    def update_fireflies(self, dt):
        """Update firefly animation"""
        import math
        
        for firefly in self.fireflies:
            # Move firefly
            firefly['x'] += firefly['dx'] * dt
            firefly['y'] += firefly['dy'] * dt
            
            # Bounce off edges
            if firefly['x'] <= 0 or firefly['x'] >= self.screen_width:
                firefly['dx'] *= -1
            if firefly['y'] <= 0 or firefly['y'] >= self.screen_height:
                firefly['dy'] *= -1
            
            # Keep within bounds
            firefly['x'] = max(0, min(self.screen_width, firefly['x']))
            firefly['y'] = max(0, min(self.screen_height, firefly['y']))
            
            # Update pulsing brightness
            firefly['brightness'] = 0.3 + 0.7 * abs(math.sin(self.firefly_timer * firefly['pulse_speed']))
    
    def load_music(self):
        """Load menu music"""
        print("🎵 Trying to load menu music...")
        
        try:
            pygame.mixer.init()
            print("✅ Pygame mixer initialized")
            
            # Check for assets folder
            if not os.path.exists("assets"):
                print("❌ assets folder not found!")
                return
            else:
                print("✅ assets folder found")
            
            # Try to find music
            music_files = [
                "assets/menu_music.mp3",
                "assets/menu_music.ogg", 
                "assets/menu_music.wav"
            ]
            
            print("🔍 Looking for music files...")
            for music_file in music_files:
                print(f"   Checking: {music_file}")
                if os.path.exists(music_file):
                    print(f"✅ Found: {music_file}")
                    try:
                        pygame.mixer.music.load(music_file)
                        pygame.mixer.music.set_volume(0.5)
                        pygame.mixer.music.play(-1)  # Loop forever
                        print(f"🎵 Music playing: {music_file}")
                        return
                    except Exception as e:
                        print(f"❌ Failed to play {music_file}: {e}")
                else:
                    print(f"❌ Not found: {music_file}")
            
            print("❌ No menu music found - running without music")
                
        except Exception as e:
            print(f"❌ Music system error: {e}")
    
    def handle_events(self, events):
        """Handle menu input events"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.state == "main":
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.execute_option()
                
                elif self.state == "high_scores":
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.state = "main"
        
        return None
    
    def execute_option(self):
        """Execute selected menu option"""
        option = self.menu_options[self.selected_option]
        
        if option == "New Game":
            return "start_game"
        elif option == "High Scores":
            self.state = "high_scores"
            return None
        elif option == "Exit":
            return "exit"
    
    def update(self, dt):
        """Update menu animations"""
        self.title_bounce += dt * 2
        self.firefly_timer += dt
        self.update_fireflies(dt)
    
    def draw_main_menu(self, surface):
        """Draw the main menu"""
        import math
        
        # Draw background
        surface.blit(self.background, (0, 0))
        
        # Draw animated fireflies
        for firefly in self.fireflies:
            color = tuple(int(c * firefly['brightness']) for c in firefly['color'])
            pygame.draw.circle(surface, color, 
                             (int(firefly['x']), int(firefly['y'])), 
                             firefly['size'])
            
            # Add subtle glow
            glow_color = tuple(int(c * firefly['brightness'] * 0.3) for c in firefly['color'])
            pygame.draw.circle(surface, glow_color, 
                             (int(firefly['x']), int(firefly['y'])), 
                             firefly['size'] + 2)
        
        # Draw title with bounce effect
        title_text = "THE LEGEND of ASHCHIME"
        title_y_offset = int(math.sin(self.title_bounce) * 10)
        title_surface = self.font_large.render(title_text, True, self.yellow)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 150 + title_y_offset))
        
        # Add nature-themed glow effect to title
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            glow_surface = self.font_large.render(title_text, True, self.green)
            glow_rect = title_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            surface.blit(glow_surface, glow_rect)
        
        surface.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_text = "Enhanced Edition"
        subtitle_surface = self.font_medium.render(subtitle_text, True, self.white)
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, 200))
        surface.blit(subtitle_surface, subtitle_rect)
        
        # Draw menu options
        start_y = 350
        option_spacing = 80
        
        for i, option in enumerate(self.menu_options):
            color = self.yellow if i == self.selected_option else self.white
            
            # Add selection indicator
            if i == self.selected_option:
                indicator = "🌿"  # Nature theme
                indicator_surface = self.font_medium.render(indicator, True, self.green)
                indicator_rect = indicator_surface.get_rect(center=(self.screen_width // 2 - 120, start_y + i * option_spacing))
                surface.blit(indicator_surface, indicator_rect)
            
            option_surface = self.font_medium.render(option, True, color)
            option_rect = option_surface.get_rect(center=(self.screen_width // 2, start_y + i * option_spacing))
            surface.blit(option_surface, option_rect)
        
        # Draw controls hint
        controls_text = "Use ARROW KEYS to navigate, ENTER to select"
        controls_surface = self.font_small.render(controls_text, True, self.gray)
        controls_rect = controls_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        surface.blit(controls_surface, controls_rect)
    
    def draw_high_scores(self, surface):
        """Draw high scores screen"""
        from high_score import HighScoreManager
        
        # Draw dimmed background
        surface.blit(self.background, (0, 0))
        
        # Draw dimmed fireflies
        for firefly in self.fireflies:
            color = tuple(int(c * firefly['brightness'] * 0.3) for c in firefly['color'])
            pygame.draw.circle(surface, color, 
                             (int(firefly['x']), int(firefly['y'])), 
                             firefly['size'])
        
        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # High scores title
        title_surface = self.font_large.render("🏆 HIGH SCORES 🏆", True, self.yellow)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100))
        surface.blit(title_surface, title_rect)
        
        # Load and display scores
        try:
            score_manager = HighScoreManager()
            top_scores = score_manager.get_top_scores(10)
            
            if top_scores:
                start_y = 180
                for i, record in enumerate(top_scores):
                    # Medal/rank
                    if i == 0:
                        medal = "🥇"
                        color = (255, 255, 0)  # Gold
                    elif i == 1:
                        medal = "🥈"
                        color = (192, 192, 192)  # Silver
                    elif i == 2:
                        medal = "🥉"
                        color = (205, 127, 50)  # Bronze
                    else:
                        medal = f"{i + 1}."
                        color = (200, 200, 200)  # Regular
                    
                    # Score line
                    score_text = f"{medal} {record['score']} pts"
                    details_text = f"Level {record['level']} • Wave {record['wave']} • {record['date']}"
                    
                    score_surface = self.font_medium.render(score_text, True, color)
                    details_surface = self.font_small.render(details_text, True, self.gray)
                    
                    score_rect = score_surface.get_rect(center=(self.screen_width // 2, start_y + i * 45))
                    details_rect = details_surface.get_rect(center=(self.screen_width // 2, start_y + i * 45 + 20))
                    
                    surface.blit(score_surface, score_rect)
                    surface.blit(details_surface, details_rect)
            else:
                no_scores_text = "No high scores yet!"
                no_scores_surface = self.font_medium.render(no_scores_text, True, self.gray)
                no_scores_rect = no_scores_surface.get_rect(center=(self.screen_width // 2, 300))
                surface.blit(no_scores_surface, no_scores_rect)
                
                hint_text = "Play the game to set your first record!"
                hint_surface = self.font_small.render(hint_text, True, self.gray)
                hint_rect = hint_surface.get_rect(center=(self.screen_width // 2, 330))
                surface.blit(hint_surface, hint_rect)
        
        except Exception as e:
            error_text = "Error loading high scores"
            error_surface = self.font_medium.render(error_text, True, (255, 100, 100))
            error_rect = error_surface.get_rect(center=(self.screen_width // 2, 300))
            surface.blit(error_surface, error_rect)
        
        # Back instruction
        back_text = "Press ESCAPE or ENTER to return"
        back_surface = self.font_small.render(back_text, True, self.white)
        back_rect = back_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        surface.blit(back_surface, back_rect)
    
    def draw(self, surface):
        """Main draw method"""
        if self.state == "main":
            self.draw_main_menu(surface)
        elif self.state == "high_scores":
            self.draw_high_scores(surface)
    
    def cleanup(self):
        """Clean up resources"""
        try:
            pygame.mixer.music.stop()
        except:
            pass