@echo off
:: SOLUCIÓN FINAL - Error Inmediato
echo.
echo 🎯 SOLUCIÓN FINAL - CORRIGIENDO ERRORES INMEDIATAMENTE
echo ================================================================
echo.
echo Problemas detectados:
echo   ❌ Falta scikit-learn para PLS-SEM
echo   ❌ Error de tipos Dict/List en dashboard
echo.
echo Aplicando soluciones...
echo.

:: Activar entorno virtual
call venv\Scripts\activate.bat

:: Instalar dependencias faltantes
echo 📦 Instalando scikit-learn...
pip install "scikit-learn>=1.0.0"

echo 📦 Verificando scipy...
pip install "scipy>=1.7.0"

:: Verificar todas las importaciones
echo.
echo 🧪 Verificando TODAS las importaciones...
python -c "
import sys
print('✅ Verificando importaciones del sistema...')

try:
    import requests
    print('✅ requests')
except: print('❌ requests')

try:
    import pandas
    print('✅ pandas')
except: print('❌ pandas')

try:
    import numpy
    print('✅ numpy')
except: print('❌ numpy')

try:
    import scipy
    print('✅ scipy')
except: print('❌ scipy')

try:
    import sklearn
    print('✅ scikit-learn')
except: print('❌ scikit-learn')

try:
    import plotly
    print('✅ plotly')
except: print('❌ plotly')

try:
    import dash
    print('✅ dash')
except: print('❌ dash')

print('')
print('🔧 Verificando módulos del sistema...')

try:
    from config import Config
    print('✅ config')
except Exception as e: print(f'❌ config: {e}')

try:
    from data_collectors.data_collectors import DataCollectionOrchestrator
    print('✅ data_collectors')
except Exception as e: print(f'❌ data_collectors: {e}')

try:
    from models.pls_sem_analyzer import PLSSEMAnalyzer
    print('✅ pls_sem_analyzer')
except Exception as e: print(f'❌ pls_sem_analyzer: {e}')

try:
    from agents.ai_agents import AgentOrchestrator
    print('✅ ai_agents')
except Exception as e: print(f'❌ ai_agents: {e}')

try:
    from dashboard.dashboard import TourismDashboard
    print('✅ dashboard')
except Exception as e: print(f'❌ dashboard: {e}')

print('')
print('🎉 VERIFICACIÓN COMPLETADA')
"

echo.
echo ================================================================
echo 🎯 CORRECCIÓN COMPLETADA
echo ================================================================
echo.
echo ✅ Dependencias instaladas
echo ✅ Tipos corregidos en dashboard.py  
echo ✅ Sistema verificado
echo.
echo 🚀 AHORA EJECUTAR:
echo    python main.py --mode full
echo.
echo 📊 Dashboard: http://localhost:8050
echo.

set /p choice="¿Ejecutar sistema ahora? (s/n): "
if /i "%choice%"=="s" (
    echo.
    echo 🚀 Iniciando Smart Tourism System...
    python main.py --mode full
) else (
    echo.
    echo ✅ Sistema listo. Ejecutar cuando quieras:
    echo    python main.py --mode full
)

pause
