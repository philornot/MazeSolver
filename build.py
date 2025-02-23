# -*- coding: utf-8 -*-
import os
import shutil
import sys
from pathlib import Path

import PyInstaller.__main__


def get_abs_path(*paths):
    """Returns absolute path relative to project root directory"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *paths)


print("Starting build process...")  # Unikamy polskich znaków w komunikatach

# Cleanup old build and dist directories
for dir_name in ['build', 'dist']:
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

# PyInstaller configuration
app_name = "MazeSolver"
main_script = get_abs_path("src", "main.py")

# Prepare datas with correct paths
datas = [
    (get_abs_path("README.md"), "."),
    (get_abs_path("src"), "src"),
    (get_abs_path("LICENSE"), "."),
]

# Remove non-existent files from datas
datas = [(src, dst) for src, dst in datas if os.path.exists(src)]

# Hidden imports list
hidden_imports = [
    'logging.handlers',
    'numpy',
    'pygame',
    'colorama',
]

# PyInstaller arguments
pyinstaller_args = [
    main_script,
    '--name=%s' % app_name,
    '--onefile',
    '--windowed',
    '--clean',
    '--noconfirm',
    '--paths', get_abs_path('src'),
]

# Add hidden imports
for imp in hidden_imports:
    pyinstaller_args.extend(['--hidden-import', imp])

# Add datas
for src, dst in datas:
    pyinstaller_args.extend(['--add-data', f'{src};{dst}'])

# Add icon if exists
icon_path = get_abs_path("assets", "icon.ico")
if os.path.exists(icon_path):
    pyinstaller_args.extend(['--icon', icon_path])

print("Build configuration:")
print(f"Main script: {main_script}")
print(f"Python path: {get_abs_path('src')}")
for src, dst in datas:
    print(f"Data: {src} -> {dst}")
print("Additional imports:")
for imp in hidden_imports:
    print(f"- {imp}")

try:
    # Run PyInstaller
    PyInstaller.__main__.run(pyinstaller_args)

    exe_path = Path('dist') / f'{app_name}.exe'
    if exe_path.exists():
        print(f"Success! Application packed to: {exe_path.absolute()}")
        print(f"File size: {exe_path.stat().st_size / (1024 * 1024):.2f} MB")
    else:
        print("Error: Executable file not found!")
        sys.exit(1)

except Exception as e:
    print(f"Build error: {e}")
    sys.exit(1)
