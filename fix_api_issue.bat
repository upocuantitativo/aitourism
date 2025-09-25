@echo off
echo ============================================
echo  SOLUCION PROBLEMA API - Smart Tourism
echo ============================================
echo.

cd /d "C:\Users\Usuario\Documents\IAtourism"

echo [1/3] Deshabilitando requerimiento de API externa...
powershell -Command "(Get-Content .env) -replace 'ENABLE_AI_ANALYSIS=True', 'ENABLE_AI_ANALYSIS=False' | Set-Content .env.tmp"
move /y .env.tmp .env >nul

echo [2/3] Verificando sistema...
python diagnostics.py --mode quick

echo [3/3] Iniciando sistema sin API externa...
echo.
echo ============================================
echo  El sistema usara analisis LOCAL (sin APIs)
echo  Esto es totalmente funcional
echo ============================================
echo.
pause

python main.py --mode full