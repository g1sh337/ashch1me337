import pygame

class Interface:
    def __init__(self):
        # Увеличим размер интерфейса в 2 раза
        self.interface_img = pygame.image.load("assets/Interface.png").convert_alpha()
        self.interface_img = pygame.transform.scale(self.interface_img, (self.interface_img.get_width()*2, self.interface_img.get_height()*2))

        # Загрузка кадров полосы здоровья и увеличение
        health_sheet = pygame.image.load("assets/healthsheet.png").convert_alpha()
        health_sheet = pygame.transform.scale(health_sheet, (health_sheet.get_width()*2, health_sheet.get_height()*2))
        self.health_frames = [
            health_sheet.subsurface(pygame.Rect(i * 226, 0, 226, 120)) for i in range(9)
        ]

        # Загрузка кадров полосы маны и увеличение
        mana_sheet = pygame.image.load("assets/manasheet.png").convert_alpha()
        mana_sheet = pygame.transform.scale(mana_sheet, (mana_sheet.get_width()*2, mana_sheet.get_height()*2))
        self.mana_frames = [
            mana_sheet.subsurface(pygame.Rect(i * 226, 0, 226, 120)) for i in range(9)
        ]

    def draw(self, surface, player):
        # Отрисовка интерфейса
        surface.blit(self.interface_img, (10, 10))

        # Индексы здоровья и маны
        hp_index = round((player.hp / player.max_hp) * 8)
        mana_index = round((player.mana / player.max_mana) * 8)
        hp_index = max(0, min(hp_index, 8))  # кадров 9 (0-8), теперь 8/8 отображается корректно
        mana_index = max(0, min(mana_index, 8))  # кадров 9 (0-8), теперь 8/8 отображается корректно

        # Отрисовка полос
        surface.blit(self.health_frames[hp_index], (10, 10))
        surface.blit(self.mana_frames[mana_index], (10, 10))
