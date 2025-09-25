#!/usr/bin/env python3
"""
Smart Tourism System Diagnostics and Health Check
Script de diagnóstico y verificación de salud del sistema
"""

import os
import sys
import json
import sqlite3
import subprocess
import importlib
import platform
import psutil
from datetime import datetime, timedelta
from pathlib import Path
import requests
import logging

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar logging para diagnóstico
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SystemDiagnostics:
    """Diagnóstico completo del Smart Tourism Management System"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
        
    def log_issue(self, message: str, is_warning: bool = False):
        """Registra un problema o advertencia"""
        if is_warning:
            self.warnings.append(message)
            logger.warning(message)
        else:
            self.issues.append(message)
            logger.error(message)
    
    def log_success(self, message: str):
        """Registra un éxito"""
        self.success_count += 1
        logger.info(f"✅ {message}")
    
    def check_python_version(self):
        """Verifica versión de Python"""
        self.total_checks += 1
        
        version = sys.version_info
        min_version = (3, 8)
        
        if version >= min_version:
            self.log_success(f"Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.log_issue(f"Python {version.major}.{version.minor} < {min_version[0]}.{min_version[1]} (mínimo requerido)")
    
    def check_dependencies(self):
        """Verifica dependencias de Python"""
        self.total_checks += 1
        
        required_packages = [
            'pandas', 'numpy', 'scipy', 'scikit-learn', 'dash', 'plotly',
            'requests', 'sqlite3', 'schedule', 'psutil'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                if package == 'sqlite3':
                    import sqlite3
                else:
                    importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
        
        if not missing_packages:
            self.log_success(f"Todas las dependencias instaladas ({len(required_packages)} paquetes)")
        else:
            self.log_issue(f"Dependencias faltantes: {', '.join(missing_packages)}")
    
    def check_directory_structure(self):
        """Verifica estructura de directorios"""
        self.total_checks += 1
        
        required_dirs = [
            'data', 'logs', 'exports', 'cache', 'backups',
            'data_collectors', 'models', 'agents', 'dashboard'
        ]
        
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
                # Crear directorio si es de datos
                if dir_name in ['data', 'logs', 'exports', 'cache', 'backups']:
                    dir_path.mkdir(exist_ok=True)
                    self.log_success(f"Directorio {dir_name}/ creado")
        
        if not missing_dirs:
            self.log_success("Estructura de directorios completa")
        else:
            for missing in missing_dirs:
                self.log_issue(f"Directorio faltante: {missing}/")
    
    def check_configuration_files(self):
        """Verifica archivos de configuración"""
        self.total_checks += 1
        
        config_files = [
            'config.py',
            'main.py',
            'requirements.txt'
        ]
        
        missing_files = []
        
        for file_name in config_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if not missing_files:
            self.log_success("Archivos de configuración presentes")
        else:
            for missing in missing_files:
                self.log_issue(f"Archivo faltante: {missing}")
        
        # Verificar archivo .env
        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'
        
        if env_file.exists():
            self.log_success("Archivo .env encontrado")
        elif env_example.exists():
            self.log_issue("Archivo .env no encontrado. Copiar desde .env.example y configurar", is_warning=True)
        else:
            self.log_issue("Archivos .env y .env.example no encontrados")
    
    def check_database(self):
        """Verifica base de datos"""
        self.total_checks += 1
        
        db_path = self.project_root / 'data' / 'tourism_data.db'
        
        if not db_path.exists():
            self.log_issue("Base de datos no encontrada. Ejecutar: python setup.py --step db", is_warning=True)
            return
        
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                
                # Verificar tablas principales
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = [
                    'integrated_data', 'ine_data', 'tripadvisor_data', 
                    'exceltur_data', 'ai_analysis_results'
                ]
                
                missing_tables = set(required_tables) - set(tables)
                
                if not missing_tables:
                    # Verificar si hay datos
                    cursor.execute("SELECT COUNT(*) FROM integrated_data")
                    record_count = cursor.fetchone()[0]
                    
                    if record_count > 0:
                        self.log_success(f"Base de datos operativa ({record_count} registros)")
                    else:
                        self.log_issue("Base de datos vacía. Ejecutar recolección de datos", is_warning=True)
                else:
                    self.log_issue(f"Tablas faltantes en BD: {', '.join(missing_tables)}")
                    
        except Exception as e:
            self.log_issue(f"Error accediendo a base de datos: {e}")
    
    def check_system_resources(self):
        """Verifica recursos del sistema"""
        self.total_checks += 1
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memoria
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disco
            disk = psutil.disk_usage(str(self.project_root))
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            
            # Evaluación
            issues = []
            if cpu_percent > 80:
                issues.append(f"Alto uso de CPU: {cpu_percent:.1f}%")
            
            if memory_percent > 85:
                issues.append(f"Alto uso de memoria: {memory_percent:.1f}%")
            elif memory_available_gb < 1:
                issues.append(f"Poca memoria disponible: {memory_available_gb:.1f}GB")
            
            if disk_percent > 90:
                issues.append(f"Poco espacio en disco: {disk_percent:.1f}% usado")
            elif disk_free_gb < 2:
                issues.append(f"Poco espacio libre: {disk_free_gb:.1f}GB")
            
            if issues:
                for issue in issues:
                    self.log_issue(issue, is_warning=True)
            else:
                self.log_success(f"Recursos del sistema OK (CPU: {cpu_percent:.1f}%, RAM: {memory_percent:.1f}%, Disco: {disk_percent:.1f}%)")
                
        except Exception as e:
            self.log_issue(f"Error verificando recursos del sistema: {e}", is_warning=True)
    
    def check_network_connectivity(self):
        """Verifica conectividad de red"""
        self.total_checks += 1
        
        test_urls = [
            ('INE', 'https://servicios.ine.es'),
            ('Exceltur', 'https://www.exceltur.org'),
            ('Anthropic API', 'https://api.anthropic.com'),
            ('Google DNS', 'https://8.8.8.8')
        ]
        
        connectivity_issues = []
        
        for service, url in test_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code < 400:
                    logger.debug(f"✓ {service} accesible")
                else:
                    connectivity_issues.append(f"{service} ({response.status_code})")
            except requests.exceptions.RequestException:
                connectivity_issues.append(service)
        
        if not connectivity_issues:
            self.log_success("Conectividad de red OK")
        else:
            self.log_issue(f"Problemas de conectividad: {', '.join(connectivity_issues)}", is_warning=True)
    
    def check_api_keys(self):
        """Verifica configuración de API keys"""
        self.total_checks += 1
        
        env_file = self.project_root / '.env'
        
        if not env_file.exists():
            self.log_issue("Archivo .env no encontrado para verificar API keys", is_warning=True)
            return
        
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            api_keys = {
                'ANTHROPIC_API_KEY': 'Claude API',
                'TRIPADVISOR_API_KEY': 'TripAdvisor API',
                'OPENAI_API_KEY': 'OpenAI API'
            }
            
            configured_keys = []
            missing_keys = []
            
            for key, service in api_keys.items():
                if key in env_content and 'your_' not in env_content:
                    configured_keys.append(service)
                else:
                    missing_keys.append(service)
            
            if configured_keys:
                self.log_success(f"API keys configuradas: {', '.join(configured_keys)}")
            
            if missing_keys:
                self.log_issue(f"API keys no configuradas: {', '.join(missing_keys)} (sistema usará análisis local)", is_warning=True)
                
        except Exception as e:
            self.log_issue(f"Error verificando API keys: {e}", is_warning=True)
    
    def check_ports_availability(self):
        """Verifica disponibilidad de puertos"""
        self.total_checks += 1
        
        import socket
        
        default_port = 8050
        
        # Verificar puerto del dashboard
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = sock.connect_ex(('localhost', default_port))
            if result == 0:
                self.log_issue(f"Puerto {default_port} ya está en uso", is_warning=True)
            else:
                self.log_success(f"Puerto {default_port} disponible para dashboard")
        except Exception as e:
            self.log_issue(f"Error verificando puerto {default_port}: {e}", is_warning=True)
        finally:
            sock.close()
    
    def check_module_imports(self):
        """Verifica que los módulos del sistema se puedan importar"""
        self.total_checks += 1
        
        modules_to_test = [
            'config',
            'data_collectors.data_collectors',
            'models.pls_sem_analyzer',
            'agents.ai_agents',
            'dashboard.dashboard',
            'utils'
        ]
        
        import_errors = []
        
        for module in modules_to_test:
            try:
                importlib.import_module(module)
            except ImportError as e:
                import_errors.append(f"{module}: {str(e)}")
        
        if not import_errors:
            self.log_success("Todos los módulos del sistema importables")
        else:
            for error in import_errors:
                self.log_issue(f"Error importando {error}")
    
    def check_data_quality(self):
        """Verifica calidad de datos si existen"""
        self.total_checks += 1
        
        db_path = self.project_root / 'data' / 'tourism_data.db'
        
        if not db_path.exists():
            self.log_issue("No hay datos para verificar calidad", is_warning=True)
            return
        
        try:
            with sqlite3.connect(str(db_path)) as conn:
                # Verificar datos recientes (último mes)
                cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM integrated_data WHERE date >= ?", 
                    (cutoff_date,)
                )
                recent_records = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT region) FROM integrated_data")
                unique_regions = cursor.fetchone()[0]
                
                if recent_records > 0:
                    self.log_success(f"Datos recientes disponibles ({recent_records} registros, {unique_regions} regiones)")
                else:
                    self.log_issue("No hay datos recientes (último mes)", is_warning=True)
                    
        except Exception as e:
            self.log_issue(f"Error verificando calidad de datos: {e}", is_warning=True)
    
    def run_comprehensive_diagnostics(self):
        """Ejecuta diagnóstico completo del sistema"""
        print("🔍 SMART TOURISM SYSTEM - DIAGNÓSTICO COMPLETO")
        print("=" * 60)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Sistema: {platform.system()} {platform.release()}")
        print(f"Directorio: {self.project_root}")
        print("")
        
        # Ejecutar todas las verificaciones
        checks = [
            ("Versión de Python", self.check_python_version),
            ("Dependencias", self.check_dependencies),
            ("Estructura de directorios", self.check_directory_structure),
            ("Archivos de configuración", self.check_configuration_files),
            ("Base de datos", self.check_database),
            ("Recursos del sistema", self.check_system_resources),
            ("Conectividad de red", self.check_network_connectivity),
            ("API Keys", self.check_api_keys),
            ("Puertos disponibles", self.check_ports_availability),
            ("Módulos del sistema", self.check_module_imports),
            ("Calidad de datos", self.check_data_quality)
        ]
        
        for check_name, check_function in checks:
            print(f"\n📋 {check_name}:")
            try:
                check_function()
            except Exception as e:
                self.log_issue(f"Error en verificación '{check_name}': {e}")
        
        # Resumen final
        print(f"\n{'='*60}")
        print("📊 RESUMEN DEL DIAGNÓSTICO")
        print(f"{'='*60}")
        
        success_rate = (self.success_count / self.total_checks) * 100 if self.total_checks > 0 else 0
        
        print(f"✅ Verificaciones exitosas: {self.success_count}/{self.total_checks} ({success_rate:.1f}%)")
        print(f"❌ Problemas críticos: {len(self.issues)}")
        print(f"⚠️  Advertencias: {len(self.warnings)}")
        
        if self.issues:
            print(f"\n🚨 PROBLEMAS CRÍTICOS:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        
        if self.warnings:
            print(f"\n⚠️  ADVERTENCIAS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        
        if len(self.issues) == 0 and len(self.warnings) <= 2:
            print("  ✨ Sistema en excelente estado. Listo para ejecutar.")
            print("  🚀 Ejecutar: python main.py --mode full")
        elif len(self.issues) == 0:
            print("  ⚡ Sistema funcional con advertencias menores.")
            print("  🔧 Revisar advertencias para optimización.")
            print("  ▶️  Ejecutar: python main.py --mode full")
        elif len(self.issues) <= 2:
            print("  🛠️  Corregir problemas críticos antes de ejecutar.")
            if any("dependencias" in issue.lower() for issue in self.issues):
                print("  📦 Instalar dependencias: pip install -r requirements.txt")
            if any("base de datos" in issue.lower() for issue in self.issues):
                print("  🗄️  Configurar BD: python setup.py --step db")
        else:
            print("  🚨 Múltiples problemas detectados.")
            print("  🔄 Ejecutar configuración completa: python setup.py --step all")
        
        # Status code para scripts
        if len(self.issues) == 0:
            return 0  # Éxito
        elif len(self.issues) <= 2:
            return 1  # Advertencias
        else:
            return 2  # Problemas críticos

def quick_health_check():
    """Verificación rápida de salud del sistema"""
    print("⚡ Quick Health Check")
    print("-" * 30)
    
    diagnostics = SystemDiagnostics()
    
    # Solo verificaciones básicas
    diagnostics.check_python_version()
    diagnostics.check_dependencies()
    diagnostics.check_database()
    diagnostics.check_system_resources()
    
    success_rate = (diagnostics.success_count / diagnostics.total_checks) * 100
    
    if success_rate >= 75:
        print(f"✅ Sistema operativo ({success_rate:.0f}% OK)")
        return 0
    else:
        print(f"❌ Sistema necesita atención ({success_rate:.0f}% OK)")
        return 1

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Tourism System Diagnostics')
    parser.add_argument('--mode', choices=['full', 'quick', 'fix'], 
                       default='full', help='Tipo de diagnóstico')
    parser.add_argument('--json', action='store_true', 
                       help='Salida en formato JSON')
    
    args = parser.parse_args()
    
    if args.mode == 'quick':
        return quick_health_check()
    elif args.mode == 'fix':
        print("🔧 Auto-fix mode")
        print("Ejecutando configuración automática...")
        subprocess.run([sys.executable, 'setup.py', '--step', 'all'])
        return 0
    else:
        diagnostics = SystemDiagnostics()
        result = diagnostics.run_comprehensive_diagnostics()
        
        if args.json:
            output = {
                'timestamp': datetime.now().isoformat(),
                'success_count': diagnostics.success_count,
                'total_checks': diagnostics.total_checks,
                'success_rate': (diagnostics.success_count / diagnostics.total_checks) * 100,
                'issues': diagnostics.issues,
                'warnings': diagnostics.warnings,
                'status': 'healthy' if result == 0 else 'warning' if result == 1 else 'critical'
            }
            print(json.dumps(output, indent=2))
        
        return result

if __name__ == "__main__":
    sys.exit(main())
