#!/bin/bash

# Smart Tourism Management System - Linux/Mac Installation Script
# Script de instalación automática para Linux y macOS

set -e  # Salir en caso de error

echo ""
echo "===================================================================="
echo " SMART TOURISM MANAGEMENT SYSTEM - INSTALACION AUTOMATICA UNIX"
echo "===================================================================="
echo ""

# Función para mostrar mensajes de estado
log_info() {
    echo "✅ $1"
}

log_warning() {
    echo "⚠️  $1"
}

log_error() {
    echo "❌ $1"
}

log_step() {
    echo ""
    echo "📋 $1..."
}

# Verificar Python
log_step "Verificando Python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    log_info "Python3 encontrado: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    log_info "Python encontrado: $(python --version)"
else
    log_error "Python no está instalado"
    echo ""
    echo "📥 Instalar Python:"
    echo "   - Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "   - CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "   - macOS: brew install python3"
    echo "   - O descargar desde: https://www.python.org/downloads/"
    exit 1
fi

# Verificar versión de Python
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    log_info "Versión de Python OK: $PYTHON_VERSION"
else
    log_error "Python $PYTHON_VERSION < $REQUIRED_VERSION (mínimo requerido)"
    exit 1
fi

# Verificar pip
log_step "Verificando pip"
if $PYTHON_CMD -m pip --version &> /dev/null; then
    log_info "pip disponible"
else
    log_error "pip no está disponible"
    echo "📥 Instalar pip: sudo apt install python3-pip (Ubuntu) o equivalente"
    exit 1
fi

# Crear entorno virtual
log_step "Creando entorno virtual"
if [ -d "venv" ]; then
    log_warning "Entorno virtual ya existe, eliminando..."
    rm -rf venv
fi

$PYTHON_CMD -m venv venv
log_info "Entorno virtual creado"

# Activar entorno virtual
log_step "Activando entorno virtual"
source venv/bin/activate
log_info "Entorno virtual activado"

# Actualizar pip
log_step "Actualizando pip"
pip install --upgrade pip

# Instalar dependencias
log_step "Instalando dependencias del sistema"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    log_info "Dependencias instaladas correctamente"
else
    log_error "Archivo requirements.txt no encontrado"
    exit 1
fi

# Ejecutar configuración completa
log_step "Ejecutando configuración del sistema"
$PYTHON_CMD setup.py --step all
if [ $? -eq 0 ]; then
    log_info "Configuración completada exitosamente"
else
    log_warning "Configuración completada con advertencias"
fi

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    log_step "Creando archivo de configuración .env"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_info "Archivo .env creado desde template"
        log_warning "IMPORTANTE: Editar .env para configurar API keys"
    else
        log_warning ".env.example no encontrado"
    fi
fi

# Dar permisos de ejecución a scripts
log_step "Configurando permisos de archivos"
chmod +x *.sh 2>/dev/null || true
chmod +x *.py 2>/dev/null || true
log_info "Permisos configurados"

# Ejecutar diagnóstico
log_step "Ejecutando diagnóstico del sistema"
$PYTHON_CMD diagnostics.py --mode quick

# Generar datos de muestra
log_step "Generando datos de muestra"
$PYTHON_CMD -c "
import sys, os
sys.path.append('.')
try:
    from data_collectors.data_collectors import DataCollectionOrchestrator
    orchestrator = DataCollectionOrchestrator()
    data = orchestrator.collect_all_data(regions=['Andalucía', 'Cataluña'])
    print('✅ Datos de muestra generados')
except Exception as e:
    print(f'⚠️ Error generando datos: {e}')
" 2>/dev/null || log_warning "Error generando datos de muestra"

# Instrucciones finales
echo ""
echo "===================================================================="
echo " 🎉 INSTALACION COMPLETADA"
echo "===================================================================="
echo ""
echo "📋 PROXIMOS PASOS:"
echo ""
echo "1. 🔑 Configurar API keys en archivo .env (opcional):"
echo "   nano .env"
echo "   - ANTHROPIC_API_KEY=tu_clave_claude"
echo "   - TRIPADVISOR_API_KEY=tu_clave_tripadvisor"
echo ""
echo "2. 🚀 Iniciar el sistema:"
echo "   - Sistema completo: ./start_system.sh"
echo "   - Línea de comandos: python main.py --mode full"
echo ""
echo "3. 📊 Acceder al dashboard:"
echo "   - URL: http://localhost:8050"
echo ""
echo "4. 🔧 Comandos útiles:"
echo "   - Diagnóstico: python diagnostics.py"
echo "   - Tests: python tests.py  "
echo "   - Scheduler: python scheduler.py"
echo ""
echo "5. 🏃 Activar entorno virtual (sesiones futuras):"
echo "   source venv/bin/activate"
echo ""
echo "📖 Documentación completa en README.md"
echo ""

# Preguntar si instalar como servicio del sistema
read -p "¿Instalar como servicio del sistema? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo ""
    echo "🔧 Configuración de servicio del sistema:"
    $PYTHON_CMD scheduler.py --mode install-service
fi

# Preguntar si iniciar el sistema
read -p "¿Iniciar el sistema ahora? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo ""
    echo "🚀 Iniciando Smart Tourism System..."
    echo "📊 Dashboard disponible en: http://localhost:8050"
    echo "⏹️  Presionar Ctrl+C para detener"
    echo ""
    $PYTHON_CMD main.py --mode full
else
    echo ""
    echo "✅ Instalación completada."
    echo "🚀 Ejecutar ./start_system.sh cuando esté listo."
fi

echo ""
echo "🎯 Instalación completada exitosamente!"
