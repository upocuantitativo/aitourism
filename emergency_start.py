"""
Emergency Start Script - Smart Tourism Management System
Script de emergencia para iniciar el sistema con dependencias mínimas
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_critical_imports():
    """Verifica las importaciones críticas"""
    critical_modules = {
        'requests': 'requests',
        'pandas': 'pandas',
        'numpy': 'numpy',  
        'plotly': 'plotly.graph_objects',
        'dash': 'dash'
    }
    
    missing_modules = []
    available_modules = []
    
    for name, module in critical_modules.items():
        try:
            __import__(module)
            available_modules.append(name)
            logger.info(f"✅ {name} disponible")
        except ImportError:
            missing_modules.append(name)
            logger.error(f"❌ {name} no disponible")
    
    return available_modules, missing_modules

def emergency_dashboard():
    """Dashboard de emergencia con dependencias mínimas"""
    try:
        from dash import Dash, html, dcc
        import plotly.graph_objects as go
        
        app = Dash(__name__)
        
        app.layout = html.Div([
            html.H1("🚨 Smart Tourism System - Modo Emergencia"),
            html.Div([
                html.H3("Estado del Sistema"),
                html.P("El sistema está ejecutándose en modo emergencia con funcionalidad limitada."),
                html.H3("Información"),
                html.Ul([
                    html.Li("Algunas dependencias no están disponibles"),
                    html.Li("Funcionalidad reducida activada"),
                    html.Li("Para funcionalidad completa, instalar todas las dependencias")
                ]),
                html.H3("Instrucciones"),
                html.Ol([
                    html.Li("Ejecutar: fix_dependencies.bat (Windows)"),
                    html.Li("O: pip install -r requirements-minimal.txt"),
                    html.Li("Después: python main.py --mode full")
                ])
            ], style={'margin': '20px', 'padding': '20px', 'border': '1px solid #ccc'})
        ])
        
        logger.info("🚀 Iniciando dashboard de emergencia en puerto 8050...")
        app.run_server(host='0.0.0.0', port=8050, debug=False)
        
    except Exception as e:
        logger.error(f"Error iniciando dashboard de emergencia: {e}")
        print("\n❌ No se puede iniciar dashboard de emergencia")
        print("🔧 Solución:")
        print("1. Ejecutar: fix_dependencies.bat")
        print("2. O instalar manualmente: pip install dash plotly")

def basic_data_generator():
    """Generador de datos básico sin dependencias externas"""
    try:
        import pandas as pd
        import numpy as np
        import sqlite3
        from datetime import datetime, timedelta
        
        logger.info("📊 Generando datos básicos...")
        
        # Crear directorio de datos
        os.makedirs('data', exist_ok=True)
        
        # Generar datos sintéticos básicos
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', end='2025-01-01', freq='M')
        regions = ['Andalucía', 'Cataluña', 'Madrid']
        
        data = []
        for region in regions:
            for date in dates:
                data.append({
                    'region': region,
                    'date': date.strftime('%Y-%m-%d'),
                    'room_occupancy_rate': np.random.normal(65, 10),
                    'tourism_employment': int(np.random.normal(45000, 5000)),
                    'tourism_competitiveness_index': np.random.normal(75, 8),
                    'current_rank': np.random.randint(1, 101),
                    'total_reviews': int(np.random.normal(5000, 1000)),
                    'total_facilities': int(np.random.normal(850, 100)),
                    'performance_economic_social_benefit': np.random.normal(78, 6),
                    'collection_timestamp': datetime.now().isoformat()
                })
        
        df = pd.DataFrame(data)
        
        # Guardar en base de datos
        with sqlite3.connect('data/tourism_data.db') as conn:
            # Crear tabla
            conn.execute("""
            CREATE TABLE IF NOT EXISTS integrated_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT,
                date TEXT,
                room_occupancy_rate REAL,
                tourism_employment INTEGER,
                tourism_competitiveness_index REAL,
                current_rank INTEGER,
                total_reviews INTEGER,
                total_facilities INTEGER,
                performance_economic_social_benefit REAL,
                collection_timestamp TEXT
            )
            """)
            
            # Insertar datos
            df.to_sql('integrated_data', conn, if_exists='replace', index=False)
            
        logger.info(f"✅ Datos básicos generados: {len(df)} registros")
        return True
        
    except Exception as e:
        logger.error(f"Error generando datos básicos: {e}")
        return False

def main():
    """Función principal de emergencia"""
    print("🚨 SMART TOURISM SYSTEM - MODO EMERGENCIA")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar importaciones críticas
    available, missing = check_critical_imports()
    
    print(f"📊 Estado de dependencias:")
    print(f"✅ Disponibles: {len(available)} - {', '.join(available)}")
    if missing:
        print(f"❌ Faltantes: {len(missing)} - {', '.join(missing)}")
    
    if len(missing) > 0:
        print("\n🔧 SOLUCIÓN RECOMENDADA:")
        print("1. Ejecutar: fix_dependencies.bat (Windows)")
        print("2. O: pip install -r requirements-minimal.txt")
        print("3. Después: python main.py --mode full")
        print()
    
    # Verificar si podemos generar datos básicos
    if 'pandas' in available and 'numpy' in available:
        if not os.path.exists('data/tourism_data.db'):
            print("📊 Generando datos básicos...")
            basic_data_generator()
    
    # Intentar iniciar dashboard de emergencia
    if 'dash' in available and 'plotly' in available:
        print("🚀 Iniciando dashboard de emergencia...")
        print("📊 Dashboard disponible en: http://localhost:8050")
        print("⏹️ Presionar Ctrl+C para detener")
        print()
        emergency_dashboard()
    else:
        print("\n❌ No se puede iniciar dashboard (dash/plotly no disponibles)")
        print("🔧 Ejecutar: pip install dash plotly")
        print("💡 O usar el script: fix_dependencies.bat")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Sistema detenido por usuario")
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        print(f"\n❌ Error crítico: {e}")
        print("🔧 Ejecutar fix_dependencies.bat para solucionar problemas")
