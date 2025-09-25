"""
Script para importar datos desde Excel al sistema Smart Tourism
Integra data_final.xlsx con la base de datos del sistema
"""

import pandas as pd
import sqlite3
import os
import sys
from datetime import datetime
import numpy as np

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_excel_file(excel_path):
    """Analiza la estructura del archivo Excel"""
    print(f"\n📊 Analizando archivo: {excel_path}")
    print("=" * 60)
    
    try:
        # Leer Excel
        df = pd.read_excel(excel_path)
        
        print(f"✅ Archivo leído exitosamente")
        print(f"📏 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
        print(f"\n📋 Columnas encontradas:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. {col}")
        
        print(f"\n📝 Primeras 5 filas:")
        print(df.head())
        
        print(f"\n📊 Tipos de datos:")
        print(df.dtypes)
        
        return df
        
    except FileNotFoundError:
        print(f"❌ Error: No se encuentra el archivo {excel_path}")
        print(f"📁 Directorio actual: {os.getcwd()}")
        return None
    except Exception as e:
        print(f"❌ Error leyendo Excel: {e}")
        return None

def map_excel_to_system_format(df):
    """Mapea las columnas del Excel al formato del sistema"""
    print("\n🔄 Mapeando datos al formato del sistema...")
    
    # Mapeo flexible de columnas comunes
    # Ajusta este diccionario según las columnas de tu Excel
    possible_mappings = {
        # Región
        'region': ['region', 'región', 'provincia', 'comunidad', 'area', 'zona'],
        # Fecha
        'date': ['date', 'fecha', 'periodo', 'mes', 'año', 'time', 'timestamp'],
        # Ocupación hotelera
        'room_occupancy_rate': ['occupancy', 'ocupación', 'ocupacion', 'room_occupancy', 'ocupancy_rate'],
        # Empleo turístico
        'tourism_employment': ['employment', 'empleo', 'empleados', 'trabajadores', 'jobs'],
        # Índice de competitividad
        'tourism_competitiveness_index': ['competitiveness', 'competitividad', 'index', 'índice', 'indice'],
        # Ranking
        'current_rank': ['rank', 'ranking', 'posición', 'posicion', 'puesto'],
        # Reviews/Valoraciones
        'total_reviews': ['reviews', 'valoraciones', 'opiniones', 'comentarios'],
        # Facilidades
        'total_facilities': ['facilities', 'facilidades', 'instalaciones', 'servicios'],
        # Beneficio económico-social
        'performance_economic_social_benefit': ['benefit', 'beneficio', 'performance', 'rendimiento', 'impacto']
    }
    
    # Buscar coincidencias automáticas
    column_mapping = {}
    df_columns_lower = [col.lower() for col in df.columns]
    
    for system_col, possible_names in possible_mappings.items():
        for excel_col, excel_col_lower in zip(df.columns, df_columns_lower):
            for possible_name in possible_names:
                if possible_name in excel_col_lower:
                    column_mapping[excel_col] = system_col
                    print(f"  ✅ '{excel_col}' → '{system_col}'")
                    break
            if excel_col in column_mapping:
                break
    
    # Aplicar mapeo
    df_mapped = pd.DataFrame()
    
    for excel_col, system_col in column_mapping.items():
        df_mapped[system_col] = df[excel_col]
    
    # Añadir columnas faltantes con valores por defecto
    required_columns = [
        'region', 'date', 'room_occupancy_rate', 'tourism_employment',
        'tourism_competitiveness_index', 'current_rank', 'total_reviews',
        'total_facilities', 'performance_economic_social_benefit'
    ]
    
    for col in required_columns:
        if col not in df_mapped.columns:
            print(f"  ⚠️  Columna '{col}' no encontrada, usando valores por defecto")
            if col == 'date':
                df_mapped[col] = datetime.now().strftime('%Y-%m-%d')
            elif col == 'region':
                df_mapped[col] = 'Sin especificar'
            else:
                df_mapped[col] = 0
    
    # Añadir metadatos
    df_mapped['collection_timestamp'] = datetime.now()
    df_mapped['source'] = 'Excel Import'
    
    # Convertir fecha a formato string si es necesario
    if 'date' in df_mapped.columns:
        df_mapped['date'] = pd.to_datetime(df_mapped['date']).dt.strftime('%Y-%m-%d')
    
    print(f"\n✅ Datos mapeados: {len(df_mapped)} registros")
    return df_mapped

def import_to_database(df, db_path='data/tourism_data.db'):
    """Importa los datos a la base de datos del sistema"""
    print("\n💾 Importando datos a la base de datos...")
    
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Conectar a la base de datos
        with sqlite3.connect(db_path) as conn:
            # Crear tabla si no existe
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
                collection_timestamp TEXT,
                source TEXT
            )
            """)
            
            # Verificar registros existentes
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM integrated_data")
            existing_records = cursor.fetchone()[0]
            print(f"  📊 Registros existentes: {existing_records}")
            
            # Insertar nuevos datos
            df.to_sql('integrated_data', conn, if_exists='append', index=False)
            
            # Verificar inserción
            cursor.execute("SELECT COUNT(*) FROM integrated_data")
            new_total = cursor.fetchone()[0]
            imported = new_total - existing_records
            
            print(f"  ✅ Registros importados: {imported}")
            print(f"  📊 Total registros en BD: {new_total}")
            
            # Mostrar resumen por región
            cursor.execute("""
                SELECT region, COUNT(*) as count 
                FROM integrated_data 
                WHERE source = 'Excel Import'
                GROUP BY region
            """)
            
            print("\n📍 Resumen por región:")
            for region, count in cursor.fetchall():
                print(f"  - {region}: {count} registros")
            
        return True
        
    except Exception as e:
        print(f"❌ Error importando a base de datos: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 IMPORTADOR DE DATOS EXCEL - Smart Tourism System")
    print("=" * 60)
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
    else:
        # Buscar archivo por defecto
        possible_files = ['data_final.xlsx', 'data/data_final.xlsx', '../data_final.xlsx']
        excel_path = None
        
        for file in possible_files:
            if os.path.exists(file):
                excel_path = file
                break
        
        if not excel_path:
            print("❌ No se especificó archivo Excel")
            print("📝 Uso: python import_excel_data.py <ruta_archivo.xlsx>")
            print("\n🔍 Archivos Excel en el directorio:")
            for file in os.listdir('.'):
                if file.endswith('.xlsx'):
                    print(f"  - {file}")
            return
    
    # Analizar archivo
    df = analyze_excel_file(excel_path)
    if df is None:
        return
    
    # Preguntar si continuar
    print("\n❓ ¿Desea importar estos datos al sistema? (s/n): ", end='')
    response = input().lower()
    
    if response != 's':
        print("❌ Importación cancelada")
        return
    
    # Mapear y importar
    df_mapped = map_excel_to_system_format(df)
    
    if import_to_database(df_mapped):
        print("\n✨ ¡Importación completada exitosamente!")
        print("📊 Los datos están disponibles en el dashboard")
        print("🚀 Ejecutar: python main.py --mode full")
    else:
        print("\n❌ Error en la importación")

if __name__ == "__main__":
    main()
