import pygame
import os

pygame.init()

def create_damage_sprite(damage_text, filename):
    """Создает спрайт анимации урона"""
    frame_width = 32
    frame_height = 32
    frame_count = 8
    
    # Создаем поверхность для всех кадров
    sprite_sheet = pygame.Surface((frame_width * frame_count, frame_height), pygame.SRCALPHA)
    
    font = pygame.font.Font(None, 20)
    
    for i in range(frame_count):
        # Создаем кадр
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        
        # Эффект появления и исчезания
        alpha = int(255 * (1 - i / frame_count))
        
        # Цвет в зависимости от урона
        if "1" in damage_text:
            color = (255, 100, 100)  # Светло-красный
        elif "2" in damage_text:
            color = (255, 50, 50)    # Красный
        else:
            color = (255, 0, 0)      # Темно-красный
        
        # Рендерим текст
        text_surface = font.render(f"-{damage_text.replace('HP', '')}", True, (255, 255, 255))
        text_surface.set_alpha(alpha)
        
        # Добавляем фон
        pygame.draw.circle(frame, (*color, alpha//3), (frame_width//2, frame_height//2), 12)
        
        # Центрируем текст
        text_rect = text_surface.get_rect(center=(frame_width//2, frame_height//2))
        frame.blit(text_surface, text_rect)
        
        # Добавляем кадр к спрайт-листу
        sprite_sheet.blit(frame, (i * frame_width, 0))
    
    # Сохраняем
    pygame.image.save(sprite_sheet, f"assets/{filename}")
    print(f"Created: assets/{filename}")

# Создаем папку assets если её нет
if not os.path.exists('assets'):
    os.makedirs('assets')

# Создаем спрайты урона
create_damage_sprite("1HP", "1HP.png")
create_damage_sprite("2HP", "2HP.png")

print("Damage sprites created successfully!")
pygame.quit()