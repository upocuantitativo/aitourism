"""
Smart Tourism Management System - Main Application
Sistema principal que integra todos los componentes del sistema de gestión turística inteligente
"""

import os
import sys
import logging
import argparse
import threading
import time
from datetime import datetime
import signal
import atexit

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from data_collectors.data_collectors import DataCollectionOrchestrator
from models.pls_sem_analyzer import PLSSEMAnalyzer
from agents.ai_agents import AgentOrchestrator
from dashboard.dashboard import TourismDashboard

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/atourism_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SmartTourismSystem:
    """Sistema principal de gestión inteligente del turismo"""
    
    def __init__(self):
        self.data_collector = DataCollectionOrchestrator()
        self.pls_analyzer = PLSSEMAnalyzer()
        self.ai_orchestrator = AgentOrchestrator()
        self.dashboard = TourismDashboard()
        
        self.is_running = False
        self.threads = []
        
        # Configurar handlers para cierre limpio
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self.cleanup)
        
        logger.info("Smart Tourism System inicializado")
    
    def initialize_system(self):
        """Inicializa el sistema completo"""
        logger.info("Inicializando Smart Tourism Management System...")
        
        # Crear directorios necesarios
        self._create_directories()
        
        # Verificar configuración
        self._verify_configuration()
        
        # Ejecutar recolección inicial de datos
        logger.info("Ejecutando recolección inicial de datos...")
        self._initial_data_collection()
        
        # Ejecutar análisis PLS-SEM inicial
        logger.info("Ejecutando análisis PLS-SEM inicial...")
        self._initial_pls_analysis()
        
        logger.info("Sistema inicializado correctamente")
    
    def _create_directories(self):
        """Crea directorios necesarios"""
        directories = ['data', 'logs', 'exports', 'backups']
        
        for directory in directories:
            dir_path = os.path.join(os.path.dirname(__file__), directory)
            os.makedirs(dir_path, exist_ok=True)
            logger.debug(f"Directorio creado/verificado: {dir_path}")
    
    def _verify_configuration(self):
        """Verifica la configuración del sistema"""
        logger.info("Verificando configuración del sistema...")
        
        # Verificar APIs keys (opcional)
        if not Config.ANTHROPIC_API_KEY or Config.ANTHROPIC_API_KEY == 'your_claude_api_key_here':
            logger.warning("API key de Claude no configurada. Usar análisis local.")
        
        # Verificar regiones configuradas
        if not Config.REGIONS:
            raise ValueError("No hay regiones configuradas en Config.REGIONS")
        
        logger.info(f"Configuración verificada. Regiones: {len(Config.REGIONS)}")
    
    def _initial_data_collection(self):
        """Ejecuta recolección inicial de datos"""
        try:
            # Recopilar datos para primeras 3 regiones como prueba
            test_regions = Config.REGIONS[:3]
            
            logger.info(f"Recopilando datos iniciales para: {test_regions}")
            integrated_data = self.data_collector.collect_all_data(regions=test_regions)
            
            if integrated_data is not None and not integrated_data.empty:
                logger.info(f"Datos iniciales recopilados: {len(integrated_data)} registros")
            else:
                logger.warning("No se pudieron recopilar datos iniciales")
                
        except Exception as e:
            logger.error(f"Error en recolección inicial: {str(e)}")
    
    def _initial_pls_analysis(self):
        """Ejecuta análisis PLS-SEM inicial"""
        try:
            # Cargar datos y ejecutar análisis
            data = self.pls_analyzer.load_data()
            
            if not data.empty:
                latent_data = self.pls_analyzer.prepare_data(data)
                composite_scores = self.pls_analyzer.calculate_composite_scores(latent_data)
                results = self.pls_analyzer.run_pls_analysis(composite_scores)
                reliability = self.pls_analyzer.calculate_reliability_validity(latent_data)
                
                # Guardar resultados
                self.pls_analyzer.save_results()
                
                logger.info("Análisis PLS-SEM inicial completado")
                logger.info(f"R² modelo completo: {results.get('Complete_Model', {}).get('r_squared', 'N/A')}")
            else:
                logger.warning("No hay datos suficientes para análisis PLS-SEM inicial")
                
        except Exception as e:
            logger.error(f"Error en análisis PLS-SEM inicial: {str(e)}")
    
    def start_automated_services(self):
        """Inicia los servicios automatizados"""
        if self.is_running:
            logger.warning("Los servicios ya están ejecutándose")
            return
        
        self.is_running = True
        logger.info("Iniciando servicios automatizados...")
        
        # Hilo para recolección automática de datos
        data_thread = threading.Thread(
            target=self._automated_data_collection,
            name="DataCollectionThread",
            daemon=True
        )
        
        # Hilo para análisis automático con IA
        ai_thread = threading.Thread(
            target=self._automated_ai_analysis,
            name="AIAnalysisThread", 
            daemon=True
        )
        
        # Hilo para análisis PLS-SEM periódico
        pls_thread = threading.Thread(
            target=self._automated_pls_analysis,
            name="PLSAnalysisThread",
            daemon=True
        )
        
        # Iniciar hilos
        data_thread.start()
        ai_thread.start()
        pls_thread.start()
        
        self.threads = [data_thread, ai_thread, pls_thread]
        
        logger.info("Servicios automatizados iniciados")
    
    def _automated_data_collection(self):
        """Recolección automática de datos"""
        while self.is_running:
            try:
                logger.info("Ejecutando recolección automática de datos...")
                
                # Recopilar datos para todas las regiones
                integrated_data = self.data_collector.collect_all_data(regions=Config.REGIONS)
                
                if integrated_data is not None and not integrated_data.empty:
                    logger.info(f"Datos recopilados automáticamente: {len(integrated_data)} registros")
                else:
                    logger.warning("Recolección automática no produjo datos")
                
                # Esperar intervalo configurado
                time.sleep(Config.AGENTS_CONFIG['data_collector_frequency'])
                
            except Exception as e:
                logger.error(f"Error en recolección automática: {str(e)}")
                time.sleep(300)  # Esperar 5 minutos en caso de error
    
    def _automated_ai_analysis(self):
        """Análisis automático con IA"""
        while self.is_running:
            try:
                logger.info("Ejecutando análisis automático de IA...")
                
                # Iniciar análisis de IA para regiones principales
                self.ai_orchestrator.start_automated_analysis(regions=Config.REGIONS[:5])
                
                # Esperar intervalo configurado
                time.sleep(Config.AGENTS_CONFIG['analysis_frequency'])
                
            except Exception as e:
                logger.error(f"Error en análisis automático de IA: {str(e)}")
                time.sleep(600)  # Esperar 10 minutos en caso de error
    
    def _automated_pls_analysis(self):
        """Análisis PLS-SEM automático"""
        while self.is_running:
            try:
                logger.info("Ejecutando análisis PLS-SEM automático...")
                
                # Ejecutar análisis completo
                data = self.pls_analyzer.load_data()
                
                if not data.empty and len(data) >= Config.PLS_SEM_CONFIG['min_sample_size']:
                    latent_data = self.pls_analyzer.prepare_data(data)
                    composite_scores = self.pls_analyzer.calculate_composite_scores(latent_data)
                    results = self.pls_analyzer.run_pls_analysis(composite_scores)
                    reliability = self.pls_analyzer.calculate_reliability_validity(latent_data)
                    
                    # Análisis de bootstrap
                    bootstrap_stats = self.pls_analyzer.bootstrap_analysis(composite_scores, n_bootstrap=1000)
                    
                    # Guardar resultados
                    self.pls_analyzer.save_results()
                    
                    logger.info("Análisis PLS-SEM automático completado")
                else:
                    logger.warning("Datos insuficientes para análisis PLS-SEM automático")
                
                # Esperar 24 horas antes del siguiente análisis
                time.sleep(86400)
                
            except Exception as e:
                logger.error(f"Error en análisis PLS-SEM automático: {str(e)}")
                time.sleep(3600)  # Esperar 1 hora en caso de error
    
    def start_dashboard(self, debug=False):
        """Inicia el dashboard web"""
        logger.info("Iniciando dashboard web...")
        
        try:
            self.dashboard.run(debug=debug)
        except Exception as e:
            logger.error(f"Error iniciando dashboard: {str(e)}")
            raise
    
    def generate_system_report(self, region=None):
        """Genera reporte del sistema"""
        logger.info(f"Generando reporte del sistema para región: {region or 'todas'}")
        
        try:
            if region:
                # Reporte para región específica
                report = self.ai_orchestrator.generate_regional_report(region)
            else:
                # Reporte general del sistema
                report = {
                    'system_status': 'active' if self.is_running else 'stopped',
                    'timestamp': datetime.now().isoformat(),
                    'regions_monitored': len(Config.REGIONS),
                    'data_collection_frequency': Config.AGENTS_CONFIG['data_collector_frequency'],
                    'analysis_frequency': Config.AGENTS_CONFIG['analysis_frequency']
                }
                
                # Añadir estadísticas de regiones
                regional_stats = []
                for reg in Config.REGIONS[:5]:  # Primeras 5 regiones
                    reg_report = self.ai_orchestrator.generate_regional_report(reg)
                    if 'error' not in reg_report:
                        regional_stats.append({
                            'region': reg,
                            'confidence': reg_report.get('average_confidence', 0),
                            'analyses_count': reg_report.get('total_analyses', 0)
                        })
                
                report['regional_statistics'] = regional_stats
            
            # Guardar reporte
            report_path = os.path.join(os.path.dirname(__file__), 'exports', 
                                     f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            import json
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Reporte generado: {report_path}")
            return report
            
        except Exception as e:
            logger.error(f"Error generando reporte: {str(e)}")
            return {"error": str(e)}
    
    def stop_services(self):
        """Detiene todos los servicios"""
        logger.info("Deteniendo servicios del sistema...")
        
        self.is_running = False
        
        # Detener orquestador de IA
        self.ai_orchestrator.stop_automated_analysis()
        
        # Esperar a que los hilos terminen
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        logger.info("Servicios detenidos")
    
    def cleanup(self):
        """Limpieza al cerrar el sistema"""
        if self.is_running:
            self.stop_services()
        logger.info("Sistema cerrado correctamente")
    
    def _signal_handler(self, signum, frame):
        """Maneja señales del sistema"""
        logger.info(f"Señal recibida: {signum}. Cerrando sistema...")
        self.cleanup()
        sys.exit(0)

def main():
    """Función principal del sistema"""
    parser = argparse.ArgumentParser(description='Smart Tourism Management System')
    parser.add_argument('--mode', choices=['init', 'services', 'dashboard', 'full', 'report'], 
                       default='full', help='Modo de ejecución')
    parser.add_argument('--region', type=str, help='Región específica para reporte')
    parser.add_argument('--debug', action='store_true', help='Modo debug para dashboard')
    parser.add_argument('--no-dashboard', action='store_true', help='No iniciar dashboard')
    
    args = parser.parse_args()
    
    # Crear sistema
    system = SmartTourismSystem()
    
    try:
        if args.mode == 'init':
            # Solo inicialización
            system.initialize_system()
            print("✅ Sistema inicializado correctamente")
            
        elif args.mode == 'services':
            # Solo servicios automatizados
            system.initialize_system()
            system.start_automated_services()
            
            print("🤖 Servicios automatizados iniciados")
            print("Presiona Ctrl+C para detener...")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
        elif args.mode == 'dashboard':
            # Solo dashboard
            system.start_dashboard(debug=args.debug)
            
        elif args.mode == 'report':
            # Generar reporte
            system.initialize_system()
            report = system.generate_system_report(region=args.region)
            
            if 'error' not in report:
                print("📊 Reporte generado correctamente")
                if args.region:
                    print(f"Región: {args.region}")
                    print(f"Confianza promedio: {report.get('average_confidence', 'N/A')}")
                    print(f"Total análisis: {report.get('total_analyses', 'N/A')}")
                else:
                    print(f"Estado del sistema: {report.get('system_status', 'N/A')}")
                    print(f"Regiones monitoreadas: {report.get('regions_monitored', 'N/A')}")
            else:
                print(f"❌ Error generando reporte: {report['error']}")
                
        else:  # mode == 'full'
            # Sistema completo
            system.initialize_system()
            
            if not args.no_dashboard:
                print("🚀 Iniciando Smart Tourism Management System completo...")
                print(f"📊 Dashboard: http://localhost:{Config.DASHBOARD_CONFIG['port']}")
                print("🤖 Servicios automatizados: Activos")
                print("📈 Análisis PLS-SEM: Activo")
                print("\nPresiona Ctrl+C para detener el sistema")
                
                # Iniciar servicios en background
                system.start_automated_services()
                
                # Iniciar dashboard (bloquea hasta Ctrl+C)
                system.start_dashboard(debug=args.debug)
            else:
                # Solo servicios automatizados
                system.start_automated_services()
                
                print("🤖 Servicios automatizados iniciados (sin dashboard)")
                print("Presiona Ctrl+C para detener...")
                
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
    
    except KeyboardInterrupt:
        print("\n⏹️  Deteniendo sistema...")
    except Exception as e:
        logger.error(f"Error en ejecución principal: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    finally:
        system.cleanup()

if __name__ == "__main__":
    main()
