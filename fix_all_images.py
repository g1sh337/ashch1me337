import os
import re


safe_loader_content = '''import pygame
import sys
import os
import json

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def safe_load_image(path, fallback_size=(64, 64), fallback_color=(100, 100, 100)):
    try:
        full_path = resource_path(path)
        if os.path.exists(full_path):
            return pygame.image.load(full_path).convert_alpha()
        else:
            print(f"Image not found: {full_path}, creating fallback")
            surface = pygame.Surface(fallback_size)
            surface.fill(fallback_color)
            return surface.convert_alpha()
    except Exception as e:
        print(f"Error loading image {path}: {e}, creating fallback")
        surface = pygame.Surface(fallback_size)
        surface.fill(fallback_color)
        return surface.convert_alpha()

def safe_font(size, font_path="assets/PressStart2P-Regular.ttf"):
    try:
        full_path = resource_path(font_path)
        if os.path.exists(full_path):
            return pygame.font.Font(full_path, size)
        else:
            return pygame.font.Font(None, size)
    except Exception as e:
        return pygame.font.Font(None, size)
'''

if not os.path.exists('safe_loader.py'):
    with open('safe_loader.py', 'w', encoding='utf-8') as f:
        f.write(safe_loader_content)
    print("Created safe_loader.py")

# Список файлов для исправления
files_to_fix = [
    'player.py', 'ghost.py', 'boss_pepe.py', 'boss_strong.py', 
    'interface.py', 'inventory.py', 'shield_spell.py', 
    'damage_number.py', 'fireball.py', 'lightning_spell.py',
    'potion.py', 'manamushroom.py', 'tank_ghost.py', 'shooter_ghost.py'
]

for filename in files_to_fix:
    if os.path.exists(filename):
        print(f"Fixing {filename}...")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Добавляем импорт safe_loader если его нет
        if 'from safe_loader import' not in content and 'safe_load_image' not in content:
            # Находим первый import pygame и добавляем после него
            if 'import pygame' in content:
                content = content.replace('import pygame', 'import pygame\nfrom safe_loader import safe_load_image, safe_font')
            else:
                content = 'from safe_loader import safe_load_image, safe_font\n' + content
        
        # Заменяем pygame.image.load на safe_load_image
        content = re.sub(r'pygame\.image\.load\(\s*"([^"]+)"\s*\)', r'safe_load_image("\1")', content)
        content = re.sub(r"pygame\.image\.load\(\s*'([^']+)'\s*\)", r"safe_load_image('\1')", content)
        
        # Заменяем .convert_alpha() если он идет сразу после загрузки
        content = re.sub(r'safe_load_image\(("[^"]+"|\'[^\']+\')\)\.convert_alpha\(\)', r'safe_load_image(\1)', content)
        
        # Заменяем pygame.font.Font для нашего шрифта
        content = re.sub(r'pygame\.font\.Font\(\s*"assets/PressStart2P-Regular\.ttf"\s*,\s*(\d+)\s*\)', r'safe_font(\1)', content)
        content = re.sub(r"pygame\.font\.Font\(\s*'assets/PressStart2P-Regular\.ttf'\s*,\s*(\d+)\s*\)", r'safe_font(\1)', content)
        
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed {filename}")
        else:
            print(f"- No changes needed in {filename}")

print("\n=== ИСПРАВЛЕНИЕ ЗАВЕРШЕНО ===")
print("Все файлы исправлены для безопасной загрузки ресурсов!")
print("\nТеперь выполните:")
print("pyinstaller --onefile --windowed --exclude-module pkg_resources --add-data \"assets;assets\" --add-data \"walls.json;.\" --add-data \"safe_loader.py;.\" --name=\"MageVsGhosts_Fixed\" main.py")