@echo off
:: SOLUCIÓN INMEDIATA - Instalar solo las dependencias faltantes
echo.
echo ⚡ INSTALACIÓN INMEDIATA - DEPENDENCIAS FALTANTES
echo ===============================================
echo.

:: Activar entorno virtual
call venv\Scripts\activate.bat

:: Instalar solo lo que falta
echo 📦 Instalando scipy...
pip install "scipy>=1.7.0"

echo 📦 Instalando scikit-learn...
pip install "scikit-learn>=1.0.0"

:: Verificar instalación
echo.
echo 🧪 Verificando instalación...
python -c "import scipy; print('✅ scipy OK')"
python -c "import sklearn; print('✅ scikit-learn OK')"

:: Probar sistema
echo.
echo 🚀 Probando sistema...
python -c "
try:
    from models.pls_sem_analyzer import PLSSEMAnalyzer
    from dashboard.dashboard import TourismDashboard
    print('✅ Todos los módulos se importan correctamente')
    print('🎉 SISTEMA LISTO PARA USAR')
except Exception as e:
    print(f'❌ Error: {e}')
"

echo.
echo 📊 Ahora ejecutar: python main.py --mode full
echo 🌐 Dashboard: http://localhost:8050
pause
