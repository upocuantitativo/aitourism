"""
Data Collectors for Smart Tourism Management System
Automated data collection from INE, TripAdvisor, and Exceltur
"""

import requests
import pandas as pd
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import sqlite3
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector(ABC):
    """Clase base abstracta para todos los recolectores de datos"""
    
    def __init__(self, name: str):
        self.name = name
        self.last_update = None
        self.data_cache = {}
        
    @abstractmethod
    def collect_data(self, region: str, date_range: tuple) -> pd.DataFrame:
        """Método abstracto para recopilar datos"""
        pass
    
    def save_data(self, data: pd.DataFrame, table_name: str):
        """Guarda datos en la base de datos local"""
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tourism_data.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            data.to_sql(table_name, conn, if_exists='replace', index=False)
            logger.info(f"Datos guardados en tabla {table_name}: {len(data)} registros")

class INEDataCollector(DataCollector):
    """Recolector de datos del Instituto Nacional de Estadística"""
    
    def __init__(self):
        super().__init__("INE_Collector")
        self.base_url = Config.INE_BASE_URL
        
    def collect_data(self, region: str, date_range: tuple) -> pd.DataFrame:
        """Recopila datos de ocupación hotelera y empleo turístico del INE"""
        try:
            # Datos de ocupación hotelera
            hotel_data = self._get_hotel_occupancy_data(region, date_range)
            
            # Datos de empleo turístico
            employment_data = self._get_tourism_employment_data(region, date_range)
            
            # Datos de establecimientos turísticos
            establishments_data = self._get_establishments_data(region, date_range)
            
            # Combinar todos los datos
            combined_data = pd.merge(hotel_data, employment_data, on=['region', 'date'], how='outer')
            combined_data = pd.merge(combined_data, establishments_data, on=['region', 'date'], how='outer')
            
            combined_data['source'] = 'INE'
            combined_data['collection_timestamp'] = datetime.now()
            
            self.save_data(combined_data, 'ine_data')
            return combined_data
            
        except Exception as e:
            logger.error(f"Error recopilando datos INE para {region}: {str(e)}")
            return pd.DataFrame()
    
    def _get_hotel_occupancy_data(self, region: str, date_range: tuple) -> pd.DataFrame:
        """Obtiene datos de ocupación hotelera"""
        # Simulación de datos del INE (en implementación real usar API oficial)
        dates = pd.date_range(start=date_range[0], end=date_range[1], freq='M')
        
        data = []
        for date in dates:
            # Generar datos sintéticos basados en patrones reales
            base_occupancy = 65.0  # Ocupación base del 65%
            seasonal_factor = 1.2 if date.month in [6, 7, 8, 12] else 0.9
            random_factor = 0.9 + (hash(f"{region}{date}") % 100) / 500  # Factor pseudo-aleatorio
            
            occupancy_rate = base_occupancy * seasonal_factor * random_factor
            
            data.append({
                'region': region,
                'date': date,
                'room_occupancy_rate': round(occupancy_rate, 2),
                'bed_occupancy_rate': round(occupancy_rate * 0.85, 2),
                'average_stay': round(2.5 + (hash(f"{region}{date}") % 30) / 100, 2),
                'total_travelers': int(50000 * seasonal_factor * random_factor)
            })
        
        return pd.DataFrame(data)
    
    def _get_tourism_employment_data(self, region: str, date_range: tuple) -> pd.DataFrame:
        """Obtiene datos de empleo turístico"""
        dates = pd.date_range(start=date_range[0], end=date_range[1], freq='M')
        
        data = []
        for date in dates:
            base_employment = 45000  # Empleo base
            growth_factor = 1.02 ** ((date.year - 2020) * 12 + date.month)  # Crecimiento anual del 2%
            seasonal_factor = 1.15 if date.month in [6, 7, 8] else 0.95
            
            employment = int(base_employment * growth_factor * seasonal_factor)
            
            data.append({
                'region': region,
                'date': date,
                'tourism_employment': employment,
                'employment_growth_rate': round((growth_factor - 1) * 100, 2)
            })
        
        return pd.DataFrame(data)
    
    def _get_establishments_data(self, region: str, date_range: tuple) -> pd.DataFrame:
        """Obtiene datos de establecimientos turísticos"""
        dates = pd.date_range(start=date_range[0], end=date_range[1], freq='M')
        
        data = []
        base_establishments = 1200
        
        for date in dates:
            growth = (date.year - 2020) * 20 + (hash(f"{region}{date}") % 10)
            total_establishments = base_establishments + growth
            
            data.append({
                'region': region,
                'date': date,
                'total_establishments': total_establishments,
                'hotel_establishments': int(total_establishments * 0.4),
                'rural_establishments': int(total_establishments * 0.3),
                'apartment_establishments': int(total_establishments * 0.3)
            })
        
        return pd.DataFrame(data)

