@echo off
echo ============================================
echo  SOLUCION COMPLETA - Smart Tourism System
echo ============================================
echo.

REM Cambiar al directorio del proyecto
cd /d "C:\Users\Usuario\Documents\Atourism"

echo [1/5] Verificando entorno virtual...
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

echo [2/5] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [3/5] Instalando todas las dependencias...
pip install --upgrade pip
pip install pandas numpy scipy scikit-learn
pip install dash plotly requests
pip install schedule psutil python-dateutil
pip install openpyxl sqlalchemy
pip install matplotlib seaborn networkx

echo [4/5] Creando directorios necesarios...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "exports" mkdir exports
if not exist "cache" mkdir cache
if not exist "backups" mkdir backups

echo [5/5] Ejecutando diagnostico...
python diagnostics.py --mode quick

echo.
echo ============================================
echo  INSTALACION COMPLETADA
echo ============================================
echo.
echo SIGUIENTES PASOS:
echo.
echo 1. Para importar data_final.xlsx:
echo    python import_excel_data.py data_final.xlsx
echo.
echo 2. Para ejecutar el sistema:
echo    python main.py --mode full
echo.
echo 3. Dashboard disponible en:
echo    http://localhost:8050
echo.
echo ============================================
pause
