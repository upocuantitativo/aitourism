"""
Utilities and Helper Functions for Smart Tourism Management System
Funciones de utilidad y helper para el sistema
"""

import os
import json
import pandas as pd
import numpy as np
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pickle
import zipfile
import shutil

logger = logging.getLogger(__name__)

class DataValidator:
    """Validador de calidad de datos"""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, required_columns: List[str] = None) -> Dict[str, Any]:
        """Valida la calidad de un DataFrame"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'quality_score': 0.0,
            'metrics': {}
        }
        
        if df.empty:
            validation_result['is_valid'] = False
            validation_result['errors'].append('DataFrame está vacío')
            return validation_result
        
        # Verificar columnas requeridas
        if required_columns:
            missing_cols = set(required_columns) - set(df.columns)
            if missing_cols:
                validation_result['errors'].append(f'Columnas faltantes: {missing_cols}')
                validation_result['is_valid'] = False
        
        # Métricas de calidad
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        completeness = 1 - (null_cells / total_cells) if total_cells > 0 else 0
        
        # Detectar duplicados
        duplicates = df.duplicated().sum()
        duplicate_rate = duplicates / len(df) if len(df) > 0 else 0
        
        # Detectar outliers (para columnas numéricas)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outliers_count = 0
        
        for col in numeric_cols:
            if df[col].notna().sum() > 0:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                outliers_count += outliers
        
        outlier_rate = outliers_count / total_cells if total_cells > 0 else 0
        
        # Calcular score de calidad
        quality_score = (
            completeness * 0.4 +  # 40% completitud
            (1 - duplicate_rate) * 0.3 +  # 30% unicidad
            (1 - outlier_rate) * 0.3  # 30% consistencia
        )
        
        validation_result['quality_score'] = round(quality_score, 3)
        validation_result['metrics'] = {
            'completeness': round(completeness, 3),
            'duplicate_rate': round(duplicate_rate, 3),
            'outlier_rate': round(outlier_rate, 3),
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': len(numeric_cols)
        }
        
        # Warnings basados en métricas
        if completeness < 0.8:
            validation_result['warnings'].append(f'Baja completitud de datos: {completeness:.1%}')
        
        if duplicate_rate > 0.05:
            validation_result['warnings'].append(f'Alta tasa de duplicados: {duplicate_rate:.1%}')
        
        if outlier_rate > 0.1:
            validation_result['warnings'].append(f'Alta tasa de outliers: {outlier_rate:.1%}')
        
        return validation_result

class DatabaseManager:
    """Gestor de base de datos con utilidades avanzadas"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def backup_database(self, backup_path: str = None) -> str:
        """Crea backup de la base de datos"""
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.db_path}.backup_{timestamp}.db"
        
        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Backup creado: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            raise
    
    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Obtiene estadísticas de una tabla"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Contar registros
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                # Información de columnas
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = cursor.fetchall()
                
                # Fecha más reciente y más antigua
                cursor.execute(f"SELECT MIN(date), MAX(date) FROM {table_name} WHERE date IS NOT NULL")
                date_range = cursor.fetchone()
                
                stats = {
                    'table_name': table_name,
                    'row_count': row_count,
                    'column_count': len(columns_info),
                    'columns': [col[1] for col in columns_info],
                    'date_range': {
                        'min_date': date_range[0] if date_range[0] else None,
                        'max_date': date_range[1] if date_range[1] else None
                    }
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de {table_name}: {e}")
            return {}
    
    def clean_old_data(self, table_name: str, days_to_keep: int = 365) -> int:
        """Limpia datos antiguos de una tabla"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {table_name} WHERE date < ?", (cutoff_str,))
                deleted_rows = cursor.rowcount
                conn.commit()
                
                logger.info(f"Eliminados {deleted_rows} registros antiguos de {table_name}")
                return deleted_rows
                
        except Exception as e:
            logger.error(f"Error limpiando datos antiguos: {e}")
            return 0

class ReportGenerator:
    """Generador de reportes en diferentes formatos"""
    
    @staticmethod
    def generate_pdf_report(data: Dict[str, Any], output_path: str) -> bool:
        """Genera reporte en PDF"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Centro
            )
            
            story.append(Paragraph("Smart Tourism Management System Report", title_style))
            story.append(Spacer(1, 12))
            
            # Información general
            info_data = [
                ['Region', data.get('region', 'N/A')],
                ['Report Date', data.get('report_date', 'N/A')],
                ['Analysis Period', data.get('analysis_period', 'N/A')],
                ['Average Confidence', f"{data.get('average_confidence', 0):.2%}"]
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 12))
            
            # Recomendaciones
            story.append(Paragraph("Top Recommendations", styles['Heading2']))
            
            recommendations = data.get('top_recommendations', [])
            for i, rec in enumerate(recommendations[:5], 1):
                rec_text = f"{i}. {rec.get('recommendation', 'N/A')} (Frequency: {rec.get('frequency', 0)})"
                story.append(Paragraph(rec_text, styles['Normal']))
                story.append(Spacer(1, 6))
            
            # Construir PDF
            doc.build(story)
            logger.info(f"Reporte PDF generado: {output_path}")
            return True
            
        except ImportError:
            logger.warning("ReportLab no disponible para generar PDFs")
            return False
        except Exception as e:
            logger.error(f"Error generando reporte PDF: {e}")
            return False
    
    @staticmethod
    def generate_excel_report(data: Dict[str, Any], output_path: str) -> bool:
        """Genera reporte en Excel"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Hoja de resumen
                summary_data = {
                    'Metric': ['Region', 'Report Date', 'Analysis Period', 'Average Confidence', 'Total Analyses'],
                    'Value': [
                        data.get('region', 'N/A'),
                        data.get('report_date', 'N/A'),
                        data.get('analysis_period', 'N/A'),
                        f"{data.get('average_confidence', 0):.2%}",
                        data.get('total_analyses', 0)
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Hoja de recomendaciones
                recommendations = data.get('top_recommendations', [])
                if recommendations:
                    rec_df = pd.DataFrame(recommendations)
                    rec_df.to_excel(writer, sheet_name='Recommendations', index=False)
                
                # Hoja de análisis más reciente
                latest_analysis = data.get('latest_analysis', {})
                if latest_analysis:
                    analysis_data = {
                        'Metric': ['Timestamp', 'Type', 'Confidence'],
                        'Value': [
                            latest_analysis.get('timestamp', 'N/A'),
                            latest_analysis.get('type', 'N/A'),
                            f"{latest_analysis.get('confidence', 0):.2%}"
                        ]
                    }
                    
                    analysis_df = pd.DataFrame(analysis_data)
                    analysis_df.to_excel(writer, sheet_name='Latest Analysis', index=False)
            
            logger.info(f"Reporte Excel generado: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generando reporte Excel: {e}")
            return False

class SystemMonitor:
    """Monitor del sistema para métricas de rendimiento"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = datetime.now()
        
    def record_metric(self, metric_name: str, value: float, timestamp: datetime = None):
        """Registra una métrica del sistema"""
        if timestamp is None:
            timestamp = datetime.now()
            
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
            
        self.metrics[metric_name].append({
            'timestamp': timestamp,
            'value': value
        })
        
        # Mantener solo últimas 1000 mediciones por métrica
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]
    
    def get_system_health(self) -> Dict[str, Any]:
        """Obtiene el estado de salud del sistema"""
        try:
            import psutil
            
            health = {
                'uptime': str(datetime.now() - self.start_time),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
                'timestamp': datetime.now().isoformat()
            }
            
            # Añadir métricas personalizadas
            for metric_name, values in self.metrics.items():
                if values:
                    recent_values = [v['value'] for v in values[-10:]]  # Últimas 10 mediciones
                    health[f'{metric_name}_avg'] = sum(recent_values) / len(recent_values)
                    health[f'{metric_name}_last'] = recent_values[-1]
            
            return health
            
        except ImportError:
            logger.warning("psutil no disponible para métricas del sistema")
            return {
                'uptime': str(datetime.now() - self.start_time),
                'timestamp': datetime.now().isoformat(),
                'status': 'monitoring_limited'
            }
        except Exception as e:
            logger.error(f"Error obteniendo salud del sistema: {e}")
            return {'status': 'error', 'error': str(e)}

