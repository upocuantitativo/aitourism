#!/usr/bin/env python3
"""
Smart Tourism Management System - Setup & Installation Script
Script de instalación y configuración del sistema
"""

import os
import sys
import subprocess
import sqlite3
import json
from pathlib import Path
import argparse

class SystemSetup:
    """Configurador del Smart Tourism Management System"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.data_path = self.project_root / "data"
        self.logs_path = self.project_root / "logs"
        
    def create_virtual_environment(self):
        """Crea entorno virtual"""
        print("🔧 Creando entorno virtual...")
        
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], 
                          check=True, capture_output=True)
            print("✅ Entorno virtual creado correctamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creando entorno virtual: {e}")
            return False
    
    def install_dependencies(self):
        """Instala dependencias del proyecto"""
        print("📦 Instalando dependencias...")
        
        # Ruta al ejecutable de pip en el entorno virtual
        if os.name == 'nt':  # Windows
            pip_path = self.venv_path / "Scripts" / "pip.exe"
            python_path = self.venv_path / "Scripts" / "python.exe"
        else:  # Linux/Mac
            pip_path = self.venv_path / "bin" / "pip"
            python_path = self.venv_path / "bin" / "python"
        
        requirements_file = self.project_root / "requirements.txt"
        requirements_minimal = self.project_root / "requirements-minimal.txt"
        
        try:
            # Actualizar pip
            print("📈 Actualizando pip...")
            subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], 
                          check=True, capture_output=True)
            
            # Intentar instalar dependencias completas
            print("📦 Instalando dependencias completas...")
            try:
                subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], 
                              check=True, capture_output=True, timeout=300)
                print("✅ Dependencias completas instaladas")
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                print("⚠️ Fallo instalación completa, intentando dependencias mínimas...")
                
                # Fallback a dependencias mínimas
                if requirements_minimal.exists():
                    subprocess.run([str(pip_path), "install", "-r", str(requirements_minimal)], 
                                  check=True, capture_output=True, timeout=180)
                    print("✅ Dependencias mínimas instaladas")
                    return True
                else:
                    # Instalación manual de dependencias críticas
                    critical_deps = [
                        "requests>=2.25.0",
                        "pandas>=1.3.0", 
                        "numpy>=1.20.0",
                        "dash>=2.0.0",
                        "plotly>=5.0.0"
                    ]
                    
                    print("🔧 Instalando dependencias críticas manualmente...")
                    for dep in critical_deps:
                        try:
                            subprocess.run([str(pip_path), "install", dep], 
                                          check=True, capture_output=True, timeout=60)
                            print(f"  ✅ {dep}")
                        except:
                            print(f"  ❌ {dep}")
                    
                    print("✅ Instalación básica completada")
                    return True
            
        except Exception as e:
            print(f"❌ Error grave en instalación: {e}")
            print("💡 Intentar instalación manual:")
            print(f"   pip install requests pandas numpy dash plotly")
            return False
    
    def create_directory_structure(self):
        """Crea estructura de directorios"""
        print("📁 Creando estructura de directorios...")
        
        directories = [
            "data",
            "logs", 
            "exports",
            "backups",
            "config",
            "tests"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
            print(f"  📂 {directory}/")
        
        print("✅ Estructura de directorios creada")
    
    def setup_database(self):
        """Configura base de datos inicial"""
        print("🗄️  Configurando base de datos...")
        
        db_path = self.data_path / "tourism_data.db"
        
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                
                # Tabla de datos integrados
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS integrated_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    date TEXT NOT NULL,
                    room_occupancy_rate REAL,
                    tourism_employment INTEGER,
                    tourism_competitiveness_index REAL,
                    current_rank INTEGER,
                    average_rating REAL,
                    total_reviews INTEGER,
                    total_facilities INTEGER,
                    performance_economic_social_benefit REAL,
                    total_establishments INTEGER,
                    collection_timestamp TEXT,
                    source TEXT
                )
                """)
                
                # Tabla de datos INE
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS ine_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    date TEXT NOT NULL,
                    room_occupancy_rate REAL,
                    bed_occupancy_rate REAL,
                    average_stay REAL,
                    total_travelers INTEGER,
                    tourism_employment INTEGER,
                    employment_growth_rate REAL,
                    total_establishments INTEGER,
                    hotel_establishments INTEGER,
                    rural_establishments INTEGER,
                    apartment_establishments INTEGER,
                    source TEXT,
                    collection_timestamp TEXT
                )
                """)
                
                # Tabla de datos TripAdvisor
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS tripadvisor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    date TEXT NOT NULL,
                    average_rating REAL,
                    total_reviews INTEGER,
                    current_rank INTEGER,
                    review_growth_rate REAL,
                    total_facilities INTEGER,
                    restaurants INTEGER,
                    attractions INTEGER,
                    activities INTEGER,
                    source TEXT,
                    collection_timestamp TEXT
                )
                """)
                
                # Tabla de datos Exceltur
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS exceltur_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    date TEXT NOT NULL,
                    tourism_competitiveness_index REAL,
                    infrastructure_score REAL,
                    accessibility_score REAL,
                    sustainability_score REAL,
                    gdp_tourism_contribution REAL,
                    tourism_revenue_millions REAL,
                    performance_economic_social_benefit REAL,
                    source TEXT,
                    collection_timestamp TEXT
                )
                """)
                
                # Tabla de resultados de análisis IA
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    results TEXT,
                    confidence_score REAL,
                    recommendations TEXT
                )
                """)
                
                # Índices para mejorar rendimiento
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_integrated_region_date ON integrated_data(region, date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ine_region_date ON ine_data(region, date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ta_region_date ON tripadvisor_data(region, date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ex_region_date ON exceltur_data(region, date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_region_timestamp ON ai_analysis_results(region, timestamp)")
                
                conn.commit()
            
            print("✅ Base de datos configurada")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando base de datos: {e}")
            return False
    
    def create_config_files(self):
        """Crea archivos de configuración"""
        print("⚙️  Creando archivos de configuración...")
        
        # Archivo .env para variables de entorno
        env_content = """# Smart Tourism Management System - Environment Variables

# API Keys (configurar con valores reales)
ANTHROPIC_API_KEY=your_claude_api_key_here
TRIPADVISOR_API_KEY=your_tripadvisor_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (SQLite local por defecto)
DATABASE_URL=sqlite:///data/tourism_data.db

# Dashboard Configuration
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8050
DASHBOARD_DEBUG=False

# Logging Level
LOG_LEVEL=INFO

# System Configuration
ENABLE_AUTO_COLLECTION=True
ENABLE_AI_ANALYSIS=True
ENABLE_PLS_ANALYSIS=True
"""
        
        env_path = self.project_root / ".env"
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)
        
        # Archivo de configuración de logging
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
                "detailed": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "formatter": "standard"
                },
                "file": {
                    "level": "DEBUG",
                    "class": "logging.FileHandler",
                    "filename": "logs/atourism_system.log",
                    "formatter": "detailed"
                }
            },
            "loggers": {
                "": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                }
            }
        }
        
        logging_path = self.project_root / "config" / "logging.json"
        with open(logging_path, "w", encoding="utf-8") as f:
            json.dump(logging_config, f, indent=2)
        
        print("✅ Archivos de configuración creados")
    
    def create_startup_scripts(self):
        """Crea scripts de inicio"""
        print("🚀 Creando scripts de inicio...")
        
        # Script para Windows
        windows_script = """@echo off
echo Smart Tourism Management System - Iniciando...
echo.

REM Activar entorno virtual
call venv\\Scripts\\activate.bat

REM Ejecutar sistema
python main.py --mode full

pause
"""
        
        windows_path = self.project_root / "start_system.bat"
        with open(windows_path, "w", encoding="utf-8") as f:
            f.write(windows_script)
        
        # Script para Linux/Mac
        unix_script = """#!/bin/bash
echo "Smart Tourism Management System - Iniciando..."
echo

# Activar entorno virtual
source venv/bin/activate

# Ejecutar sistema
python main.py --mode full

read -p "Presiona Enter para salir..."
"""
        
        unix_path = self.project_root / "start_system.sh"
        with open(unix_path, "w", encoding="utf-8") as f:
            f.write(unix_script)
        
        # Hacer ejecutable en Unix
        try:
            os.chmod(unix_path, 0o755)
        except:
            pass
        
        # Script solo para dashboard
        dashboard_script = """@echo off
echo Smart Tourism Dashboard - Iniciando...
echo Dashboard disponible en: http://localhost:8050
echo.

call venv\\Scripts\\activate.bat
python main.py --mode dashboard

pause
"""
        
        dashboard_path = self.project_root / "start_dashboard.bat"
        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(dashboard_script)
        
        print("✅ Scripts de inicio creados")
    
    def create_sample_data(self):
        """Crea datos de muestra para pruebas"""
        print("📊 Creando datos de muestra...")
        
        try:
            # Importar el recolector de datos para generar datos sintéticos
            sys.path.append(str(self.project_root))
            from data_collectors.data_collectors import DataCollectionOrchestrator
            
            orchestrator = DataCollectionOrchestrator()
            
            # Generar datos para las primeras 3 regiones
            test_regions = ["Andalucía", "Cataluña", "Madrid"]
            integrated_data = orchestrator.collect_all_data(regions=test_regions)
            
            if integrated_data is not None and not integrated_data.empty:
                print(f"✅ Datos de muestra creados: {len(integrated_data)} registros")
            else:
                print("⚠️  No se pudieron crear datos de muestra")
            
        except Exception as e:
            print(f"⚠️  Error creando datos de muestra: {e}")
    
    def run_tests(self):
        """Ejecuta tests básicos del sistema"""
        print("🧪 Ejecutando tests básicos...")
        
        try:
            # Test de importación de módulos
            sys.path.append(str(self.project_root))
            
            import config
            print("  ✅ Configuración importada")
            
            from data_collectors.data_collectors import DataCollectionOrchestrator
            print("  ✅ Recolectores de datos importados")
            
            from models.pls_sem_analyzer import PLSSEMAnalyzer
            print("  ✅ Analizador PLS-SEM importado")
            
            from agents.ai_agents import AgentOrchestrator
            print("  ✅ Agentes IA importados")
            
            from dashboard.dashboard import TourismDashboard
            print("  ✅ Dashboard importado")
            
            # Test de base de datos
            db_path = self.data_path / "tourism_data.db"
            if db_path.exists():
                print("  ✅ Base de datos accesible")
            else:
                print("  ❌ Base de datos no encontrada")
            
            print("✅ Tests básicos completados")
            return True
            
        except Exception as e:
            print(f"❌ Error en tests: {e}")
            return False
    
    def setup_complete(self):
        """Configuración completa del sistema"""
        print("\n🎯 CONFIGURACIÓN COMPLETA DEL SMART TOURISM SYSTEM")
        print("=" * 60)
        
        steps = [
            ("Crear entorno virtual", self.create_virtual_environment),
            ("Instalar dependencias", self.install_dependencies),
            ("Crear estructura de directorios", self.create_directory_structure),
            ("Configurar base de datos", self.setup_database),
            ("Crear archivos de configuración", self.create_config_files),
            ("Crear scripts de inicio", self.create_startup_scripts),
            ("Crear datos de muestra", self.create_sample_data),
            ("Ejecutar tests básicos", self.run_tests)
        ]
        
        success_count = 0
        for step_name, step_function in steps:
            print(f"\n📋 {step_name}...")
            if step_function():
                success_count += 1
            else:
                print(f"⚠️  {step_name} falló, pero continuando...")
        
        print(f"\n🎉 CONFIGURACIÓN COMPLETADA: {success_count}/{len(steps)} pasos exitosos")
        
        if success_count >= len(steps) - 1:  # Permitir 1 fallo
            print("\n🚀 PRÓXIMOS PASOS:")
            print("1. Configurar las API keys en el archivo .env")
            print("2. Ejecutar: python main.py --mode init (para inicialización)")
            print("3. Ejecutar: python main.py --mode full (para sistema completo)")
            print("4. O usar los scripts: start_system.bat / start_system.sh")
            print(f"5. Dashboard disponible en: http://localhost:8050")
            
            print("\n📖 DOCUMENTACIÓN:")
            print("- Configuración: config/")
            print("- Logs: logs/")
            print("- Datos: data/")
            print("- Exportaciones: exports/")
            
        else:
            print("\n❌ Configuración incompleta. Revisar errores anteriores.")

def main():
    """Función principal del script de configuración"""
    parser = argparse.ArgumentParser(description='Smart Tourism System Setup')
    parser.add_argument('--step', choices=[
        'venv', 'deps', 'dirs', 'db', 'config', 'scripts', 'sample', 'test', 'all'
    ], default='all', help='Paso específico a ejecutar')
    
    args = parser.parse_args()
    
    setup = SystemSetup()
    
    if args.step == 'all':
        setup.setup_complete()
    elif args.step == 'venv':
        setup.create_virtual_environment()
    elif args.step == 'deps':
        setup.install_dependencies()
    elif args.step == 'dirs':
        setup.create_directory_structure()
    elif args.step == 'db':
        setup.setup_database()
    elif args.step == 'config':
        setup.create_config_files()
    elif args.step == 'scripts':
        setup.create_startup_scripts()
    elif args.step == 'sample':
        setup.create_sample_data()
    elif args.step == 'test':
        setup.run_tests()

if __name__ == "__main__":
    main()
