@echo off
echo Smart Tourism Dashboard - Iniciando...
echo Dashboard disponible en: http://localhost:8050
echo.

call venv\Scripts\activate.bat
python main.py --mode dashboard

pause
