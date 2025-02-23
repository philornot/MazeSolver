import os
import sys
import shutil
from pathlib import Path
import PyInstaller.__main__


def get_abs_path(*paths):
    """Zwraca absolutną ścieżkę względem głównego katalogu projektu"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *paths)


# Usuń stare pliki build i dist jeśli istnieją
for dir_name in ['build', 'dist']:
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

# Konfiguracja dla PyInstaller
app_name = "MazeSolver"
main_script = get_abs_path("src", "main.py")

# Przygotuj datas z poprawnymi ścieżkami
datas = [
    (get_abs_path("README.md"), "."),
    (get_abs_path("src"), "src"),  # Kopiujemy cały katalog src
    (get_abs_path("LICENSE"), "."),
]

# Usuń nieistniejące pliki z datas
datas = [(src, dst) for src, dst in datas if os.path.exists(src)]

# Lista ukrytych importów
hidden_imports = [
    'logging.handlers',
    'numpy',
    'pygame',
    'colorama',
]

# Argumenty dla PyInstaller
pyinstaller_args = [
    main_script,
    '--name=%s' % app_name,
    '--onefile',
    '--windowed',
    '--clean',
    '--noconfirm',
    '--paths', get_abs_path('src'),  # Dodaj src do PYTHONPATH
]

# Dodaj hidden imports
for imp in hidden_imports:
    pyinstaller_args.extend(['--hidden-import', imp])

# Dodaj datas do argumentów
for src, dst in datas:
    pyinstaller_args.extend(['--add-data', f'{src};{dst}'])

# Dodaj ikonę jeśli istnieje
icon_path = get_abs_path("assets", "icon.ico")
if os.path.exists(icon_path):
    pyinstaller_args.extend(['--icon', icon_path])

print(f"Rozpoczynam budowanie aplikacji {app_name}...")
print("\nUżywane ścieżki:")
print(f"Main script: {main_script}")
print(f"Python path: {get_abs_path('src')}")
for src, dst in datas:
    print(f"Data: {src} -> {dst}")
print("\nDodatkowe importy:")
for imp in hidden_imports:
    print(f"- {imp}")

try:
    # Uruchom PyInstaller
    PyInstaller.__main__.run(pyinstaller_args)

    exe_path = Path('dist') / f'{app_name}.exe'
    if exe_path.exists():
        print(f"\nSukces! Aplikacja została spakowana do: {exe_path.absolute()}")
        print(f"Rozmiar pliku: {exe_path.stat().st_size / (1024 * 1024):.2f} MB")
    else:
        print("\nBłąd: Nie znaleziono pliku wykonywalnego!")
        sys.exit(1)

except Exception as e:
    print(f"\nWystąpił błąd podczas budowania: {e}")
    sys.exit(1)