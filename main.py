# main.py - Complete game with menu integration, high scores and FIXED pause system
import pygame
import json
import random
import sys

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
from player import Player
from ghost import Ghost
from fireball import Fireball
from potion import Potion
from tank_ghost import TankGhost
from shooter_ghost import ShooterGhost
from lightning_spell import LightningSpell
from interface import Interface
from manamushroom import ManaMushroom
from inventory import Inventory
from shield_spell import PlayerLevel
from boss_pepe import BossPepe
from boss_strong import BossStrong
from config import config
from menu import MainMenu  # Menu integration
from high_score import HighScoreManager  # High score system
from pause_menu import PauseMenu  # Pause menu system
from upgrade_pill import UpgradePill  # НОВЫЙ ИМПОРТ
import os
import atexit
import math

def cleanup():
    """Cleanup on exit"""
    try:
        pygame.quit()
    except:
        pass

atexit.register(cleanup)

def resource_path(relative_path):
    """ Get resource path for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def safe_load_json(filename, default_value):
    """Safe JSON file loading"""
    try:
        path = resource_path(filename)
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        else:
            print(f"JSON file not found: {path}, using default")
            return default_value
    except Exception as e:
        print(f"Error loading {filename}: {e}, using default")
        return default_value

def safe_load_image(path, fallback_size=(64, 64)):
    """Safe image loading"""
    try:
        full_path = resource_path(path)
        if os.path.exists(full_path):
            return pygame.image.load(full_path)
        else:
            print(f"Image not found: {full_path}, creating fallback")
            surface = pygame.Surface(fallback_size)
            surface.fill((100, 100, 100))  # Gray color
            return surface
    except Exception as e:
        print(f"Error loading image {path}: {e}, creating fallback")
        surface = pygame.Surface(fallback_size)
        surface.fill((200, 100, 100))  # Reddish color for error
        return surface

def safe_font(size):
    """Safe font loading"""
    try:
        font_path = resource_path("assets/PressStart2P-Regular.ttf")
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
        else:
            print(f"Font not found: {font_path}, using system font")
            return pygame.font.Font(None, size)
    except Exception as e:
        print(f"Error loading font: {e}, using system font")
        return pygame.font.Font(None, size)

def show_game_over_screen_with_records(screen, font, final_score, final_level, final_wave, clock):
    """Show Game Over screen with high scores"""
    # Initialize score manager
    score_manager = HighScoreManager()
    
    # Add new score
    rank = score_manager.add_score(final_score, final_level, final_wave)
    is_new_record = score_manager.is_new_record(final_score)
    high_score = score_manager.get_high_score()
    
    overlay = pygame.Surface(screen.get_size())
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    
    # Show screen for 6 seconds
    for i in range(360):  # 6 seconds at 60 FPS
        screen.blit(overlay, (0, 0))
        
        try:
            # Game Over title
            if is_new_record and rank == 1:
                title_color = (255, 255, 0)  # Gold for new record
                title_text = "🏆 NEW HIGH SCORE! 🏆"
            elif rank and rank <= 3:
                title_color = (255, 150, 50)  # Orange for top-3
                title_text = "🌟 GREAT SCORE! 🌟"
            else:
                title_color = (255, 100, 100)  # Red for regular
                title_text = "GAME OVER"
            
            game_over_font = safe_font(28)
            game_over_surface = game_over_font.render(title_text, True, title_color)
            game_over_rect = game_over_surface.get_rect(center=(screen.get_width() // 2, 80))
            screen.blit(game_over_surface, game_over_rect)
            
            # Current result
            score_font = safe_font(16)
            
            current_score_text = f"Your Score: {final_score}"
            current_score_surface = score_font.render(current_score_text, True, (255, 255, 255))
            current_score_rect = current_score_surface.get_rect(center=(screen.get_width() // 2, 130))
            screen.blit(current_score_surface, current_score_rect)
            
            level_text = f"Level: {final_level}  •  Wave: {final_wave}"
            level_surface = score_font.render(level_text, True, (200, 200, 200))
            level_rect = level_surface.get_rect(center=(screen.get_width() // 2, 155))
            screen.blit(level_surface, level_rect)
            
            # Ranking information
            if rank:
                if rank == 1:
                    rank_text = "🥇 NEW HIGH SCORE!"
                    rank_color = (255, 255, 0)
                elif rank == 2:
                    rank_text = "🥈 2nd Place!"
                    rank_color = (192, 192, 192)
                elif rank == 3:
                    rank_text = "🥉 3rd Place!"
                    rank_color = (205, 127, 50)
                elif rank <= 5:
                    rank_text = f"🌟 #{rank} in Top 5!"
                    rank_color = (150, 255, 150)
                elif rank <= 10:
                    rank_text = f"📈 #{rank} in Top 10!"
                    rank_color = (150, 255, 150)
                else:
                    rank_text = f"Rank: #{rank}"
                    rank_color = (200, 200, 200)
                
                rank_surface = score_font.render(rank_text, True, rank_color)
                rank_rect = rank_surface.get_rect(center=(screen.get_width() // 2, 185))
                screen.blit(rank_surface, rank_rect)
            
            # High score
            record_text = f"High Score: {high_score}"
            record_surface = score_font.render(record_text, True, (255, 255, 100))
            record_rect = record_surface.get_rect(center=(screen.get_width() // 2, 215))
            screen.blit(record_surface, record_rect)
            
            # Top-5 scores
            top_scores = score_manager.get_top_scores(5)
            if top_scores:
                top_font = safe_font(12)
                
                top_title = "🏆 TOP SCORES 🏆"
                top_title_surface = top_font.render(top_title, True, (100, 255, 150))
                top_title_rect = top_title_surface.get_rect(center=(screen.get_width() // 2, 260))
                screen.blit(top_title_surface, top_title_rect)
                
                for idx, record in enumerate(top_scores):
                    # Color based on rank
                    if idx == 0:
                        color = (255, 255, 0)  # Gold
                        medal = "🥇"
                    elif idx == 1:
                        color = (192, 192, 192)  # Silver
                        medal = "🥈"
                    elif idx == 2:
                        color = (205, 127, 50)  # Bronze
                        medal = "🥉"
                    else:
                        color = (200, 200, 200)  # Regular
                        medal = f"{idx + 1}."
                    
                    # Highlight current result
                    if (record['score'] == final_score and 
                        record['level'] == final_level and 
                        record['wave'] == final_wave):
                        color = (100, 255, 100)  # Green for current
                        medal = "➤" + medal
                    
                    score_line = f"{medal} {record['score']} pts (Lv.{record['level']}, W.{record['wave']})"
                    score_surface = top_font.render(score_line, True, color)
                    score_rect = score_surface.get_rect(center=(screen.get_width() // 2, 290 + idx * 22))
                    screen.blit(score_surface, score_rect)
            
            # Progress bar showing time remaining
            progress_width = 300
            progress_height = 6
            progress_x = (screen.get_width() - progress_width) // 2
            progress_y = screen.get_height() - 80
            
            # Background
            pygame.draw.rect(screen, (50, 50, 50), (progress_x, progress_y, progress_width, progress_height))
            
            # Progress
            progress_ratio = 1 - (i / 360)
            progress_fill_width = int(progress_width * progress_ratio)
            if progress_ratio > 0.5:
                progress_color = (100, 255, 150)  # Green
            elif progress_ratio > 0.25:
                progress_color = (255, 255, 100)  # Yellow
            else:
                progress_color = (255, 150, 100)  # Orange
            
            pygame.draw.rect(screen, progress_color, (progress_x, progress_y, progress_fill_width, progress_height))
            
            # Instruction
            instruction_font = safe_font(10)
            instruction_text = "Returning to menu... (press any key to skip)"
            instruction_surface = instruction_font.render(instruction_text, True, (150, 150, 150))
            instruction_rect = instruction_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
            screen.blit(instruction_surface, instruction_rect)
            
        except Exception as e:
            print(f"Error drawing game over screen: {e}")
        
        pygame.display.flip()
        clock.tick(60)
        
        # Can skip with any key
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                return

def start_game_loop(screen, clock):
    """Main game loop - your original game code"""
    
    # Stop menu music and try to load game music
    pygame.mixer.music.stop()
    
    # Try to load game music
    try:
        game_music_files = [
            "assets/game_music.mp3",
            "assets/game_music.ogg",
            "assets/game_music.wav"
        ]
        
        music_loaded = False
        for music_file in game_music_files:
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.4)  # Lower volume during game
                pygame.mixer.music.play(-1)
                print(f"Game music loaded: {music_file}")
                music_loaded = True
                break
        
        if not music_loaded:
            print("No game music found - playing without music")
            
    except Exception as e:
        print(f"Game music error: {e}")
    
    # Get screen dimensions
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    
    # FPS tracking variable
    fps_counter = 0
    fps_timer = 0

    # Load background and game resources with safe loading
    background = safe_load_image("assets/background.png", (1200, 1200))
    original_bg_width, original_bg_height = background.get_size()

    # Fixed world size - 1200x1200
    TARGET_WORLD_SIZE = 1200
    bg_width = TARGET_WORLD_SIZE
    bg_height = TARGET_WORLD_SIZE

    # Scale background to needed size
    if original_bg_width != TARGET_WORLD_SIZE or original_bg_height != TARGET_WORLD_SIZE:
        background = pygame.transform.scale(background, (TARGET_WORLD_SIZE, TARGET_WORLD_SIZE))
        print(f"Background scaled from {original_bg_width}x{original_bg_height} to {TARGET_WORLD_SIZE}x{TARGET_WORLD_SIZE}")
    else:
        print(f"Background already correct size: {TARGET_WORLD_SIZE}x{TARGET_WORLD_SIZE}")

    game_over_image = safe_load_image("assets/game_over.png", (400, 300))
    font = safe_font(12)

    # Safe wall loading
    wall_data = safe_load_json("walls.json", [])
    walls = [pygame.Rect(*r) for r in wall_data]

    # If no walls, create basic boundary walls
    if not walls:
        print("No walls loaded, creating basic boundary walls")
        # Create world boundaries
        wall_thickness = 32
        walls = [
            pygame.Rect(0, 0, bg_width, wall_thickness),  # Top
            pygame.Rect(0, bg_height - wall_thickness, bg_width, wall_thickness),  # Bottom
            pygame.Rect(0, 0, wall_thickness, bg_height),  # Left
            pygame.Rect(bg_width - wall_thickness, 0, wall_thickness, bg_height),  # Right
        ]

    player = Player(bg_width // 2, bg_height // 2)
    player.max_hp = config.PLAYER_START_HP
    player.hp = config.PLAYER_START_HP
    player.max_mana = config.PLAYER_START_MANA
    player.mana = config.PLAYER_START_MANA

    player_level = PlayerLevel()
    interface = Interface(SCREEN_WIDTH, SCREEN_HEIGHT)
    inventory = Inventory(scale=2)

    # Boss system
    class BossManager:
        def __init__(self):
            self.boss_pepe = None
            self.boss_strong = None
            self.current_boss_type = "pepe"
            self.boss_cycle = 0
            self.boss_defeated = False
            self.boss_spawn_score = config.BOSS_SPAWN_SCORE_START
            self.boss_cooldown = 0
            self.boss_cooldown_duration = 10
            self.warning_time = 5
            self.showing_warning = False
            
        def update(self, dt, score, player, ghosts):
            if self.boss_cooldown > 0:
                self.boss_cooldown -= dt
                if self.boss_cooldown <= self.warning_time and not self.showing_warning:
                    self.showing_warning = True
                    
            if self.boss_pepe and self.boss_pepe.active:
                self.boss_pepe.update(dt, player, ghosts)
                if not self.boss_pepe.active:
                    self.boss_defeated = True
                    self.boss_cooldown = self.boss_cooldown_duration
                    self.showing_warning = False
                    
            if self.boss_strong and self.boss_strong.active:
                self.boss_strong.update(dt, player, ghosts)
                if not self.boss_strong.active:
                    self.boss_defeated = True
                    self.boss_cooldown = self.boss_cooldown_duration
                    self.showing_warning = False
                    
            if (score >= self.boss_spawn_score and 
                self.boss_cooldown <= 0 and 
                not self.has_active_boss()):
                self.spawn_next_boss()
                
        def has_active_boss(self):
            return ((self.boss_pepe and self.boss_pepe.active) or 
                    (self.boss_strong and self.boss_strong.active))
                    
        def spawn_next_boss(self):
            x = bg_width // 2 + random.randint(-100, 100)
            y = bg_height // 2 + random.randint(-100, 100)
            
            power_level = 1 + self.boss_cycle
            
            if self.current_boss_type == "pepe":
                self.boss_pepe = BossPepe(x, y, power_level)
                self.current_boss_type = "strong"
            else:
                self.boss_strong = BossStrong(x, y, power_level)
                self.current_boss_type = "pepe"
                self.boss_cycle += 1
                
            self.boss_spawn_score += 150 + self.boss_cycle * 50
            self.showing_warning = False
            
        def get_next_boss_name(self):
            if self.current_boss_type == "pepe":
                return f"PEPE BOSS LV.{1 + self.boss_cycle}"
            else:
                return f"STRONG BOSS LV.{1 + self.boss_cycle}"
            
        def draw(self, surface, camera_offset):
            if self.boss_pepe and self.boss_pepe.active:
                self.boss_pepe.draw(surface, camera_offset)
            if self.boss_strong and self.boss_strong.active:
                self.boss_strong.draw(surface, camera_offset)
                
            if self.showing_warning and self.boss_cooldown > 0:
                interface.draw_boss_warning(surface, self.get_next_boss_name(), self.boss_cooldown)
                
        def notify_ghost_killed(self):
            if self.boss_pepe and self.boss_pepe.active:
                self.boss_pepe.notify_ghost_killed()

    # Ghost wave system
    class WaveManager:
        def __init__(self):
            self.wave_number = 1
            self.ghosts_in_wave = 3
            self.wave_timer = 0
            self.wave_duration = 30
            self.spawn_timer = 0
            self.spawn_interval = 3
            self.ghosts_spawned_this_wave = 0
            
        def update(self, dt, ghosts, bg_width, bg_height):
            self.wave_timer += dt
            self.spawn_timer += dt
            
            if self.wave_timer >= self.wave_duration:
                self.start_new_wave()
                
            if (self.spawn_timer >= self.spawn_interval and 
                self.ghosts_spawned_this_wave < self.ghosts_in_wave):
                self.spawn_ghost(ghosts, bg_width, bg_height)
                
        def start_new_wave(self):
            self.wave_number += 1
            self.wave_timer = 0
            self.ghosts_spawned_this_wave = 0
            
            self.wave_duration = max(20, 30 - (self.wave_number - 1) * 1)
            
            base_increase = int(2 * config.DIFFICULTY_MULTIPLIER)
            self.ghosts_in_wave = 3 + (self.wave_number - 1) * base_increase
            self.spawn_interval = max(0.8, 3 - (self.wave_number - 1) * 0.15)
            
        def spawn_ghost(self, ghosts, bg_width, bg_height):
            margin = 100
            
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                x = random.randint(margin, bg_width - margin)
                y = random.randint(0, margin)
            elif side == 'bottom':
                x = random.randint(margin, bg_width - margin)
                y = random.randint(bg_height - margin, bg_height)
            elif side == 'left':
                x = random.randint(0, margin)
                y = random.randint(margin, bg_height - margin)
            else:
                x = random.randint(bg_width - margin, bg_width)
                y = random.randint(margin, bg_height - margin)
                
            if self.wave_number <= 2:
                ghost_types = [Ghost, Ghost, Ghost, TankGhost]
            elif self.wave_number <= 5:
                ghost_types = [Ghost, Ghost, TankGhost, ShooterGhost]
            else:
                ghost_types = [Ghost, TankGhost, TankGhost, ShooterGhost, ShooterGhost]
                
            ghost_type = random.choice(ghost_types)
            ghosts.append(ghost_type(x, y))
            
            self.ghosts_spawned_this_wave += 1
            self.spawn_timer = 0

    # Player progression system
    class PlayerProgression:
        def __init__(self, player):
            self.player = player
            self.experience = 0
            self.level = 1
            self.exp_for_next_level = 100
            self.stat_points = 0
            
        def add_experience(self, amount):
            self.experience += amount
            while self.experience >= self.exp_for_next_level:
                self.level_up()
                
        def level_up(self):
            self.experience -= self.exp_for_next_level
            self.level += 1
            self.exp_for_next_level = int(self.exp_for_next_level * 1.2)
            
            self.player.max_hp += 5
            self.player.hp = self.player.max_hp
            self.player.max_mana += 5
            self.player.mana = self.player.max_mana
            self.player.speed += 5
            
            return f"Level Up! Now level {self.level}"

    # Initialize systems
    boss_manager = BossManager()
    wave_manager = WaveManager()
    player_progression = PlayerProgression(player)

    ghosts = []
    fireballs = []
    lightnings = []

    previous_potion_score = 0
    level_text = ""
    level_text_timer = 0
    previous_mana_score = 0
    potion = None
    mana_mushroom = None
    score = 0

    # НОВЫЕ ПЕРЕМЕННЫЕ ДЛЯ УЛУЧШЕНИЙ
    upgrade_pill = None
    pill_spawn_timer = 0
    pill_spawn_cooldown = 30  # Каждые 30 секунд появляется таблетка
    pills_collected = 0  # Счетчик собранных таблеток

    running = True
    paused = False
    pause_menu = None  # NEW: Pause menu system
    camera_offset = pygame.Vector2(0, 0)

    print("Game started from menu!")

    while running:
        dt = clock.tick(config.FPS) / 1000
        
        # FPS counting
        fps_timer += dt
        fps_counter += 1
        current_fps = 60
        if fps_timer >= 1.0:
            current_fps = fps_counter / fps_timer
            fps_counter = 0
            fps_timer = 0

        # Get key states at the beginning of each frame
        keys = pygame.key.get_pressed()

        if not paused:
            player.taking_damage = False
            player.recover_mana(dt)

            # Spell unlock system
            if score >= 100 and player_level.level == 1:
                level_text = "Level 2 Unlocked: Lightning Spell!"
                level_text_timer = 3
                player_level.level_up()
            elif score >= 200 and player_level.level == 2:
                level_text = "Level 3 Unlocked: Shield Spell!"
                level_text_timer = 3
                player_level.level_up()

            # НОВЫЙ КОД: Периодический спавн таблеток
            pill_spawn_timer += dt

            # Спавним таблетку если игрок достиг 5 уровня и прошло достаточно времени
            if (player_progression.level >= 5 and 
                pill_spawn_timer >= pill_spawn_cooldown and 
                (not upgrade_pill or not upgrade_pill.active)):
                
                # Случайная позиция около центра карты
                center_x = bg_width // 2
                center_y = bg_height // 2
                
                # Добавляем случайное смещение от центра
                offset_x = random.randint(-300, 300)
                offset_y = random.randint(-300, 300)
                
                # Убеждаемся что таблетка в пределах карты
                pill_x = max(150, min(bg_width - 150, center_x + offset_x))
                pill_y = max(150, min(bg_height - 150, center_y + offset_y))
                
                # Создаем таблетку
                upgrade_pill = UpgradePill(pill_x, pill_y, "triple_shot")
                pill_spawn_timer = 0  # Сброс таймера
                
                # Уменьшаем кулдаун с прогрессом (минимум 15 секунд)
                pill_spawn_cooldown = max(15, 30 - wave_manager.wave_number)
                
                print(f"🌟 Triple Shot pill #{pills_collected + 1} spawned! Next in {pill_spawn_cooldown}s 🌟")

            # Обновление таблетки
            if upgrade_pill and upgrade_pill.active:
                upgrade_pill.update(dt)
                
                # Проверка подбора таблетки
                if player.rect.colliderect(upgrade_pill.rect):
                    upgrade_pill.active = False
                    upgrade_pill.collected = True
                    
                    if upgrade_pill.upgrade_type == "triple_shot":
                        player.activate_triple_shot()
                        pills_collected += 1
                        print(f"💊 Pills collected: {pills_collected}")

            # Update systems
            boss_manager.update(dt, score, player, ghosts)
            wave_manager.update(dt, ghosts, bg_width, bg_height)
            
            # Update player with wall checking
            player.update(keys, dt, walls)
            
            # Limit player to world boundaries
            margin = 50
            player.rect.x = max(margin, min(player.rect.x, bg_width - player.rect.width - margin))
            player.rect.y = max(margin, min(player.rect.y, bg_height - player.rect.height - margin))
            
            # Set camera AFTER player update
            camera_offset = pygame.math.Vector2(
                player.rect.centerx - SCREEN_WIDTH // 2,
                player.rect.centery - SCREEN_HEIGHT // 2
            )
            camera_offset.x = max(0, min(camera_offset.x, bg_width - SCREEN_WIDTH))
            camera_offset.y = max(0, min(camera_offset.y, bg_height - SCREEN_HEIGHT))

            if player.shield_cooldown > 0:
                player.shield_cooldown -= dt

            if potion and potion.active:
                potion.update(dt)
            if mana_mushroom and mana_mushroom.active:
                mana_mushroom.update(dt)

            for ghost in ghosts:
                ghost.update(dt, player)

            for fireball in fireballs[:]:
                fireball.update(dt)
                if fireball.timer > fireball.lifetime:
                    fireballs.remove(fireball)

            # Fireball collisions
            for fireball in fireballs[:]:
                # Damage to bosses
                if boss_manager.boss_strong and boss_manager.boss_strong.active and fireball.rect.colliderect(boss_manager.boss_strong.rect):
                    boss_manager.boss_strong.take_damage(5)
                    if fireball in fireballs:
                        fireballs.remove(fireball)
                    continue
                
                if boss_manager.boss_pepe and boss_manager.boss_pepe.active and fireball.rect.colliderect(boss_manager.boss_pepe.rect):
                    boss_manager.boss_pepe.take_damage(5)
                    if fireball in fireballs:
                        fireballs.remove(fireball)
                    continue
                    
                # Damage to ghosts
                for ghost in ghosts[:]:
                    if fireball.rect.colliderect(ghost.rect):
                        if hasattr(ghost, 'hp'):
                            ghost.hp -= 1
                            if ghost.hp <= 0:
                                ghosts.remove(ghost)
                                score += 10
                                player_progression.add_experience(10)
                                boss_manager.notify_ghost_killed()
                        else:
                            ghosts.remove(ghost)
                            score += 10
                            player_progression.add_experience(10)
                            boss_manager.notify_ghost_killed()
                        if fireball in fireballs:
                            fireballs.remove(fireball)
                        break

            
            if score - previous_potion_score >= 100 and (not potion or not potion.active):
                previous_potion_score = score
                attempts = 0
                while True:
                    x = random.randint(100, bg_width - 100)
                    y = random.randint(100, bg_height - 100)
                    new_potion = Potion(x, y)
                    if not any(new_potion.rect.colliderect(w) for w in walls):
                        potion = new_potion
                        break
                    attempts += 1
                    if attempts > 100:
                        break

            if score - previous_mana_score >= 150 and (not mana_mushroom or not mana_mushroom.active):
                previous_mana_score = score
                attempts = 0
                while True:
                    x = random.randint(100, bg_width - 100)
                    y = random.randint(100, bg_height - 100)
                    new_mana = ManaMushroom(x, y)
                    if not any(new_mana.rect.colliderect(w) for w in walls):
                        mana_mushroom = new_mana
                        break
                    attempts += 1
                    if attempts > 100:
                        break

            # Item pickup
            if potion and potion.active and player.rect.colliderect(potion.rect):
                inventory.add_item("hilka")
                potion.active = False

            if mana_mushroom and mana_mushroom.active and player.rect.colliderect(mana_mushroom.rect):
                inventory.add_item("mana")
                mana_mushroom.active = False

            for lightning in lightnings[:]:
                lightning.update(dt)
                if lightning.finished:
                    lightnings.remove(lightning)

            if level_text_timer > 0:
                level_text_timer -= dt

        # FIXED: Events handling - get events once and handle properly
        events = pygame.event.get()
        
        # Handle pause menu FIRST if paused
        if paused and pause_menu:
            pause_result = pause_menu.handle_events(events)
            
            if pause_result == "continue":
                paused = False
                pause_menu = None
            elif pause_result == "main_menu":
                # Return to main menu
                pygame.mixer.music.stop()
                return "menu"
            elif pause_result == "update_screen":
                # Update screen after fullscreen toggle
                SCREEN_WIDTH, SCREEN_HEIGHT = config.get_resolution()
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), config.get_screen_mode())
                interface = Interface(SCREEN_WIDTH, SCREEN_HEIGHT)
                pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Handle game events only if NOT paused
        if not paused:
            for event in events:
                if event.type == pygame.QUIT:
                    config.save_settings()
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Open pause menu
                        paused = True
                        pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
                    elif event.key == pygame.K_F11:
                        config.toggle_fullscreen()
                        SCREEN_WIDTH, SCREEN_HEIGHT = config.get_resolution()
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), config.get_screen_mode())
                        interface = Interface(SCREEN_WIDTH, SCREEN_HEIGHT)
                    elif event.key == pygame.K_p or event.key == pygame.K_PAUSE:
                        # Open pause menu
                        paused = True
                        pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
                    elif event.key == pygame.K_F3:
                        config.SHOW_FPS = not config.SHOW_FPS
                    elif event.key == pygame.K_F1:
                        config.SHOW_CONTROLS = not config.SHOW_CONTROLS
                    elif event.key == pygame.K_SPACE:
                        # НОВЫЙ КОД: Тройная стрельба
                        if player.has_triple_shot:
                            # Тройная стрельба: вперед, диагональ вверх, диагональ вниз
                            base_direction = 1 if player.facing == "right" else -1
                            
                            # Центральный снаряд (прямо)
                            direction_center = pygame.Vector2(base_direction, 0)
                            fireballs.append(Fireball(player.rect.centerx, player.rect.centery, direction_center))
                            
                            # Верхний диагональный снаряд
                            direction_up = pygame.Vector2(base_direction, -0.5).normalize()
                            fireballs.append(Fireball(player.rect.centerx, player.rect.centery, direction_up))
                            
                            # Нижний диагональный снаряд
                            direction_down = pygame.Vector2(base_direction, 0.5).normalize()
                            fireballs.append(Fireball(player.rect.centerx, player.rect.centery, direction_down))
                            
                            player.start_shoot_animation(base_direction)
                        else:
                            # Обычная стрельба
                            direction = pygame.Vector2(1 if player.facing == "right" else -1, 0)
                            fireballs.append(Fireball(player.rect.centerx, player.rect.centery, direction))
                            player.start_shoot_animation(direction.x)
                    elif event.key == pygame.K_q and player_level.unlock_lightning and player.mana >= 20:
                        player.mana -= 20
                        targets_hit = 0
                        player_pos = pygame.Vector2(player.rect.center)
                        
                        # Урон по призракам
                        for ghost in ghosts[:]:
                            dist = pygame.Vector2(ghost.rect.center) - player_pos
                            if dist.length() < 150:
                                lightnings.append(LightningSpell(ghost.rect.centerx, ghost.rect.centery))
                                ghost.hp = 0 if hasattr(ghost, 'hp') else None
                                if ghost in ghosts:
                                    ghosts.remove(ghost)
                                    score += 10
                                    player_progression.add_experience(15)
                                    boss_manager.notify_ghost_killed()
                                    targets_hit += 1
                        
                        # НОВЫЙ КОД: Урон по боссам
                        # Проверяем Boss Pepe
                        if boss_manager.boss_pepe and boss_manager.boss_pepe.active:
                            boss_pos = pygame.Vector2(boss_manager.boss_pepe.rect.center)
                            dist = boss_pos - player_pos
                            if dist.length() < 150:
                                lightnings.append(LightningSpell(boss_manager.boss_pepe.rect.centerx, boss_manager.boss_pepe.rect.centery))
                                boss_manager.boss_pepe.take_damage(15)
                                targets_hit += 1
                                print("⚡ Lightning hit Boss Pepe!")
                        
                        # Проверяем Boss Strong
                        if boss_manager.boss_strong and boss_manager.boss_strong.active:
                            boss_pos = pygame.Vector2(boss_manager.boss_strong.rect.center)
                            dist = boss_pos - player_pos
                            if dist.length() < 150:
                                lightnings.append(LightningSpell(boss_manager.boss_strong.rect.centerx, boss_manager.boss_strong.rect.centery))
                                boss_manager.boss_strong.take_damage(15)
                                targets_hit += 1
                                print("⚡ Lightning hit Boss Strong!")
                        
                        if targets_hit > 0:
                            player.start_shoot_animation(1 if player.facing == "right" else -1)
                    elif event.key == pygame.K_1:
                        if inventory.use_item("hilka"):
                            player.hp = min(player.max_hp, player.hp + 30)
                    elif event.key == pygame.K_2:
                        if inventory.use_item("mana"):
                            player.mana = min(player.max_mana, player.mana + 30)
                    elif event.key == pygame.K_e:
                        if player_level.unlock_shield and player.shield_cooldown <= 0:
                            player.shield.activate()
                            player.shield_cooldown = 15
        else:
            # If paused, still handle QUIT events
            for event in events:
                if event.type == pygame.QUIT:
                    config.save_settings()
                    return "quit"

        # Check player death
        if player.hp <= 0:
            show_game_over_screen_with_records(screen, font, score, player_progression.level, wave_manager.wave_number, clock)
            pygame.mixer.music.stop()
            return "menu"

        # Rendering
        screen.blit(background, (-camera_offset.x, -camera_offset.y))
        
        if not paused:
            player.draw(screen, camera_offset)
            boss_manager.draw(screen, camera_offset)
            
            for ghost in ghosts:
                ghost.draw(screen, camera_offset)
            for fireball in fireballs:
                fireball.draw(screen, camera_offset)
            for lightning in lightnings:
                lightning.draw(screen, camera_offset)
            if potion and potion.active:
                potion.draw(screen, camera_offset)
            if mana_mushroom and mana_mushroom.active:
                mana_mushroom.draw(screen, camera_offset)
            
            # НОВЫЙ КОД: Рисуем таблетку улучшения
            if upgrade_pill and upgrade_pill.active:
                upgrade_pill.draw(screen, camera_offset)
        else:
            # Draw everything with darkening on pause
            player.draw(screen, camera_offset)
            boss_manager.draw(screen, camera_offset)
            
            for ghost in ghosts:
                ghost.draw(screen, camera_offset)
            for fireball in fireballs:
                fireball.draw(screen, camera_offset)
            for lightning in lightnings:
                lightning.draw(screen, camera_offset)
            if potion and potion.active:
                potion.draw(screen, camera_offset)
            if mana_mushroom and mana_mushroom.active:
                mana_mushroom.draw(screen, camera_offset)
            
            # Рисуем таблетку даже на паузе
            if upgrade_pill and upgrade_pill.active:
                upgrade_pill.draw(screen, camera_offset)

        interface.draw(screen, player)
        inventory.draw(screen)

        # UI information
        score_text = font.render(f"{score}", True, (250, 235, 255))
        screen.blit(score_text, (140, 95))
        
        # Информация о таблетках
        if player_progression.level >= 5:
            if upgrade_pill and upgrade_pill.active:
                pill_info_text = "💊 TRIPLE SHOT PILL AVAILABLE!"
                pill_info_color = (255, 255, 0)
            else:
                next_pill_time = max(0, pill_spawn_cooldown - pill_spawn_timer)
                pill_info_text = f"💊 Next pill in: {int(next_pill_time)}s"
                pill_info_color = (200, 200, 200)
            
            pill_info_surface = font.render(pill_info_text, True, pill_info_color)
            screen.blit(pill_info_surface, (20, 140))
        
        # Wave information
        if not paused:
            time_until_next_wave = wave_manager.wave_duration - wave_manager.wave_timer
            interface.draw_wave_info(screen, wave_manager.wave_number, 
                                   wave_manager.ghosts_spawned_this_wave, 
                                   wave_manager.ghosts_in_wave, 
                                   time_until_next_wave)
        
        # Player statistics
        interface.draw_player_stats(screen, player_progression.level, 
                                  player_progression.experience, 
                                  player_progression.exp_for_next_level)
        
        # Show FPS if enabled
        if config.SHOW_FPS:
            interface.draw_fps_counter(screen, current_fps)
        
        # Show controls if enabled
        if config.SHOW_CONTROLS:
            interface.draw_controls_help(screen)

        if level_text_timer > 0:
            level_font = safe_font(12)
            level_surf = level_font.render(level_text, True, (255, 255, 0))
            level_rect = level_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
            screen.blit(level_surf, level_rect)
        
        # FIXED: Draw pause menu if paused (replaces old pause text)
        if paused and pause_menu:
            pause_menu.draw(screen)

        pygame.display.flip()

def main():
    """Main function with menu"""
    pygame.init()
    
    # Screen setup
    SCREEN_WIDTH, SCREEN_HEIGHT = config.get_resolution()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), config.get_screen_mode())
    pygame.display.set_caption("Mage vs Ghosts - Enhanced Edition")
    clock = pygame.time.Clock()
    
    # Initialize menu
    menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Main loop
    running = True
    while running:
        dt = clock.tick(config.FPS) / 1000.0
        
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # Update menu
        menu.update(dt)
        
        # Handle menu input
        menu_result = menu.handle_events(events)
        
        if menu_result == "start_game":
            print("Starting game...")
            game_result = start_game_loop(screen, clock)
            
            if game_result == "quit":
                running = False
            elif game_result == "menu":
                # Recreate menu to restart music
                menu.cleanup()
                menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
                
        elif menu_result == "exit":
            running = False
        
        # Draw menu
        menu.draw(screen)
        pygame.display.flip()
    
    # Cleanup
    menu.cleanup()
    config.save_settings()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()