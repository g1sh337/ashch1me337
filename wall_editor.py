import pygame
import json

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Wall Editor")
clock = pygame.time.Clock()

# Загрузи фон
background = pygame.image.load("assets/background.png").convert()
bg_width, bg_height = background.get_size()

camera_offset = pygame.Vector2(0, 0)
walls = []

grid_size = 32  # размер одной ячейки

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Добавление стены (ЛКМ)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            world_x = mx + camera_offset.x
            world_y = my + camera_offset.y
            rect = pygame.Rect(
                int(world_x // grid_size) * grid_size,
                int(world_y // grid_size) * grid_size,
                grid_size, grid_size
            )
            if rect not in walls:
                walls.append(rect)

        # Удаление стены (ПКМ)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            world_x = mx + camera_offset.x
            world_y = my + camera_offset.y
            for wall in walls:
                if wall.collidepoint(world_x, world_y):
                    walls.remove(wall)
                    break

        # Сохранить стены
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                with open("walls.json", "w") as f:
                    wall_data = [[r.x, r.y, r.width, r.height] for r in walls]
                    json.dump(wall_data, f)
                    print("💾 Walls saved to walls.json")
            elif event.key == pygame.K_ESCAPE:
                running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: camera_offset.x -= 200 * dt
    if keys[pygame.K_RIGHT]: camera_offset.x += 200 * dt
    if keys[pygame.K_UP]: camera_offset.y -= 200 * dt
    if keys[pygame.K_DOWN]: camera_offset.y += 200 * dt

    # Обрезка камеры
    camera_offset.x = max(0, min(camera_offset.x, bg_width - screen.get_width()))
    camera_offset.y = max(0, min(camera_offset.y, bg_height - screen.get_height()))

    # Отрисовка
    screen.blit(background, (-camera_offset.x, -camera_offset.y))

    for wall in walls:
        screen_rect = wall.move(-camera_offset.x, -camera_offset.y)
        pygame.draw.rect(screen, (255, 60, 60), screen_rect, 2)

    pygame.display.flip()

pygame.quit()
