"""
Smart Tourism Management System - Configuration
System for automated tourism impact analysis using PLS-SEM and AI agents
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for the Smart Tourism Management System"""
    
    # API Keys (configurar en variables de entorno)
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', 'your_claude_api_key_here')
    TRIPADVISOR_API_KEY = os.getenv('TRIPADVISOR_API_KEY', 'your_tripadvisor_api_key')
    
    # OpenAI como alternativa gratuita (usando modelos locales o API gratuita)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key')
    
    # URLs de fuentes de datos
    INE_BASE_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/"
    EXCELTUR_BASE_URL = "https://www.exceltur.org/observatorio-monitur/"
    
    # Configuración de la base de datos
    DATABASE_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'atourism_db',
        'user': 'atourism_user',
        'password': 'your_password'
    }
    
    # Configuración PLS-SEM
    PLS_SEM_CONFIG = {
        'min_sample_size': 100,
        'bootstrap_samples': 5000,
        'significance_level': 0.05,
        'convergence_criteria': 1e-7
    }
    
    # Regiones de estudio
    REGIONS = [
        'Andalucía', 'Cataluña', 'Madrid', 'Valencia', 'Canarias',
        'Baleares', 'Galicia', 'Castilla y León', 'País Vasco',
        'Castilla-La Mancha', 'Murcia', 'Aragón', 'Extremadura',
        'Asturias', 'Navarra', 'Cantabria', 'La Rioja', 'Ceuta', 'Melilla'
    ]
    
    # Variables del modelo PLS-SEM
    LATENT_VARIABLES = {
        'Tourism_Competitiveness': [
            'performance_economic_social_benefit',
            'room_occupancy_rate',
            'tourism_competitiveness_index'
        ],
        'Satisfaction': [
            'current_rank',
            'reviews',
            'total_facilities'
        ],
        'Tourism_Employment': [
            'tourism_employment'
        ]
    }
    
    # Configuración del dashboard
    DASHBOARD_CONFIG = {
        'host': '0.0.0.0',
        'port': 8050,
        'debug': True,
        'update_interval': 300  # 5 minutos
    }
    
    # Configuración de agentes IA
    AGENTS_CONFIG = {
        'data_collector_frequency': 3600,  # 1 hora
        'analysis_frequency': 7200,       # 2 horas
        'reporting_frequency': 86400,     # 24 horas
        'learning_rate': 0.01,
        'confidence_threshold': 0.8
    }

    @classmethod
    def get_database_url(cls) -> str:
        """Construye la URL de conexión a la base de datos"""
        config = cls.DATABASE_CONFIG
        return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
