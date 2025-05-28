import pygame
import json
import random
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

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Mage vs Ghosts")
clock = pygame.time.Clock()

background = pygame.image.load("assets/background.png").convert()
bg_width, bg_height = background.get_size()

game_over_image = pygame.image.load("assets/game_over.png").convert_alpha()
font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 12)

with open("walls.json") as f:
    wall_data = json.load(f)
    walls = [pygame.Rect(*r) for r in wall_data]

player = Player(bg_width // 2, bg_height // 2)
player_level = PlayerLevel()
interface = Interface()
inventory = Inventory(scale=2)

boss_pepe = None
boss_pepe_spawned = False
boss_strong = None
boss_strong_spawned = False

ghosts = [Ghost(200, 200), Ghost(600, 400), Ghost(800, 800)]
fireballs = []
lightnings = []

ghost_spawn_timer = 0
ghost_spawn_interval = 3
previous_potion_score = 0
level_text = ""
level_text_timer = 0
previous_mana_score = 0
potion = None
mana_mushroom = None
score = 0

running = True
while running:
    dt = clock.tick(60) / 1000
    player.taking_damage = False
    player.recover_mana(dt)

    if score >= 100 and player_level.level == 1:
        level_text = "Level 2 Unlocked: ⚡ Lightning!"
        level_text_timer = 3
        player_level.level_up()
    elif score >= 200 and player_level.level == 2:
        level_text = "Level 3 Unlocked: 🛡 Shield!"
        level_text_timer = 3
        player_level.level_up()

    if score >= 500 and not boss_pepe_spawned:
        boss_pepe = BossPepe(bg_width // 2, 100)
        boss_pepe_spawned = True

    if score >= 50 and not boss_strong_spawned:
        boss_strong = BossStrong(bg_width // 2, 150)
        boss_strong_spawned = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                direction = pygame.Vector2(1 if player.facing == "right" else -1, 0)
                fireballs.append(Fireball(player.rect.centerx, player.rect.centery, direction))
                player.start_shoot_animation(direction.x)
            elif event.key == pygame.K_q and player_level.unlock_lightning and player.mana >= 20:
                player.mana -= 20
                for ghost in ghosts[:]:
                    dist = pygame.Vector2(ghost.rect.center) - pygame.Vector2(player.rect.center)
                    if dist.length() < 150:
                        lightnings.append(LightningSpell(ghost.rect.centerx, ghost.rect.centery))
                        ghost.hp = 0 if hasattr(ghost, 'hp') else None
                        if ghost in ghosts:
                            ghosts.remove(ghost)
                            score += 10
                            if boss_pepe and boss_pepe.active:
                                boss_pepe.notify_ghost_killed()
            elif event.key == pygame.K_KP5:
                x = random.randint(0, bg_width)
                y = random.randint(0, bg_height)
                ghost_type = random.choice([Ghost, TankGhost, ShooterGhost])
                ghosts.append(ghost_type(x, y))
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

    keys = pygame.key.get_pressed()
    camera_offset = pygame.math.Vector2(
        player.rect.centerx - screen.get_width() // 2,
        player.rect.centery - screen.get_height() // 2
    )
    camera_offset.x = max(0, min(camera_offset.x, bg_width - screen.get_width()))
    camera_offset.y = max(0, min(camera_offset.y, bg_height - screen.get_height()))

    player.update(keys, dt, walls)
    if player.shield_cooldown > 0:
        player.shield_cooldown -= dt

    if boss_pepe:
        boss_pepe.update(dt, player, ghosts)
    if boss_strong:
        boss_strong.update(dt, player, ghosts)

    if potion and potion.active:
        potion.update(dt)
    if mana_mushroom and mana_mushroom.active:
        mana_mushroom.update(dt)

    for ghost in ghosts:
        ghost.update(dt, player)

    if player.hp <= 0:
        break

    for fireball in fireballs[:]:
        fireball.update(dt)
        if fireball.timer > fireball.lifetime:
            fireballs.remove(fireball)

    for fireball in fireballs[:]:
        if boss_strong and boss_strong.active and fireball.rect.colliderect(boss_strong.rect):
            boss_strong.hp -= 5
            if boss_strong.hp <= 0:
                boss_strong.active = False
            if fireball in fireballs:
                fireballs.remove(fireball)
            continue
        for ghost in ghosts[:]:
            if fireball.rect.colliderect(ghost.rect):
                if hasattr(ghost, 'hp'):
                    ghost.hp -= 1
                    if ghost.hp <= 0:
                        ghosts.remove(ghost)
                        score += 10
                        if boss_pepe and boss_pepe.active:
                            boss_pepe.notify_ghost_killed()
                else:
                    ghosts.remove(ghost)
                    score += 10
                    if boss_pepe and boss_pepe.active:
                        boss_pepe.notify_ghost_killed()
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

    if potion and potion.active and player.rect.colliderect(potion.rect):
        inventory.add_item("hilka")
        potion.active = False

    if mana_mushroom and mana_mushroom.active and player.rect.colliderect(mana_mushroom.rect):
        inventory.add_item("mana")
        mana_mushroom.active = False

    ghost_spawn_timer += dt
    if ghost_spawn_timer >= ghost_spawn_interval:
        ghost_spawn_timer = 0
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, bg_width)
            y = 0
        elif side == 'bottom':
            x = random.randint(0, bg_width)
            y = bg_height
        elif side == 'left':
            x = 0
            y = random.randint(0, bg_height)
        else:
            x = bg_width
            y = random.randint(0, bg_height)
        ghost_type = random.choice([Ghost, TankGhost, ShooterGhost])
        ghosts.append(ghost_type(x, y))

    for lightning in lightnings[:]:
        lightning.update(dt)
        if lightning.finished:
            lightnings.remove(lightning)

    screen.blit(background, (-camera_offset.x, -camera_offset.y))
    player.draw(screen, camera_offset)
    if boss_pepe:
        boss_pepe.draw(screen, camera_offset)
    if boss_strong:
        boss_strong.draw(screen, camera_offset)
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

    if level_text_timer > 0:
        level_text_timer -= dt
        level_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 12)
        level_surf = level_font.render(level_text, True, (255, 255, 0))
        level_rect = level_surf.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(level_surf, level_rect)

    pygame.display.flip()

# Game Over экран
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                exec(open("main.py").read())
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()

    screen.fill((0, 0, 0))
    img_rect = game_over_image.get_rect(center=screen.get_rect().center)
    screen.blit(game_over_image, img_rect)
    pygame.display.flip()
