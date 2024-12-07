@echo off
python -m PyInstaller --onefile --windowed -w --add-data "icon.png;." --icon icon.png main.py --name Spla3StageDesktop-Windows
pause