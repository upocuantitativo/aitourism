@echo off
:: Quick Fix Script for Windows - Solución inmediata al problema de dependencias
echo.
echo 🔧 SMART TOURISM SYSTEM - SOLUCIÓN RÁPIDA DE DEPENDENCIAS
echo ================================================================
echo.

:: Verificar si estamos en el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Entorno virtual no encontrado
    echo 🔧 Ejecutar primero: python -m venv venv
    pause
    exit /b 1
)

:: Activar entorno virtual
echo 🔌 Activando entorno virtual...
call venv\Scripts\activate.bat

:: Actualizar pip
echo 📈 Actualizando pip...
python -m pip install --upgrade pip

:: Instalar dependencias críticas una por una
echo.
echo 📦 Instalando dependencias críticas...

echo   📦 Instalando requests...
pip install "requests>=2.25.0"
if errorlevel 1 (
    echo   ❌ Error con requests
) else (
    echo   ✅ requests instalado
)

echo   📦 Instalando pandas...
pip install "pandas>=1.3.0"
if errorlevel 1 (
    echo   ❌ Error con pandas
) else (
    echo   ✅ pandas instalado
)

echo   📦 Instalando numpy...
pip install "numpy>=1.20.0"
if errorlevel 1 (
    echo   ❌ Error con numpy
) else (
    echo   ✅ numpy instalado
)

echo   📦 Instalando scipy...
pip install "scipy>=1.7.0"
if errorlevel 1 (
    echo   ❌ Error con scipy
) else (
    echo   ✅ scipy instalado
)

echo   📦 Instalando scikit-learn...
pip install "scikit-learn>=1.0.0"
if errorlevel 1 (
    echo   ❌ Error con scikit-learn
) else (
    echo   ✅ scikit-learn instalado
)

echo   📦 Instalando plotly...
pip install "plotly>=5.0.0"
if errorlevel 1 (
    echo   ❌ Error con plotly
) else (
    echo   ✅ plotly instalado
)

echo   📦 Instalando dash...
pip install "dash>=2.0.0"
if errorlevel 1 (
    echo   ❌ Error con dash
) else (
    echo   ✅ dash instalado
)

echo   📦 Instalando schedule...
pip install "schedule>=1.1.0"
if errorlevel 1 (
    echo   ❌ Error con schedule
) else (
    echo   ✅ schedule instalado
)

echo   📦 Instalando psutil...
pip install "psutil>=5.8.0"
if errorlevel 1 (
    echo   ❌ Error con psutil
) else (
    echo   ✅ psutil instalado
)

echo   📦 Instalando python-dateutil...
pip install "python-dateutil>=2.8.0"
if errorlevel 1 (
    echo   ❌ Error con python-dateutil
) else (
    echo   ✅ python-dateutil instalado
)

echo   📦 Instalando sqlalchemy...
pip install "sqlalchemy>=1.4.0"
if errorlevel 1 (
    echo   ❌ Error con sqlalchemy
) else (
    echo   ✅ sqlalchemy instalado
)

:: Probar importaciones críticas
echo.
echo 🧪 Probando importaciones críticas...

python -c "import requests; print('✅ requests')" 2>nul || echo ❌ requests
python -c "import pandas; print('✅ pandas')" 2>nul || echo ❌ pandas  
python -c "import numpy; print('✅ numpy')" 2>nul || echo ❌ numpy
python -c "import scipy; print('✅ scipy')" 2>nul || echo ❌ scipy
python -c "import sklearn; print('✅ scikit-learn')" 2>nul || echo ❌ scikit-learn
python -c "import plotly; print('✅ plotly')" 2>nul || echo ❌ plotly
python -c "import dash; print('✅ dash')" 2>nul || echo ❌ dash

:: Intentar ejecutar diagnóstico rápido
echo.
echo 🔍 Ejecutando diagnóstico rápido...
python quick_install.py

:: Crear directorios básicos si no existen
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "exports" mkdir exports
if not exist "cache" mkdir cache

:: Crear base de datos básica usando Python
echo.
echo 🗄️ Configurando base de datos...
python -c "import sqlite3; import os; os.makedirs('data', exist_ok=True); conn = sqlite3.connect('data/tourism_data.db'); conn.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER)'); conn.close(); print('✅ Base de datos básica creada')" 2>nul || echo ⚠️ No se pudo crear base de datos

echo.
echo ================================================================
echo 🎉 INSTALACIÓN RÁPIDA COMPLETADA
echo ================================================================
echo.
echo 🚀 Ahora puedes intentar ejecutar:
echo    python main.py --mode full
echo.
echo 📊 El dashboard estará disponible en: http://localhost:8050
echo.
echo 🔧 Si aún hay problemas, ejecutar:
echo    python diagnostics.py --mode full
echo.

set /p choice="¿Intentar ejecutar el sistema ahora? (s/n): "
if /i "%choice%"=="s" (
    echo.
    echo 🚀 Iniciando sistema...
    python main.py --mode full
) else (
    echo.
    echo ✅ Listo para usar. Ejecutar cuando esté preparado:
    echo    python main.py --mode full
)

pause
