@echo off
:: Smart Tourism Management System - Windows Installation Script
:: Script de instalación automática para Windows

echo.
echo ====================================================================
echo  SMART TOURISM MANAGEMENT SYSTEM - INSTALACION AUTOMATICA WINDOWS
echo ====================================================================
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en PATH
    echo.
    echo 📥 Descargar Python desde: https://www.python.org/downloads/
    echo ⚠️  Asegurar marcar "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado:
python --version

:: Verificar pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no está disponible
    echo 📥 Instalar pip o reinstalar Python
    pause
    exit /b 1
)

echo ✅ pip disponible

:: Crear entorno virtual
echo.
echo 📦 Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo ❌ Error creando entorno virtual
    pause
    exit /b 1
)

:: Activar entorno virtual
echo ✅ Entorno virtual creado
echo 🔌 Activando entorno virtual...
call venv\Scripts\activate.bat

:: Actualizar pip
echo 📈 Actualizando pip...
python -m pip install --upgrade pip

:: Instalar dependencias
echo 📦 Instalando dependencias del sistema...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    echo 🔍 Verificar archivo requirements.txt
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas correctamente

:: Ejecutar configuración completa
echo.
echo ⚙️ Ejecutando configuración del sistema...
python setup.py --step all
if errorlevel 1 (
    echo ⚠️ Configuración completada con advertencias
) else (
    echo ✅ Configuración completada exitosamente
)

:: Crear archivo .env si no existe
if not exist .env (
    echo.
    echo 📄 Creando archivo de configuración .env...
    copy .env.example .env >nul 2>&1
    echo ✅ Archivo .env creado desde template
    echo ⚠️ IMPORTANTE: Editar .env para configurar API keys
)

:: Ejecutar diagnóstico
echo.
echo 🔍 Ejecutando diagnóstico del sistema...
python diagnostics.py --mode quick

:: Generar datos de muestra
echo.
echo 📊 Generando datos de muestra...
python -c "
import sys, os
sys.path.append('.')
try:
    from data_collectors.data_collectors import DataCollectionOrchestrator
    orchestrator = DataCollectionOrchestrator()
    data = orchestrator.collect_all_data(regions=['Andalucía', 'Cataluña'])
    print('✅ Datos de muestra generados')
except Exception as e:
    print(f'⚠️ Error generando datos: {e}')
"

:: Instrucciones finales
echo.
echo ====================================================================
echo  🎉 INSTALACION COMPLETADA
echo ====================================================================
echo.
echo 📋 PROXIMOS PASOS:
echo.
echo 1. 🔑 Configurar API keys en archivo .env (opcional):
echo    - ANTHROPIC_API_KEY=tu_clave_claude
echo    - TRIPADVISOR_API_KEY=tu_clave_tripadvisor
echo.
echo 2. 🚀 Iniciar el sistema:
echo    - Sistema completo: start_system.bat
echo    - Solo dashboard: start_dashboard.bat  
echo    - Línea de comandos: python main.py --mode full
echo.
echo 3. 📊 Acceder al dashboard:
echo    - URL: http://localhost:8050
echo.
echo 4. 🔧 Comandos útiles:
echo    - Diagnóstico: python diagnostics.py
echo    - Tests: python tests.py
echo    - Scheduler: python scheduler.py
echo.
echo 📖 Documentación completa en README.md
echo.

:: Preguntar si iniciar el sistema
set /p choice="¿Iniciar el sistema ahora? (s/n): "
if /i "%choice%"=="s" (
    echo.
    echo 🚀 Iniciando Smart Tourism System...
    echo 📊 Dashboard disponible en: http://localhost:8050
    echo ⏹️  Presionar Ctrl+C para detener
    echo.
    python main.py --mode full
) else (
    echo.
    echo ✅ Instalación completada. 
    echo 🚀 Ejecutar start_system.bat cuando esté listo.
)

echo.
pause