class TripAdvisorDataCollector(DataCollector):
    """Recolector de datos de TripAdvisor"""
    
    def __init__(self):
        super().__init__("TripAdvisor_Collector")
        self.api_key = Config.TRIPADVISOR_API_KEY
        
    def collect_data(self, region: str, date_range: tuple) -> pd.DataFrame:
        """Recopila datos de TripAdvisor sobre valoraciones y ranking"""
        try:
            # Datos de rankings y valoraciones
            rating_data = self._get_ratings_data(region, date_range)
            
            # Datos de facilidades y servicios
            facilities_data = self._get_facilities_data(region, date_range)
            
            # Combinar datos
            combined_data = pd.merge(rating_data, facilities_data, on=['region', 'date'], how='outer')
            combined_data['source'] = 'TripAdvisor'
            combined_data['collection_timestamp'] = datetime.now()
            
            self.save_data(combined_data, 'tripadvisor_data')
            return combined_data
            
        except Exception as e:
            logger.error(f"Error recopilando datos TripAdvisor para {region}: {str(e)}")
            return pd.DataFrame()
    
    def _get_ratings_data(self, region: str, date_range: tuple) -> pd.DataFrame:
        """Obtiene datos de valoraciones y rankings"""
        dates = pd.date_range(start=date_range[0], end=date_range[1], freq='M')
        
        data = []
        for date in dates:
            # Simular datos de TripAdvisor
            base_rating = 4.2
            trend = 0.1 * ((date.year - 2020) + date.month / 12)
            noise = (hash(f"{region}{date}") % 100 - 50) / 1000
            
            current_rating = base_rating + trend + noise
            current_rating = max(1.0, min(5.0, current_rating))
            
            data.append({
                'region': region,
                'date': date,
                'average_rating': round(current_rating, 2),
                'total_reviews': int(5000 + (date.year - 2020) * 500 + (hash(f"{region}{date}") % 1000)),
                'current_rank': hash(f"{region}{date}") % 100 + 1,  # Ranking entre 1-100
                'review_growth_rate': round((hash(f"{region}{date}") % 20 - 10) / 10, 2)
            })
        
        return pd.DataFrame(data)
    
    def _get_facilities_data(self, region: str, date_range: tuple) -> pd.DataFrame:
        """Obtiene datos de facilidades turísticas"""
        dates = pd.date_range(start=date_range[0], end=date_range[1], freq='M')
        
        data = []
        for date in dates:
            base_facilities = 850
            growth = (date.year - 2020) * 25
            
            data.append({
                'region': region,
                'date': date,
                'total_facilities': base_facilities + growth,
                'restaurants': int((base_facilities + growth) * 0.4),
                'attractions': int((base_facilities + growth) * 0.3),
                'activities': int((base_facilities + growth) * 0.3)
            })
        
        return pd.DataFrame(data)

class ExcelturDataCollector(DataCollector):
    """Recolector de datos de Exceltur (MONITUR)"""
    
    def __init__(self):
        super().__init__("Exceltur_Collector")
        self.base_url = Config.EXCELTUR_BASE_URL
        
    def collect_data(self, region: str, date_range: tuple) -> pd.DataFrame:
        """Recopila datos de competitividad turística de Exceltur"""
        try:
            # Datos de competitividad turística
            competitiveness_data = self._get_competitiveness_data(region, date_range)
            
            # Datos económicos y sociales
            economic_data = self._get_economic_impact_data(region, date_range)
            
            # Combinar datos
            combined_data = pd.merge(competitiveness_data, economic_data, on=['region', 'date'], how='outer')
            combined_data['source'] = 'Exceltur'
            combined_data['collection_timestamp'] = datetime.now()
            
            self.save_data(combined_data, 'exceltur_data')
            return combined_data
            
        except Exception as e:
            logger.error(f"Error recopilando datos Exceltur para {region}: {str(e)}")
            return pd.DataFrame()
    
    def _get_competitiveness_data(self, region: str, date_range: tuple) -> pd.DataFrame:
        """Obtiene datos del índice de competitividad turística"""
        dates = pd.date_range(start=date_range[0], end=date_range[1], freq='M')
        
        data = []
        for date in dates:
            # Índice base de competitividad (0-100)
            base_index = 72.5
            improvement = 0.5 * (date.year - 2020)  # Mejora gradual
            seasonal_adj = 2.0 if date.month in [5, 6, 7, 8, 9] else -1.0
            random_factor = (hash(f"{region}{date}") % 10 - 5) / 2
            
            competitiveness_index = base_index + improvement + seasonal_adj + random_factor
            competitiveness_index = max(0, min(100, competitiveness_index))
            
            data.append({
                'region': region,
                'date': date,
                'tourism_competitiveness_index': round(competitiveness_index, 2),
                'infrastructure_score': round(competitiveness_index * 0.95, 2),
                'accessibility_score': round(competitiveness_index * 1.05, 2),
                'sustainability_score': round(competitiveness_index * 0.88, 2)
            })
        
        return pd.DataFrame(data)
    
    def _get_economic_impact_data(self, region: str, date_range: tuple) -> pd.DataFrame:
        """Obtiene datos de impacto económico y social"""
        dates = pd.date_range(start=date_range[0], end=date_range[1], freq='M')
        
        data = []
        for date in dates:
            base_gdp_contribution = 8.5  # % PIB
            growth = 0.2 * (date.year - 2020)
            
            data.append({
                'region': region,
                'date': date,
                'gdp_tourism_contribution': round(base_gdp_contribution + growth, 2),
                'tourism_revenue_millions': round(2500 + growth * 100 + (hash(f"{region}{date}") % 500), 2),
                'performance_economic_social_benefit': round(75 + growth * 2, 2)
            })
        
        return pd.DataFrame(data)

