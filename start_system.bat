@echo off
echo Smart Tourism Management System - Iniciando...
echo.

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar sistema
python main.py --mode full

pause
