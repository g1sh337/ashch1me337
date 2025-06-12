# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ['main.py'],  # Главный файл игры
    pathex=[],
    binaries=[],
    datas=[
        # Добавляем папку assets целиком
        ('assets', 'assets'),
        # Добавляем JSON файлы
        ('walls.json', '.'),
        ('game_settings.json', '.'),
    ],
    hiddenimports=[
        # Основные модули
        'pygame',
        'json',
        'random',
        'sys',
        'os',
        'subprocess',
        # Модули игры
        'player',
        'ghost',
        'fireball',
        'potion',
        'tank_ghost',
        'shooter_ghost',
        'lightning_spell',
        'interface',
        'manamushroom',
        'inventory',
        'shield_spell',
        'boss_pepe',
        'boss_strong',
        'config',
        'damage_number',
        'world_manager',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Исключаем ненужные модули для уменьшения размера
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy.random._examples',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Создание архива Python файлов
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Создание исполняемого файла
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MageVsGhosts',  # Имя EXE файла
    debug=False,  # Отключаем отладку для финальной версии
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Сжатие UPX для уменьшения размера
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Убираем консольное окно
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico'  # Раскомментируйте если есть иконка
)