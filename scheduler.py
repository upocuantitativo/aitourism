"""
Smart Tourism System Scheduler
Automatización y programación de tareas del sistema
"""

import os
import sys
import time
import schedule
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any
import json
import subprocess

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from utils import DatabaseManager, SystemMonitor, ReportGenerator, CacheManager
import main

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskScheduler:
    """Programador de tareas automatizadas del sistema"""
    
    def __init__(self):
        self.scheduled_jobs = []
        self.system_monitor = SystemMonitor()
        self.cache_manager = CacheManager()
        self.is_running = False
        self.smart_system = None
        
    def setup_system(self):
        """Configura el sistema principal"""
        try:
            self.smart_system = main.SmartTourismSystem()
            logger.info("Sistema Smart Tourism inicializado para scheduler")
        except Exception as e:
            logger.error(f"Error inicializando sistema: {e}")
            self.smart_system = None
    
    def schedule_data_collection(self):
        """Programa recolección automática de datos"""
        
        def run_data_collection():
            """Ejecuta recolección de datos"""
            try:
                logger.info("Iniciando recolección programada de datos...")
                start_time = time.time()
                
                if not self.smart_system:
                    self.setup_system()
                
                if self.smart_system:
                    # Recopilar datos para todas las regiones
                    integrated_data = self.smart_system.data_collector.collect_all_data(
                        regions=Config.REGIONS
                    )
                    
                    execution_time = time.time() - start_time
                    self.system_monitor.record_metric('data_collection_time', execution_time)
                    
                    if integrated_data is not None and not integrated_data.empty:
                        logger.info(f"Recolección completada: {len(integrated_data)} registros en {execution_time:.1f}s")
                        self.system_monitor.record_metric('data_collection_records', len(integrated_data))
                    else:
                        logger.warning("Recolección de datos no produjo resultados")
                        self.system_monitor.record_metric('data_collection_records', 0)
                        
            except Exception as e:
                logger.error(f"Error en recolección programada: {e}")
                self.system_monitor.record_metric('data_collection_errors', 1)
        
        # Programar cada hora
        schedule.every().hour.at(":00").do(run_data_collection)
        
        # Programar también a intervalos específicos para mayor frecuencia
        schedule.every(Config.AGENTS_CONFIG['data_collector_frequency'] // 60).minutes.do(run_data_collection)
        
        logger.info("Recolección de datos programada cada hora y cada {} minutos".format(
            Config.AGENTS_CONFIG['data_collector_frequency'] // 60
        ))
    
    def schedule_pls_analysis(self):
        """Programa análisis PLS-SEM"""
        
        def run_pls_analysis():
            """Ejecuta análisis PLS-SEM"""
            try:
                logger.info("Iniciando análisis PLS-SEM programado...")
                start_time = time.time()
                
                if not self.smart_system:
                    self.setup_system()
                
                if self.smart_system:
                    # Cargar datos
                    data = self.smart_system.pls_analyzer.load_data()
                    
                    if not data.empty and len(data) >= Config.PLS_SEM_CONFIG['min_sample_size']:
                        # Ejecutar análisis completo
                        latent_data = self.smart_system.pls_analyzer.prepare_data(data)
                        composite_scores = self.smart_system.pls_analyzer.calculate_composite_scores(latent_data)
                        results = self.smart_system.pls_analyzer.run_pls_analysis(composite_scores)
                        reliability = self.smart_system.pls_analyzer.calculate_reliability_validity(latent_data)
                        
                        # Bootstrap analysis
                        bootstrap_stats = self.smart_system.pls_analyzer.bootstrap_analysis(
                            composite_scores, n_bootstrap=1000
                        )
                        
                        # Guardar resultados
                        self.smart_system.pls_analyzer.save_results()
                        
                        execution_time = time.time() - start_time
                        self.system_monitor.record_metric('pls_analysis_time', execution_time)
                        
                        # Extraer R² para monitoreo
                        r_squared = results.get('Complete_Model', {}).get('r_squared', 0)
                        self.system_monitor.record_metric('model_r_squared', r_squared)
                        
                        logger.info(f"Análisis PLS-SEM completado en {execution_time:.1f}s (R² = {r_squared:.3f})")
                        
                    else:
                        logger.warning(f"Datos insuficientes para PLS-SEM: {len(data)} < {Config.PLS_SEM_CONFIG['min_sample_size']}")
                        self.system_monitor.record_metric('pls_analysis_errors', 1)
                        
            except Exception as e:
                logger.error(f"Error en análisis PLS-SEM programado: {e}")
                self.system_monitor.record_metric('pls_analysis_errors', 1)
        
        # Programar análisis PLS-SEM diario a las 3:00 AM
        schedule.every().day.at("03:00").do(run_pls_analysis)
        
        logger.info("Análisis PLS-SEM programado diariamente a las 3:00 AM")
    
    def schedule_ai_analysis(self):
        """Programa análisis de IA"""
        
        def run_ai_analysis():
            """Ejecuta análisis de IA"""
            try:
                logger.info("Iniciando análisis de IA programado...")
                start_time = time.time()
                
                if not self.smart_system:
                    self.setup_system()
                
                if self.smart_system:
                    # Ejecutar análisis IA para regiones principales
                    test_regions = Config.REGIONS[:5]  # Primeras 5 regiones
                    
                    for region in test_regions:
                        try:
                            # Cargar datos de la región
                            data = self.smart_system.ai_orchestrator._load_region_data(region)
                            
                            if not data.empty:
                                # Intentar análisis con Claude
                                result = self.smart_system.ai_orchestrator.agents['claude'].analyze(
                                    data, {'region': region}
                                )
                                
                                if result.confidence_score > 0.5:
                                    self.smart_system.ai_orchestrator._store_result(result)
                                    self.system_monitor.record_metric(f'ai_confidence_{region}', result.confidence_score)
                                else:
                                    # Fallback a análisis local
                                    local_result = self.smart_system.ai_orchestrator.agents['local'].analyze(
                                        data, {'region': region}
                                    )
                                    self.smart_system.ai_orchestrator._store_result(local_result)
                                    self.system_monitor.record_metric(f'ai_confidence_{region}', local_result.confidence_score)
                                    
                        except Exception as e:
                            logger.warning(f"Error en análisis IA para {region}: {e}")
                            continue
                    
                    execution_time = time.time() - start_time
                    self.system_monitor.record_metric('ai_analysis_time', execution_time)
                    
                    logger.info(f"Análisis de IA completado para {len(test_regions)} regiones en {execution_time:.1f}s")
                    
            except Exception as e:
                logger.error(f"Error en análisis IA programado: {e}")
                self.system_monitor.record_metric('ai_analysis_errors', 1)
        
        # Programar análisis IA cada 2 horas
        schedule.every(2).hours.do(run_ai_analysis)
        
        logger.info("Análisis de IA programado cada 2 horas")
    
    def schedule_system_maintenance(self):
        """Programa mantenimiento del sistema"""
        
        def run_maintenance():
            """Ejecuta tareas de mantenimiento"""
            try:
                logger.info("Iniciando mantenimiento programado del sistema...")
                
                # Limpiar cache expirado
                cleared_cache = self.cache_manager.clear_expired(max_age_hours=24)
                
                # Backup de base de datos
                db_path = os.path.join(os.path.dirname(__file__), 'data', 'tourism_data.db')
                if os.path.exists(db_path):
                    db_manager = DatabaseManager(db_path)
                    backup_path = db_manager.backup_database()
                    logger.info(f"Backup creado: {backup_path}")
                
                # Limpiar datos antiguos (mantener últimos 2 años)
                tables_to_clean = ['integrated_data', 'ine_data', 'tripadvisor_data', 'exceltur_data']
                total_cleaned = 0
                
                for table in tables_to_clean:
                    try:
                        cleaned = db_manager.clean_old_data(table, days_to_keep=730)  # 2 años
                        total_cleaned += cleaned
                    except Exception as e:
                        logger.warning(f"Error limpiando tabla {table}: {e}")
                
                # Registrar métricas de mantenimiento
                self.system_monitor.record_metric('maintenance_cache_cleared', cleared_cache)
                self.system_monitor.record_metric('maintenance_records_cleaned', total_cleaned)
                
                logger.info(f"Mantenimiento completado: {cleared_cache} cache eliminados, {total_cleaned} registros antiguos limpiados")
                
            except Exception as e:
                logger.error(f"Error en mantenimiento programado: {e}")
                self.system_monitor.record_metric('maintenance_errors', 1)
        
        # Programar mantenimiento diario a las 2:00 AM
        schedule.every().day.at("02:00").do(run_maintenance)
        
        logger.info("Mantenimiento del sistema programado diariamente a las 2:00 AM")
    
    def schedule_report_generation(self):
        """Programa generación de reportes"""
        
        def generate_weekly_reports():
            """Genera reportes semanales"""
            try:
                logger.info("Generando reportes semanales programados...")
                
                if not self.smart_system:
                    self.setup_system()
                
                if self.smart_system:
                    # Generar reportes para regiones principales
                    main_regions = Config.REGIONS[:5]
                    
                    for region in main_regions:
                        try:
                            report = self.smart_system.generate_system_report(region=region)
                            
                            if 'error' not in report:
                                # Guardar reporte como JSON
                                timestamp = datetime.now().strftime('%Y%m%d')
                                report_path = os.path.join(
                                    os.path.dirname(__file__), 'exports', 
                                    f"weekly_report_{region}_{timestamp}.json"
                                )
                                
                                with open(report_path, 'w', encoding='utf-8') as f:
                                    json.dump(report, f, indent=2, ensure_ascii=False)
                                
                                # Intentar generar reporte Excel
                                excel_path = report_path.replace('.json', '.xlsx')
                                ReportGenerator.generate_excel_report(report, excel_path)
                                
                                logger.info(f"Reporte semanal generado para {region}")
                                
                        except Exception as e:
                            logger.warning(f"Error generando reporte para {region}: {e}")
                
            except Exception as e:
                logger.error(f"Error en generación de reportes programada: {e}")
        
        # Programar reportes semanales los lunes a las 6:00 AM
        schedule.every().monday.at("06:00").do(generate_weekly_reports)
        
        logger.info("Generación de reportes semanales programada los lunes a las 6:00 AM")
    
    def schedule_health_check(self):
        """Programa verificaciones de salud del sistema"""
        
        def health_check():
            """Verifica salud del sistema"""
            try:
                health = self.system_monitor.get_system_health()
                
                # Registrar métricas de salud
                if 'cpu_percent' in health:
                    self.system_monitor.record_metric('system_cpu', health['cpu_percent'])
                
                if 'memory_percent' in health:
                    self.system_monitor.record_metric('system_memory', health['memory_percent'])
                
                if 'disk_percent' in health:
                    self.system_monitor.record_metric('system_disk', health['disk_percent'])
                
                # Alertas básicas
                alerts = []
                
                if health.get('cpu_percent', 0) > 80:
                    alerts.append(f"Alto uso de CPU: {health['cpu_percent']:.1f}%")
                
                if health.get('memory_percent', 0) > 85:
                    alerts.append(f"Alto uso de memoria: {health['memory_percent']:.1f}%")
                
                if health.get('disk_percent', 0) > 90:
                    alerts.append(f"Alto uso de disco: {health['disk_percent']:.1f}%")
                
                if alerts:
                    logger.warning("Alertas del sistema: " + "; ".join(alerts))
                else:
                    logger.debug("Health check: Sistema operando normalmente")
                
            except Exception as e:
                logger.error(f"Error en health check: {e}")
        
        # Programar health check cada 15 minutos
        schedule.every(15).minutes.do(health_check)
        
        logger.info("Health check programado cada 15 minutos")
    
    def setup_all_schedules(self):
        """Configura todas las tareas programadas"""
        logger.info("Configurando todas las tareas programadas...")
        
        self.schedule_data_collection()
        self.schedule_pls_analysis()
        self.schedule_ai_analysis()
        self.schedule_system_maintenance()
        self.schedule_report_generation()
        self.schedule_health_check()
        
        logger.info(f"Total de tareas programadas: {len(schedule.jobs)}")
    
    def run_scheduler(self):
        """Ejecuta el programador de tareas"""
        self.is_running = True
        logger.info("Iniciando scheduler de tareas...")
        
        # Configurar todas las tareas
        self.setup_all_schedules()
        
        # Inicializar sistema
        self.setup_system()
        
        # Ejecutar loop principal
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
                
        except KeyboardInterrupt:
            logger.info("Scheduler detenido por usuario")
        except Exception as e:
            logger.error(f"Error en scheduler: {e}")
        finally:
            self.stop_scheduler()
    
    def stop_scheduler(self):
        """Detiene el programador de tareas"""
        self.is_running = False
        schedule.clear()
        logger.info("Scheduler detenido y tareas limpiadas")
    
    def get_scheduled_jobs_info(self) -> List[Dict[str, Any]]:
        """Obtiene información de tareas programadas"""
        jobs_info = []
        
        for job in schedule.jobs:
            jobs_info.append({
                'function': job.job_func.__name__,
                'interval': str(job.interval),
                'unit': job.unit,
                'at_time': str(job.at_time) if job.at_time else None,
                'next_run': job.next_run.isoformat() if job.next_run else None
            })
        
        return jobs_info

class SystemAutostart:
    """Configurador de inicio automático del sistema"""
    
    @staticmethod
    def create_systemd_service(service_name: str = "atourism-system"):
        """Crea servicio systemd para Linux (solo para referencia)"""
        service_content = f"""[Unit]
Description=Smart Tourism Management System
After=network.target

[Service]
Type=simple
User=atourism
WorkingDirectory={os.path.dirname(os.path.abspath(__file__))}
ExecStart=/usr/bin/python3 {os.path.abspath(__file__)} --mode scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_path = f"/etc/systemd/system/{service_name}.service"
        
        print(f"Para instalar como servicio systemd, crear archivo {service_path} con contenido:")
        print(service_content)
        print("\nComandos de instalación:")
        print(f"sudo systemctl enable {service_name}")
        print(f"sudo systemctl start {service_name}")
        print(f"sudo systemctl status {service_name}")
    
    @staticmethod
    def create_windows_task():
        """Crea tarea programada para Windows (solo para referencia)"""
        script_path = os.path.abspath(__file__)
        python_path = sys.executable
        
        task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Smart Tourism Management System Scheduler</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>S4U</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>{script_path} --mode scheduler</Arguments>
      <WorkingDirectory>{os.path.dirname(script_path)}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
        
        print("Para instalar como tarea programada de Windows:")
        print("1. Abrir 'Programador de tareas' como administrador")
        print("2. Crear tarea básica...")
        print("3. Configurar para ejecutar al inicio del sistema")
        print(f"4. Programa: {python_path}")
        print(f"5. Argumentos: {script_path} --mode scheduler")
        print(f"6. Directorio de trabajo: {os.path.dirname(script_path)}")

def main():
    """Función principal del scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Tourism System Scheduler')
    parser.add_argument('--mode', choices=['scheduler', 'info', 'install-service'], 
                       default='scheduler', help='Modo de ejecución')
    
    args = parser.parse_args()
    
    if args.mode == 'scheduler':
        # Ejecutar scheduler
        scheduler = TaskScheduler()
        
        print("🤖 Smart Tourism System Scheduler")
        print("=" * 50)
        print("Iniciando programador de tareas automatizadas...")
        print("Presiona Ctrl+C para detener")
        print("")
        
        try:
            scheduler.run_scheduler()
        except KeyboardInterrupt:
            print("\n⏹️  Deteniendo scheduler...")
            scheduler.stop_scheduler()
    
    elif args.mode == 'info':
        # Mostrar información de tareas programadas
        scheduler = TaskScheduler()
        scheduler.setup_all_schedules()
        
        jobs_info = scheduler.get_scheduled_jobs_info()
        
        print("📋 Tareas Programadas del Sistema")
        print("=" * 50)
        
        for i, job in enumerate(jobs_info, 1):
            print(f"{i}. {job['function']}")
            print(f"   Intervalo: cada {job['interval']} {job['unit']}")
            if job['at_time']:
                print(f"   Hora: {job['at_time']}")
            if job['next_run']:
                print(f"   Próxima ejecución: {job['next_run']}")
            print()
    
    elif args.mode == 'install-service':
        # Información para instalar como servicio
        print("🔧 Instalación como Servicio del Sistema")
        print("=" * 50)
        
        autostart = SystemAutostart()
        
        if os.name == 'posix':  # Linux/Mac
            autostart.create_systemd_service()
        else:  # Windows
            autostart.create_windows_task()

if __name__ == "__main__":
    main()