class DataCollectionOrchestrator:
    """Orquestador principal para la recolección de datos"""
    
    def __init__(self):
        self.collectors = {
            'ine': INEDataCollector(),
            'tripadvisor': TripAdvisorDataCollector(),
            'exceltur': ExcelturDataCollector()
        }
        
    def collect_all_data(self, regions: List[str] = None, 
                        date_range: tuple = None) -> Dict[str, pd.DataFrame]:
        """Recopila datos de todas las fuentes para todas las regiones"""
        
        if regions is None:
            regions = Config.REGIONS
            
        if date_range is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # Último año
            date_range = (start_date, end_date)
        
        logger.info(f"Iniciando recolección de datos para {len(regions)} regiones")
        
        all_data = {}
        
        for region in regions:
            logger.info(f"Recopilando datos para {region}")
            region_data = {}
            
            for source, collector in self.collectors.items():
                try:
                    data = collector.collect_data(region, date_range)
                    region_data[source] = data
                    logger.info(f"Datos de {source} recopilados para {region}: {len(data)} registros")
                except Exception as e:
                    logger.error(f"Error recopilando datos de {source} para {region}: {str(e)}")
                    region_data[source] = pd.DataFrame()
            
            all_data[region] = region_data
            
            # Pequeña pausa para evitar sobrecargar las APIs
            time.sleep(1)
        
        # Crear dataset integrado
        integrated_data = self._create_integrated_dataset(all_data)
        return integrated_data
    
    def _create_integrated_dataset(self, all_data: Dict[str, Dict[str, pd.DataFrame]]) -> pd.DataFrame:
        """Crea un dataset integrado combinando todas las fuentes"""
        integrated_records = []
        
        for region, sources_data in all_data.items():
            # Obtener todas las fechas únicas
            all_dates = set()
            for df in sources_data.values():
                if not df.empty and 'date' in df.columns:
                    all_dates.update(df['date'].unique())
            
            all_dates = sorted(all_dates)
            
            for date in all_dates:
                record = {
                    'region': region,
                    'date': date,
                    'collection_timestamp': datetime.now()
                }
                
                # Integrar datos de INE
                ine_data = sources_data.get('ine', pd.DataFrame())
                if not ine_data.empty:
                    ine_row = ine_data[ine_data['date'] == date]
                    if not ine_row.empty:
                        record.update({
                            'room_occupancy_rate': ine_row.iloc[0].get('room_occupancy_rate', None),
                            'tourism_employment': ine_row.iloc[0].get('tourism_employment', None),
                            'total_establishments': ine_row.iloc[0].get('total_establishments', None)
                        })
                
                # Integrar datos de TripAdvisor
                ta_data = sources_data.get('tripadvisor', pd.DataFrame())
                if not ta_data.empty:
                    ta_row = ta_data[ta_data['date'] == date]
                    if not ta_row.empty:
                        record.update({
                            'current_rank': ta_row.iloc[0].get('current_rank', None),
                            'average_rating': ta_row.iloc[0].get('average_rating', None),
                            'total_reviews': ta_row.iloc[0].get('total_reviews', None),
                            'total_facilities': ta_row.iloc[0].get('total_facilities', None)
                        })
                
                # Integrar datos de Exceltur
                ex_data = sources_data.get('exceltur', pd.DataFrame())
                if not ex_data.empty:
                    ex_row = ex_data[ex_data['date'] == date]
                    if not ex_row.empty:
                        record.update({
                            'tourism_competitiveness_index': ex_row.iloc[0].get('tourism_competitiveness_index', None),
                            'performance_economic_social_benefit': ex_row.iloc[0].get('performance_economic_social_benefit', None)
                        })
                
                integrated_records.append(record)
        
        integrated_df = pd.DataFrame(integrated_records)
        
        # Guardar dataset integrado
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tourism_data.db')
        with sqlite3.connect(db_path) as conn:
            integrated_df.to_sql('integrated_data', conn, if_exists='replace', index=False)
        
        logger.info(f"Dataset integrado creado: {len(integrated_df)} registros")
        return integrated_df

def main():
    """Función principal para ejecutar la recolección de datos"""
    orchestrator = DataCollectionOrchestrator()
    
    # Recopilar datos para algunas regiones de prueba
    test_regions = ['Andalucía', 'Cataluña', 'Madrid']
    
    integrated_data = orchestrator.collect_all_data(regions=test_regions)
    
    print(f"Recolección completada. Total de registros: {len(integrated_data)}")
    print("\nPrimeros 5 registros:")
    print(integrated_data.head())

if __name__ == "__main__":
    main()
