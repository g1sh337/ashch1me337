# -*- mode: python ; coding: utf-8 -*-
import os

# Собираем все файлы из папки assets
def collect_assets():
    assets_data = []
    assets_dir = 'assets'
    if os.path.exists(assets_dir):
        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                src = os.path.join(root, file)
                dst = root
                assets_data.append((src, dst))
    return assets_data

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=collect_assets() + [
        ('walls.json', '.'),
        ('game_settings.json', '.'),
    ],
    hiddenimports=[
        'pygame',
        'json',
        'random',
        'sys',
        'os',
        'subprocess',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy.random._examples',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MageVsGhosts',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Без консоли для финальной версии
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)