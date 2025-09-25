#!/usr/bin/env python3
"""
Quick Fix Installation Script
Script para solucionar problemas de instalación inmediatamente
"""

import subprocess
import sys
import os

def install_package(package):
    """Instala un paquete individual"""
    try:
        print(f"📦 Instalando {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {package}: {e}")
        return False

def main():
    """Instalación rápida de dependencias esenciales"""
    print("🚀 SMART TOURISM SYSTEM - INSTALACIÓN RÁPIDA")
    print("=" * 60)
    
    # Verificar que estamos en un entorno virtual
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️ No se detectó entorno virtual activo")
        response = input("¿Continuar instalando en el sistema global? (s/n): ")
        if response.lower() != 's':
            print("❌ Instalación cancelada")
            return 1
    
    # Actualizar pip primero
    print("📈 Actualizando pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("✅ pip actualizado")
    except:
        print("⚠️ No se pudo actualizar pip, continuando...")
    
    # Dependencias esenciales en orden de prioridad
    essential_packages = [
        "requests>=2.25.0",
        "pandas>=1.3.0", 
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "plotly>=5.0.0",
        "dash>=2.0.0",
        "schedule>=1.1.0",
        "psutil>=5.8.0",
        "python-dateutil>=2.8.0",
        "sqlalchemy>=1.4.0"
    ]
    
    print(f"\n📋 Instalando {len(essential_packages)} dependencias esenciales...")
    
    success_count = 0
    failed_packages = []
    
    for package in essential_packages:
        if install_package(package):
            success_count += 1
        else:
            failed_packages.append(package)
    
    print(f"\n📊 RESUMEN DE INSTALACIÓN:")
    print(f"✅ Exitosas: {success_count}/{len(essential_packages)}")
    
    if failed_packages:
        print(f"❌ Fallidas: {len(failed_packages)}")
        for pkg in failed_packages:
            print(f"   - {pkg}")
    
    # Probar importaciones
    print(f"\n🧪 Probando importaciones...")
    
    test_imports = [
        ("requests", "requests"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("scikit-learn", "sklearn"),
        ("plotly", "plotly.graph_objects"),
        ("dash", "dash"),
        ("schedule", "schedule"),
        ("psutil", "psutil")
    ]
    
    import_success = 0
    for name, module in test_imports:
        try:
            __import__(module)
            print(f"✅ {name}")
            import_success += 1
        except ImportError:
            print(f"❌ {name}")
    
    print(f"\n📈 Importaciones exitosas: {import_success}/{len(test_imports)}")
    
    if import_success >= 8:  # Al menos 8 de 9 dependencias principales
        print(f"\n🎉 INSTALACIÓN EXITOSA!")
        print(f"🚀 Ahora puedes ejecutar: python main.py --mode full")
        return 0
    else:
        print(f"\n⚠️ INSTALACIÓN PARCIAL")
        print(f"🔧 Algunos módulos no están disponibles")
        print(f"💡 Intentar: pip install -r requirements-minimal.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
