import os
import glob

print("=== ПРОВЕРКА РЕСУРСОВ ===")
print()

# Проверяем папку assets
if os.path.exists('assets'):
    print("✓ Папка assets найдена")
    
    print("\nВсе файлы в папке assets:")
    for root, dirs, files in os.walk('assets'):
        for file in files:
            full_path = os.path.join(root, file)
            size = os.path.getsize(full_path)
            print(f"  {full_path} ({size} bytes)")
    
    print()
else:
    print("✗ Папка assets НЕ НАЙДЕНА!")


critical_files = [
    'assets/background.png',
    'assets/Interface.png', 
    'assets/healthsheet.png',
    'assets/manasheet.png',
    'assets/shiled_spell.png',  # С опечаткой
    'assets/shield_spell.png',  # Правильное название
    'assets/mag stay sprite.png',
    'assets/PressStart2P-Regular.ttf',
    'walls.json',
    'game_settings.json',
    'main.py',
    'safe_loader.py'
]

print("Проверка критически важных файлов:")
missing_files = []
for file_path in critical_files:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"  ✓ {file_path} ({size} bytes)")
    else:
        print(f"  ✗ {file_path} - НЕ НАЙДЕН")
        missing_files.append(file_path)

print()
if missing_files:
    print("ОТСУТСТВУЮЩИЕ ФАЙЛЫ:")
    for file in missing_files:
        print(f"  - {file}")
    print()
    print("Рекомендации:")
    if 'assets/shiled_spell.png' in missing_files and 'assets/shield_spell.png' in missing_files:
        print("  - Создайте файл shield_spell.png в папке assets")
    print("  - Убедитесь что все файлы на месте перед сборкой")
else:
    print("✓ Все критически важные файлы найдены!")

print()
print("=== КОНЕЦ ПРОВЕРКИ ===")