class ConfigManager:
    """Gestor de configuración con validación"""
    
    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        """Carga configuración desde archivo JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"Configuración cargada desde {config_path}")
            return config
            
        except FileNotFoundError:
            logger.error(f"Archivo de configuración no encontrado: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando configuración JSON: {e}")
            return {}
    
    @staticmethod
    def save_config(config: Dict[str, Any], config_path: str) -> bool:
        """Guarda configuración en archivo JSON"""
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuración guardada en {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            return False
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> List[str]:
        """Valida configuración y retorna lista de errores"""
        errors = []
        
        # Validaciones básicas
        required_keys = ['REGIONS', 'PLS_SEM_CONFIG', 'DASHBOARD_CONFIG', 'AGENTS_CONFIG']
        
        for key in required_keys:
            if key not in config:
                errors.append(f"Clave requerida faltante: {key}")
        
        # Validar regiones
        if 'REGIONS' in config:
            if not isinstance(config['REGIONS'], list) or len(config['REGIONS']) == 0:
                errors.append("REGIONS debe ser una lista no vacía")
        
        # Validar configuración PLS-SEM
        if 'PLS_SEM_CONFIG' in config:
            pls_config = config['PLS_SEM_CONFIG']
            if 'min_sample_size' not in pls_config or pls_config['min_sample_size'] < 30:
                errors.append("min_sample_size debe ser >= 30")
        
        return errors

class CacheManager:
    """Gestor de cache para mejorar rendimiento"""
    
    def __init__(self, cache_dir: str = 'cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
    def get_cache_key(self, *args) -> str:
        """Genera clave de cache a partir de argumentos"""
        import hashlib
        key_string = '_'.join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str, max_age_hours: int = 24) -> Any:
        """Obtiene valor del cache si no está expirado"""
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        
        if not os.path.exists(cache_file):
            return None
        
        # Verificar edad del archivo
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        if file_age.total_seconds() > max_age_hours * 3600:
            os.remove(cache_file)
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning(f"Error leyendo cache {key}: {e}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """Guarda valor en cache"""
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
            return True
        except Exception as e:
            logger.error(f"Error guardando cache {key}: {e}")
            return False
    
    def clear_expired(self, max_age_hours: int = 24) -> int:
        """Limpia archivos de cache expirados"""
        cleared_count = 0
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                file_path = os.path.join(self.cache_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_time < cutoff_time:
                    try:
                        os.remove(file_path)
                        cleared_count += 1
                    except Exception as e:
                        logger.warning(f"Error eliminando cache expirado {filename}: {e}")
        
        logger.info(f"Cache limpiado: {cleared_count} archivos eliminados")
        return cleared_count

# Funciones de utilidad globales

def setup_logging(log_level: str = 'INFO', log_file: str = None):
    """Configura logging del sistema"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if log_file:
        logging.basicConfig(
            level=numeric_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(level=numeric_level, format=log_format)

def ensure_directory(directory_path: str):
    """Asegura que un directorio existe"""
    os.makedirs(directory_path, exist_ok=True)

def get_project_root() -> str:
    """Obtiene el directorio raíz del proyecto"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def format_timestamp(timestamp: datetime = None, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Formatea timestamp"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(format_str)

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """División segura que evita división por cero"""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calcula cambio porcentual"""
    if old_value == 0:
        return 0.0 if new_value == 0 else float('inf')
    return ((new_value - old_value) / old_value) * 100

# Decoradores útiles

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorador para reintentar función en caso de error"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    logger.warning(f"Intento {attempt + 1} falló para {func.__name__}: {e}")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

def timing(func):
    """Decorador para medir tiempo de ejecución"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} ejecutado en {end_time - start_time:.2f} segundos")
        return result
    return wrapper

import time

if __name__ == "__main__":
    # Ejemplo de uso de las utilidades
    print("🔧 Testing Smart Tourism System Utilities")
    
    # Test DataValidator
    test_data = pd.DataFrame({
        'region': ['Andalucía', 'Cataluña', None],
        'value': [100, 200, 300],
        'date': ['2025-01-01', '2025-01-02', '2025-01-03']
    })
    
    validator = DataValidator()
    validation = validator.validate_dataframe(test_data, required_columns=['region', 'value'])
    print(f"✅ Validación completada: Score {validation['quality_score']}")
    
    # Test SystemMonitor
    monitor = SystemMonitor()
    monitor.record_metric('test_metric', 0.85)
    health = monitor.get_system_health()
    print(f"✅ Sistema monitoreado: {health.get('status', 'running')}")
    
    print("🎉 Utilities test completado")
