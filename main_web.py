# main_web.py - Pygbag Web Version with asyncio support
import asyncio
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
from menu import MainMenu
from high_score import HighScoreManager
from pause_menu import PauseMenu
from upgrade_pill import UpgradePill
import os
import math

def resource_path(relative_path):
    """ Get resource path for web """
    return relative_path

def safe_load_json(filename, default_value):
    """Safe JSON file loading"""
    try:
        if os.path.exists(filename):
            with open(filename) as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return default_value

def safe_font(size, font_path="assets/PressStart2P-Regular.ttf"):
    """Safe font loading"""
    try:
        return pygame.font.Font(font_path, size)
    except:
        return pygame.font.Font(None, size)

def safe_load_image(path, fallback_size=(64, 64), fallback_color=(100, 100, 100)):
    """Safe image loading"""
    try:
        img = pygame.image.load(path).convert_alpha()
        return img
    except Exception as e:
        print(f"Error loading {path}: {e}")
        fallback = pygame.Surface(fallback_size, pygame.SRCALPHA)
        fallback.fill(fallback_color)
        return fallback

def show_game_over_screen_with_records(screen, font, final_score, final_level, final_wave, clock):
    """Show Game Over screen with high scores"""
    high_score_manager = HighScoreManager()
    rank = high_score_manager.add_score(final_score, final_level, final_wave)
    top_scores = high_score_manager.get_top_scores(5)
    
    for i in range(360):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                return
        
        try:
            screen.fill((20, 20, 30))
            
            title_font = safe_font(24)
            title = title_font.render("GAME OVER", True, (255, 100, 100))
            title_rect = title.get_rect(center=(screen.get_width() // 2, 80))
            screen.blit(title, title_rect)
            
            score_font = safe_font(14)
            current_score_text = f"Your Score: {final_score}"
            current_score_surface = score_font.render(current_score_text, True, (255, 255, 150))
            current_score_rect = current_score_surface.get_rect(center=(screen.get_width() // 2, 130))
            screen.blit(current_score_surface, current_score_rect)
            
            level_text = f"Level: {final_level}  •  Wave: {final_wave}"
            level_surface = score_font.render(level_text, True, (200, 200, 200))
            level_rect = level_surface.get_rect(center=(screen.get_width() // 2, 155))
            screen.blit(level_surface, level_rect)
            
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
                else:
                    rank_text = f"#{rank} in Top Scores!"
                    rank_color = (150, 200, 255)
                
                rank_surface = score_font.render(rank_text, True, rank_color)
                rank_rect = rank_surface.get_rect(center=(screen.get_width() // 2, 185))
                screen.blit(rank_surface, rank_rect)
            
            top_title_font = safe_font(16)
            top_title = top_title_font.render("TOP SCORES", True, (200, 200, 255))
            top_title_rect = top_title.get_rect(center=(screen.get_width() // 2, 235))
            screen.blit(top_title, top_title_rect)
            
            top_font = safe_font(11)
            for idx, record in enumerate(top_scores):
                if idx == 0:
                    medal = "🥇"
                    color = (255, 255, 0)
                elif idx == 1:
                    medal = "🥈"
                    color = (192, 192, 192)
                elif idx == 2:
                    medal = "🥉"
                    color = (205, 127, 50)
                else:
                    medal = f"#{idx + 1}"
                    color = (180, 180, 180)
                
                if record['score'] == final_score and idx == rank - 1:
                    color = (255, 255, 150)
                
                score_line = f"{medal} {record['score']} pts (Lv.{record['level']}, W.{record['wave']})"
                score_surface = top_font.render(score_line, True, color)
                score_rect = score_surface.get_rect(center=(screen.get_width() // 2, 290 + idx * 22))
                screen.blit(score_surface, score_rect)
            
            progress_width = 300
            progress_height = 6
            progress_x = (screen.get_width() - progress_width) // 2
            progress_y = screen.get_height() - 80
            
            pygame.draw.rect(screen, (50, 50, 50), (progress_x, progress_y, progress_width, progress_height))
            
            progress_ratio = 1 - (i / 360)
            progress_fill_width = int(progress_width * progress_ratio)
            if progress_ratio > 0.5:
                progress_color = (100, 255, 150)
            elif progress_ratio > 0.25:
                progress_color = (255, 255, 100)
            else:
                progress_color = (255, 150, 100)
            
            pygame.draw.rect(screen, progress_color, (progress_x, progress_y, progress_fill_width, progress_height))
            
            instruction_font = safe_font(10)
            instruction_text = "Returning to menu... (press any key to skip)"
            instruction_surface = instruction_font.render(instruction_text, True, (150, 150, 150))
            instruction_rect = instruction_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
            screen.blit(instruction_surface, instruction_rect)
            
        except Exception as e:
            print(f"Error drawing game over screen: {e}")
        
        pygame.display.flip()
        await asyncio.sleep(0)  # Yield to browser
        clock.tick(60)

async def start_game_loop(screen, clock):
    """Main game loop - async version for Pygbag"""
    
    pygame.mixer.music.stop()
    
    # Music temporarily disabled for web version (MP3 not supported)
    # TODO: Convert music to OGG format
    try:
        # music_path = resource_path("assets/game_music.ogg")
        # if os.path.exists(music_path):
        #     pygame.mixer.music.load(music_path)
        #     pygame.mixer.music.set_volume(0.3)
        #     pygame.mixer.music.play(-1)
        pass
    except Exception as e:
        print(f"Could not load game music: {e}")
    
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()
    
    bg_width, bg_height = 1920, 1080
    bg = safe_load_image(resource_path("assets/background.png"), (bg_width, bg_height))
    bg = pygame.transform.scale(bg, (bg_width, bg_height))
    
    font = safe_font(14)
    
    # Load walls
    walls = safe_load_json("walls.json", [])
    walls = [pygame.Rect(w['x'], w['y'], w['width'], w['height']) for w in walls]
    
    player = Player(bg_width // 2, bg_height // 2, walls)
    player.hp = config.PLAYER_START_HP
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

    # Wave system
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

    # Player progression
    class PlayerProgression:
        def __init__(self, player):
            self.level = 1
            self.experience = 0
            self.exp_for_next_level = 100
            self.player = player
            
        def add_experience(self, amount):
            self.experience += amount
            if self.experience >= self.exp_for_next_level:
                self.level_up()
        
        def level_up(self):
            self.level += 1
            self.experience = 0
            self.exp_for_next_level = int(self.exp_for_next_level * 1.5)
            
            self.player.max_hp += 5
            self.player.hp = min(self.player.max_hp, self.player.hp + 10)
            self.player.max_mana += 5
            self.player.mana = min(self.player.max_mana, self.player.mana + 10)
            
            return f"LEVEL UP! Level {self.level}"

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

    running = True
    paused = False
    pause_menu = None
    camera_offset = pygame.Vector2(0, 0)

    pill_spawn_timer = 0
    pill_spawn_cooldown = 45
    upgrade_pills = []

    while running:
        dt = clock.tick(config.FPS) / 1000.0
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not paused:
                        paused = True
                        pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT, score, player_progression.level, wave_manager.wave_number)
                        pygame.mixer.music.pause()
                    else:
                        paused = False
                        pause_menu = None
                        pygame.mixer.music.unpause()
                
                if paused and pause_menu:
                    action = pause_menu.handle_input(event)
                    if action == "resume":
                        paused = False
                        pause_menu = None
                        pygame.mixer.music.unpause()
                    elif action == "restart":
                        return "restart"
                    elif action == "menu":
                        return "menu"
                    elif action == "exit":
                        return "quit"
                        
                if not paused:
                    if event.key == pygame.K_SPACE:
                        if player.mana >= 10:
                            player.mana -= 10
                            player.start_shoot_animation(1 if player.facing == "right" else -1)
                            
                            if player.facing == "right":
                                fireballs.append(Fireball(player.rect.centerx, player.rect.centery, 1, 0))
                            else:
                                fireballs.append(Fireball(player.rect.centerx, player.rect.centery, -1, 0))
                    
                    elif event.key == pygame.K_q:
                        if player_level.unlock_lightning and player.mana >= 25:
                            player.mana -= 25
                            ghosts_hit = 0
                            for ghost in ghosts[:]:
                                dist = pygame.math.Vector2(ghost.rect.centerx - player.rect.centerx,
                                                          ghost.rect.centery - player.rect.centery)
                                if dist.length() < 150:
                                    lightnings.append(LightningSpell(ghost.rect.centerx, ghost.rect.centery))
                                    ghost.hp = 0 if hasattr(ghost, 'hp') else None
                                    if ghost in ghosts:
                                        ghosts.remove(ghost)
                                        score += 10
                                        player_progression.add_experience(15)
                                        boss_manager.notify_ghost_killed()
                                        ghosts_hit += 1
                            if ghosts_hit > 0:
                                player.start_shoot_animation(1 if player.facing == "right" else -1)
                    
                    elif event.key == pygame.K_1:
                        if inventory.use_item("hilka"):
                            player.hp = min(player.max_hp, player.hp + 30)
                    
                    elif event.key == pygame.K_2:
                        if inventory.use_item("mana"):
                            player.mana = min(player.max_mana, player.mana + 30)
                    
                    elif event.key == pygame.K_e:
                        if player_level.unlock_shield and player.shield_cooldown <= 0:
                            player.shield_active = True
                            player.shield_timer = 0
                            player.shield_cooldown = 20

        if not paused:
            keys = pygame.key.get_pressed()
            
            if level_text_timer > 0:
                level_text_timer -= dt
            
            current_fps = clock.get_fps()
            
            if score >= previous_potion_score + 100:
                previous_potion_score += 100
                x = random.randint(100, bg_width - 100)
                y = random.randint(100, bg_height - 100)
                potion = Potion(x, y)
            
            if score >= previous_mana_score + 150:
                previous_mana_score += 150
                x = random.randint(100, bg_width - 100)
                y = random.randint(100, bg_height - 100)
                mana_mushroom = ManaMushroom(x, y)
            
            pill_spawn_timer += dt
            if pill_spawn_timer >= pill_spawn_cooldown:
                pill_spawn_timer = 0
                x = random.randint(100, bg_width - 100)
                y = random.randint(100, bg_height - 100)
                upgrade_pills.append(UpgradePill(x, y))
            
            for pill in upgrade_pills[:]:
                if pill.active:
                    pill.update(dt)
                    if pill.rect.colliderect(player.rect):
                        pill_type = pill.collect()
                        if pill_type == "hp":
                            player.max_hp += 15
                            player.hp = min(player.max_hp, player.hp + 15)
                        elif pill_type == "mana":
                            player.max_mana += 15
                            player.mana = min(player.max_mana, player.mana + 15)
                        elif pill_type == "triple":
                            player.max_hp += 10
                            player.hp = min(player.max_hp, player.hp + 10)
                            player.max_mana += 10
                            player.mana = min(player.max_mana, player.mana + 10)
                else:
                    upgrade_pills.remove(pill)
            
            if potion and potion.active:
                potion.update(dt)
                if potion.rect.colliderect(player.rect):
                    inventory.add_item("hilka")
                    potion.active = False
            
            if mana_mushroom and mana_mushroom.active:
                mana_mushroom.update(dt)
                if mana_mushroom.rect.colliderect(player.rect):
                    inventory.add_item("mana")
                    mana_mushroom.active = False
            
            for fireball in fireballs[:]:
                fireball.update(dt)
                if not fireball.active:
                    fireballs.remove(fireball)
                    continue
                
                for ghost in ghosts[:]:
                    if fireball.rect.colliderect(ghost.rect):
                        fireball.active = False
                        
                        if hasattr(ghost, 'hp'):
                            ghost.hp -= 10
                            if ghost.hp <= 0:
                                ghosts.remove(ghost)
                                score += 10
                                player_progression.add_experience(15)
                                boss_manager.notify_ghost_killed()
                        else:
                            ghosts.remove(ghost)
                            score += 10
                            player_progression.add_experience(15)
                            boss_manager.notify_ghost_killed()
                        break
                
                if boss_manager.boss_pepe and boss_manager.boss_pepe.active:
                    if fireball.rect.colliderect(boss_manager.boss_pepe.rect):
                        fireball.active = False
                        if boss_manager.boss_pepe.has_hp:
                            boss_manager.boss_pepe.take_damage(10)
                
                if boss_manager.boss_strong and boss_manager.boss_strong.active:
                    if fireball.rect.colliderect(boss_manager.boss_strong.rect):
                        fireball.active = False
                        boss_manager.boss_strong.take_damage(10)
            
            for lightning in lightnings[:]:
                lightning.update(dt)
                if not lightning.active:
                    lightnings.remove(lightning)
            
            for ghost in ghosts[:]:
                ghost.update(dt, player)
                if ghost.rect.colliderect(player.rect):
                    if not player.shield_active:
                        player.hp -= 1
            
            if boss_manager.boss_pepe and boss_manager.boss_pepe.active:
                if boss_manager.boss_pepe.rect.colliderect(player.rect):
                    if not player.shield_active:
                        player.hp -= boss_manager.boss_pepe.damage * dt
            
            if boss_manager.boss_strong and boss_manager.boss_strong.active:
                if boss_manager.boss_strong.rect.colliderect(player.rect):
                    if not player.shield_active:
                        player.hp -= boss_manager.boss_strong.damage * dt
            
            if player.hp <= 0:
                await show_game_over_screen_with_records(screen, font, score, player_progression.level, wave_manager.wave_number, clock)
                return "menu"
            
            if player.shield_active:
                player.shield_timer += dt
                if player.shield_timer >= 5:
                    player.shield_active = False
            
            if player_progression.experience >= player_progression.exp_for_next_level:
                level_text = player_progression.level_up()
                level_text_timer = 3
                player_level.level_up()
            
            boss_manager.update(dt, score, player, ghosts)
            wave_manager.update(dt, ghosts, bg_width, bg_height)
            
            player.update(keys, dt, walls)
            
            margin = 50
            player.rect.x = max(margin, min(player.rect.x, bg_width - player.rect.width - margin))
            player.rect.y = max(margin, min(player.rect.y, bg_height - player.rect.height - margin))
            
            camera_offset = pygame.math.Vector2(
                player.rect.centerx - SCREEN_WIDTH // 2,
                player.rect.centery - SCREEN_HEIGHT // 2
            )
            camera_offset.x = max(0, min(camera_offset.x, bg_width - SCREEN_WIDTH))
            camera_offset.y = max(0, min(camera_offset.y, bg_height - SCREEN_HEIGHT))

            if player.shield_cooldown > 0:
                player.shield_cooldown -= dt
        
        # Drawing
        screen.blit(bg, (-camera_offset.x, -camera_offset.y))
        
        if not paused:
            player.draw(screen, camera_offset)
            boss_manager.draw(screen, camera_offset)
            
            for ghost in ghosts:
                ghost.draw(screen, camera_offset)
            for fireball in fireballs:
                fireball.draw(screen, camera_offset)
            for lightning in lightnings:
                lightning.draw(screen, camera_offset)
            for pill in upgrade_pills:
                if pill.active:
                    pill.draw(screen, camera_offset)
            if potion and potion.active:
                potion.draw(screen, camera_offset)
            if mana_mushroom and mana_mushroom.active:
                mana_mushroom.draw(screen, camera_offset)
        else:
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

        interface.draw(screen, player)
        inventory.draw(screen)

        score_text = font.render(f"{score}", True, (250, 235, 255))
        screen.blit(score_text, (140, 95))
        
        if not paused:
            if upgrade_pills:
                pill_info_text = f"💊 Active: {len(upgrade_pills)}"
                pill_info_color = (255, 200, 255)
            else:
                next_pill_time = max(0, pill_spawn_cooldown - pill_spawn_timer)
                pill_info_text = f"💊 Next pill in: {int(next_pill_time)}s"
                pill_info_color = (200, 200, 200)
            
            pill_info_surface = font.render(pill_info_text, True, pill_info_color)
            screen.blit(pill_info_surface, (20, 140))
        
        if not paused:
            time_until_next_wave = wave_manager.wave_duration - wave_manager.wave_timer
            interface.draw_wave_info(screen, wave_manager.wave_number, 
                                   wave_manager.ghosts_spawned_this_wave, 
                                   wave_manager.ghosts_in_wave, 
                                   time_until_next_wave)
        
        interface.draw_player_stats(screen, player_progression.level, 
                                  player_progression.experience, 
                                  player_progression.exp_for_next_level)
        
        if config.SHOW_FPS:
            interface.draw_fps_counter(screen, current_fps)
        
        if config.SHOW_CONTROLS:
            interface.draw_controls_help(screen)

        if level_text_timer > 0:
            level_font = safe_font(12)
            level_surf = level_font.render(level_text, True, (255, 255, 0))
            level_rect = level_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
            screen.blit(level_surf, level_rect)
        
        if paused and pause_menu:
            pause_menu.draw(screen)

        pygame.display.flip()
        await asyncio.sleep(0)  # Critical for Pygbag

async def main():
    """Main function with menu - async version"""
    pygame.init()
    
    SCREEN_WIDTH, SCREEN_HEIGHT = config.get_resolution()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), config.get_screen_mode())
    pygame.display.set_caption("The LEGEND of ASHCHIME")
    clock = pygame.time.Clock()
    
    menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    running = True
    while running:
        dt = clock.tick(config.FPS) / 1000.0
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        menu.update(dt)
        
        menu_result = menu.handle_events(events)
        
        if menu_result == "start_game":
            print("Starting game...")
            game_result = await start_game_loop(screen, clock)
            
            if game_result == "quit":
                running = False
            elif game_result == "menu" or game_result == "restart":
                menu.cleanup()
                menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
                
        elif menu_result == "exit":
            running = False
        
        menu.draw(screen)
        pygame.display.flip()
        await asyncio.sleep(0)  # Critical for Pygbag
    
    menu.cleanup()
    config.save_settings()
    pygame.quit()

# Pygbag entry point
asyncio.run(main())
