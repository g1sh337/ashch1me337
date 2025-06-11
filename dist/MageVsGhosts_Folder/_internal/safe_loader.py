import pygame
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
