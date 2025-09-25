"""
AI Agents System for Smart Tourism Management
Automated analysis, insights generation, and policy recommendations
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import sqlite3
from abc import ABC, abstractmethod
import requests
import asyncio
from dataclasses import dataclass
import threading
from queue import Queue

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Estructura para resultados de análisis"""
    region: str
    analysis_type: str
    timestamp: datetime
    results: Dict[str, Any]
    confidence_score: float
    recommendations: List[str]

class AIAgent(ABC):
    """Clase base abstracta para agentes IA"""
    
    def __init__(self, name: str, api_key: str = None):
        self.name = name
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        self.last_execution = None
        self.execution_history = []
        
    @abstractmethod
    def analyze(self, data: pd.DataFrame, context: Dict = None) -> AnalysisResult:
        """Método abstracto para análisis"""
        pass
    
    def log_execution(self, result: AnalysisResult):
        """Registra la ejecución del agente"""
        self.last_execution = datetime.now()
        self.execution_history.append({
            'timestamp': self.last_execution,
            'region': result.region,
            'confidence': result.confidence_score,
            'recommendations_count': len(result.recommendations)
        })
        
        # Mantener solo los últimos 100 registros
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]

class ClaudeAnalysisAgent(AIAgent):
    """Agente que usa la API de Claude para análisis avanzado"""
    
    def __init__(self):
        super().__init__("Claude_Analysis_Agent")
        self.api_url = "https://api.anthropic.com/v1/messages"
        
    def analyze(self, data: pd.DataFrame, context: Dict = None) -> AnalysisResult:
        """Realiza análisis usando Claude API"""
        try:
            # Preparar datos para el análisis
            data_summary = self._prepare_data_summary(data, context)
            
            # Crear prompt para Claude
            prompt = self._create_analysis_prompt(data_summary, context)
            
            # Llamar a la API de Claude
            response = self._call_claude_api(prompt)
            
            # Procesar respuesta
            analysis_result = self._process_claude_response(response, context)
            
            self.log_execution(analysis_result)
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error en análisis de Claude: {str(e)}")
            return self._create_fallback_result(data, context)
    
    def _prepare_data_summary(self, data: pd.DataFrame, context: Dict) -> Dict:
        """Prepara resumen de datos para análisis"""
        if data.empty:
            return {"error": "No data available"}
        
        region = context.get('region', 'Unknown') if context else 'Unknown'
        
        # Calcular estadísticas clave
        recent_data = data.tail(12)  # Últimos 12 meses
        
        summary = {
            'region': region,
            'period': f"{recent_data['date'].min()} to {recent_data['date'].max()}",
            'sample_size': len(recent_data),
            'metrics': {}
        }
        
        # Métricas clave
        key_metrics = [
            'room_occupancy_rate', 'tourism_employment', 'tourism_competitiveness_index',
            'average_rating', 'total_reviews', 'total_facilities'
        ]
        
        for metric in key_metrics:
            if metric in recent_data.columns:
                summary['metrics'][metric] = {
                    'current': float(recent_data[metric].iloc[-1]) if not pd.isna(recent_data[metric].iloc[-1]) else None,
                    'average': float(recent_data[metric].mean()),
                    'trend': float(recent_data[metric].pct_change().mean() * 100),  # Tendencia en %
                    'volatility': float(recent_data[metric].std())
                }
        
        # Análisis PLS-SEM si está disponible
        if context and 'pls_results' in context:
            summary['pls_sem_results'] = context['pls_results']
        
        return summary
    
    def _create_analysis_prompt(self, data_summary: Dict, context: Dict) -> str:
        """Crea prompt para análisis de Claude"""
        
        region = data_summary.get('region', 'Unknown')
        
        prompt = f"""
        Actúa como un experto analista en turismo y economía regional. Analiza los siguientes datos turísticos para la región de {region} y proporciona insights estratégicos.

        DATOS DISPONIBLES:
        {json.dumps(data_summary, indent=2, ensure_ascii=False)}

        ANÁLISIS REQUERIDO:
        1. Evaluación del rendimiento turístico actual
        2. Identificación de tendencias clave
        3. Análisis de fortalezas y debilidades
        4. Factores de riesgo y oportunidades
        5. Recomendaciones específicas para mejorar el empleo turístico

        CONTEXTO DEL MODELO:
        - Estamos usando un modelo PLS-SEM que relaciona Competitividad Turística → Satisfacción → Empleo Turístico
        - Los coeficientes estructurales típicos son: TC→Satisfacción (0.884), TC→Empleo (0.319), Satisfacción→Empleo (0.580)

        FORMATO DE RESPUESTA:
        Proporciona tu análisis en formato JSON con la siguiente estructura:
        {{
            "performance_assessment": "evaluación general del rendimiento",
            "key_trends": ["tendencia 1", "tendencia 2", "..."],
            "strengths": ["fortaleza 1", "fortaleza 2", "..."],
            "weaknesses": ["debilidad 1", "debilidad 2", "..."],
            "opportunities": ["oportunidad 1", "oportunidad 2", "..."],
            "threats": ["amenaza 1", "amenaza 2", "..."],
            "recommendations": [
                {{
                    "priority": "alta/media/baja",
                    "action": "descripción de la acción",
                    "expected_impact": "impacto esperado",
                    "timeframe": "corto/medio/largo plazo"
                }}
            ],
            "confidence_score": 0.85,
            "next_review_date": "2025-08-20"
        }}

        Asegúrate de que tus recomendaciones sean específicas, accionables y basadas en evidencia.
        """
        
        return prompt
    
    def _call_claude_api(self, prompt: str) -> Dict:
        """Llama a la API de Claude"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error llamando a Claude API: {str(e)}")
            # Fallback a análisis local
            return self._local_analysis_fallback(prompt)
    
    def _local_analysis_fallback(self, prompt: str) -> Dict:
        """Análisis de respaldo cuando la API no está disponible"""
        logger.info("Usando análisis local de respaldo")
        
        # Análisis básico usando reglas heurísticas
        return {
            "content": [
                {
                    "text": json.dumps({
                        "performance_assessment": "Análisis generado localmente - API no disponible",
                        "key_trends": ["Datos procesados localmente", "Tendencias identificadas mediante heurísticas"],
                        "strengths": ["Datos disponibles para análisis", "Sistema funcionando"],
                        "weaknesses": ["API externa no disponible", "Análisis limitado"],
                        "opportunities": ["Implementar análisis local más robusto", "Diversificar fuentes de IA"],
                        "threats": ["Dependencia de APIs externas"],
                        "recommendations": [
                            {
                                "priority": "alta",
                                "action": "Establecer conexión estable con API de IA",
                                "expected_impact": "Mejores análisis automatizados",
                                "timeframe": "corto plazo"
                            }
                        ],
                        "confidence_score": 0.6,
                        "next_review_date": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                    })
                }
            ]
        }
    
    def _process_claude_response(self, response: Dict, context: Dict) -> AnalysisResult:
        """Procesa la respuesta de Claude"""
        try:
            # Extraer contenido de la respuesta
            content = response.get("content", [{}])[0].get("text", "{}")
            
            # Parsear JSON de la respuesta
            analysis_data = json.loads(content)
            
            # Crear resultado estructurado
            result = AnalysisResult(
                region=context.get('region', 'Unknown') if context else 'Unknown',
                analysis_type='claude_comprehensive',
                timestamp=datetime.now(),
                results=analysis_data,
                confidence_score=analysis_data.get('confidence_score', 0.5),
                recommendations=[
                    rec.get('action', 'No action specified') 
                    for rec in analysis_data.get('recommendations', [])
                ]
            )
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando respuesta de Claude: {str(e)}")
            return self._create_fallback_result(pd.DataFrame(), context)
        except Exception as e:
            logger.error(f"Error procesando respuesta de Claude: {str(e)}")
            return self._create_fallback_result(pd.DataFrame(), context)
    
    def _create_fallback_result(self, data: pd.DataFrame, context: Dict) -> AnalysisResult:
        """Crea resultado de respaldo en caso de error"""
        return AnalysisResult(
            region=context.get('region', 'Unknown') if context else 'Unknown',
            analysis_type='fallback_analysis',
            timestamp=datetime.now(),
            results={
                "status": "error",
                "message": "Analysis failed, using fallback"
            },
            confidence_score=0.3,
            recommendations=["Review data quality", "Check API connectivity"]
        )

class LocalAnalysisAgent(AIAgent):
    """Agente de análisis local sin dependencias externas"""
    
    def __init__(self):
        super().__init__("Local_Analysis_Agent")
        
    def analyze(self, data: pd.DataFrame, context: Dict = None) -> AnalysisResult:
        """Realiza análisis usando algoritmos locales"""
        try:
            region = context.get('region', 'Unknown') if context else 'Unknown'
            
            # Análisis estadístico básico
            analysis_results = self._perform_statistical_analysis(data)
            
            # Generar recomendaciones basadas en reglas
            recommendations = self._generate_rule_based_recommendations(analysis_results)
            
            # Calcular score de confianza
            confidence = self._calculate_confidence_score(data, analysis_results)
            
            result = AnalysisResult(
                region=region,
                analysis_type='local_statistical',
                timestamp=datetime.now(),
                results=analysis_results,
                confidence_score=confidence,
                recommendations=recommendations
            )
            
            self.log_execution(result)
            return result
            
        except Exception as e:
            logger.error(f"Error en análisis local: {str(e)}")
            return self._create_empty_result(context)
    
    def _perform_statistical_analysis(self, data: pd.DataFrame) -> Dict:
        """Realiza análisis estadístico de los datos"""
        if data.empty:
            return {"error": "No data available"}
        
        recent_data = data.tail(12)
        analysis = {}
        
        # Análisis de tendencias
        metrics = ['room_occupancy_rate', 'tourism_employment', 'tourism_competitiveness_index']
        
        for metric in metrics:
            if metric in recent_data.columns:
                series = recent_data[metric].dropna()
                if len(series) > 1:
                    # Calcular tendencia lineal
                    x = range(len(series))
                    coeffs = pd.Series(x).corr(series)
                    
                    analysis[metric] = {
                        'current_value': float(series.iloc[-1]),
                        'average': float(series.mean()),
                        'trend_correlation': float(coeffs) if not pd.isna(coeffs) else 0,
                        'volatility': float(series.std()),
                        'trend_direction': 'up' if coeffs > 0.1 else 'down' if coeffs < -0.1 else 'stable'
                    }
        
        # Análisis de correlaciones
        if len(recent_data) > 3:
            numeric_cols = recent_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                correlations = recent_data[numeric_cols].corr()
                analysis['correlations'] = correlations.to_dict()
        
        # Detección de anomalías simples
        anomalies = []
        for metric in metrics:
            if metric in recent_data.columns:
                series = recent_data[metric].dropna()
                if len(series) > 3:
                    mean_val = series.mean()
                    std_val = series.std()
                    current_val = series.iloc[-1]
                    
                    if abs(current_val - mean_val) > 2 * std_val:
                        anomalies.append(f"Anomalía detectada en {metric}: valor actual {current_val:.2f} vs media {mean_val:.2f}")
        
        analysis['anomalies'] = anomalies
        
        return analysis
    
    def _generate_rule_based_recommendations(self, analysis: Dict) -> List[str]:
        """Genera recomendaciones basadas en reglas"""
        recommendations = []
        
        # Reglas basadas en ocupación hotelera
        if 'room_occupancy_rate' in analysis:
            occupancy = analysis['room_occupancy_rate']
            if occupancy['current_value'] < 50:
                recommendations.append("Baja ocupación hotelera detectada. Implementar campañas promocionales.")
            elif occupancy['trend_direction'] == 'down':
                recommendations.append("Tendencia decreciente en ocupación. Revisar estrategias de marketing.")
            elif occupancy['current_value'] > 90:
                recommendations.append("Alta ocupación. Considerar aumentar capacidad hotelera.")
        
        # Reglas basadas en empleo turístico
        if 'tourism_employment' in analysis:
            employment = analysis['tourism_employment']
            if employment['trend_direction'] == 'down':
                recommendations.append("Descenso en empleo turístico. Implementar programas de estímulo sectorial.")
            elif employment['volatility'] > employment['average'] * 0.1:
                recommendations.append("Alta volatilidad en empleo. Establecer políticas de estabilización.")
        
        # Reglas basadas en competitividad
        if 'tourism_competitiveness_index' in analysis:
            competitiveness = analysis['tourism_competitiveness_index']
            if competitiveness['current_value'] < 70:
                recommendations.append("Índice de competitividad bajo. Invertir en infraestructura turística.")
            elif competitiveness['trend_direction'] == 'up':
                recommendations.append("Buena tendencia en competitividad. Mantener y ampliar inversiones.")
        
        # Reglas basadas en anomalías
        if analysis.get('anomalies'):
            recommendations.append("Anomalías detectadas en los datos. Realizar análisis detallado.")
        
        if not recommendations:
            recommendations.append("Mantener monitoreo continuo de indicadores.")
        
        return recommendations
    
    def _calculate_confidence_score(self, data: pd.DataFrame, analysis: Dict) -> float:
        """Calcula score de confianza basado en calidad de datos"""
        if data.empty:
            return 0.0
        
        # Factores que afectan la confianza
        factors = []
        
        # Tamaño de muestra
        sample_size = len(data)
        if sample_size >= 12:
            factors.append(0.3)
        elif sample_size >= 6:
            factors.append(0.2)
        else:
            factors.append(0.1)
        
        # Completitud de datos
        completeness = 1 - data.isnull().sum().sum() / (data.shape[0] * data.shape[1])
        factors.append(completeness * 0.3)
        
        # Consistencia temporal
        if 'date' in data.columns and len(data) > 1:
            date_consistency = 1.0 if data['date'].is_monotonic_increasing else 0.5
            factors.append(date_consistency * 0.2)
        else:
            factors.append(0.1)
        
        # Variabilidad razonable (no datos constantes)
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            variability = min(1.0, data[numeric_cols].std().mean() / data[numeric_cols].mean().mean())
            factors.append(variability * 0.2)
        else:
            factors.append(0.1)
        
        confidence = min(1.0, sum(factors))
        return round(confidence, 2)
    
    def _create_empty_result(self, context: Dict) -> AnalysisResult:
        """Crea resultado vacío en caso de error"""
        return AnalysisResult(
            region=context.get('region', 'Unknown') if context else 'Unknown',
            analysis_type='local_error',
            timestamp=datetime.now(),
            results={"error": "Analysis failed"},
            confidence_score=0.0,
            recommendations=["Check data availability"]
        )

class AgentOrchestrator:
    """Orquestador de agentes IA para análisis automatizado"""
    
    def __init__(self):
        self.agents = {
            'claude': ClaudeAnalysisAgent(),
            'local': LocalAnalysisAgent()
        }
        self.execution_queue = Queue()
        self.results_storage = []
        self.is_running = False
        
    def start_automated_analysis(self, regions: List[str] = None):
        """Inicia el análisis automatizado continuo"""
        if regions is None:
            regions = Config.REGIONS[:5]  # Primeras 5 regiones para prueba
        
        self.is_running = True
        
        # Hilo para procesamiento continuo
        processing_thread = threading.Thread(target=self._continuous_processing, args=(regions,))
        processing_thread.daemon = True
        processing_thread.start()
        
        logger.info(f"Análisis automatizado iniciado para {len(regions)} regiones")
    
    def stop_automated_analysis(self):
        """Detiene el análisis automatizado"""
        self.is_running = False
        logger.info("Análisis automatizado detenido")
    
    def _continuous_processing(self, regions: List[str]):
        """Procesamiento continuo de análisis"""
        while self.is_running:
            try:
                for region in regions:
                    # Cargar datos para la región
                    data = self._load_region_data(region)
                    
                    if not data.empty:
                        # Intentar análisis con Claude primero
                        try:
                            result = self.agents['claude'].analyze(data, {'region': region})
                            if result.confidence_score > 0.5:
                                self._store_result(result)
                            else:
                                # Fallback a análisis local
                                local_result = self.agents['local'].analyze(data, {'region': region})
                                self._store_result(local_result)
                        except:
                            # Análisis local como respaldo
                            local_result = self.agents['local'].analyze(data, {'region': region})
                            self._store_result(local_result)
                    
                    # Pausa entre regiones
                    time.sleep(Config.AGENTS_CONFIG['data_collector_frequency'] / len(regions))
                
                # Pausa entre ciclos completos
                time.sleep(Config.AGENTS_CONFIG['analysis_frequency'])
                
            except Exception as e:
                logger.error(f"Error en procesamiento continuo: {str(e)}")
                time.sleep(60)  # Pausa en caso de error
    
    def _load_region_data(self, region: str) -> pd.DataFrame:
        """Carga datos para una región específica"""
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tourism_data.db')
            
            if not os.path.exists(db_path):
                return pd.DataFrame()
            
            with sqlite3.connect(db_path) as conn:
                query = """
                SELECT * FROM integrated_data 
                WHERE region = ? 
                AND date >= date('now', '-12 months')
                ORDER BY date
                """
                data = pd.read_sql_query(query, conn, params=(region,))
                
            return data
            
        except Exception as e:
            logger.error(f"Error cargando datos para {region}: {str(e)}")
            return pd.DataFrame()
    
    def _store_result(self, result: AnalysisResult):
        """Almacena resultado de análisis"""
        try:
            # Añadir a almacenamiento en memoria
            self.results_storage.append(result)
            
            # Mantener solo los últimos 1000 resultados
            if len(self.results_storage) > 1000:
                self.results_storage = self.results_storage[-1000:]
            
            # Guardar en base de datos
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tourism_data.db')
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Crear tabla si no existe
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT,
                    analysis_type TEXT,
                    timestamp TEXT,
                    results TEXT,
                    confidence_score REAL,
                    recommendations TEXT
                )
                """)
                
                # Insertar resultado
                cursor.execute("""
                INSERT INTO ai_analysis_results 
                (region, analysis_type, timestamp, results, confidence_score, recommendations)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    result.region,
                    result.analysis_type,
                    result.timestamp.isoformat(),
                    json.dumps(result.results),
                    result.confidence_score,
                    json.dumps(result.recommendations)
                ))
                
                conn.commit()
            
            logger.info(f"Resultado almacenado para {result.region} (confianza: {result.confidence_score:.2f})")
            
        except Exception as e:
            logger.error(f"Error almacenando resultado: {str(e)}")
    
    def get_latest_results(self, region: str = None, limit: int = 10) -> List[AnalysisResult]:
        """Obtiene los resultados más recientes"""
        if region:
            results = [r for r in self.results_storage if r.region == region]
        else:
            results = self.results_storage
        
        # Ordenar por timestamp y devolver los más recientes
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:limit]
    
    def generate_regional_report(self, region: str) -> Dict:
        """Genera reporte consolidado para una región"""
        try:
            # Obtener resultados recientes para la región
            recent_results = self.get_latest_results(region, limit=5)
            
            if not recent_results:
                return {"error": f"No hay resultados disponibles para {region}"}
            
            # Consolidar recomendaciones
            all_recommendations = []
            confidence_scores = []
            
            for result in recent_results:
                all_recommendations.extend(result.recommendations)
                confidence_scores.append(result.confidence_score)
            
            # Encontrar recomendaciones más frecuentes
            from collections import Counter
            recommendation_counts = Counter(all_recommendations)
            top_recommendations = recommendation_counts.most_common(5)
            
            report = {
                'region': region,
                'report_date': datetime.now().isoformat(),
                'analysis_period': f"{recent_results[-1].timestamp} to {recent_results[0].timestamp}",
                'average_confidence': sum(confidence_scores) / len(confidence_scores),
                'total_analyses': len(recent_results),
                'top_recommendations': [
                    {'recommendation': rec, 'frequency': count} 
                    for rec, count in top_recommendations
                ],
                'latest_analysis': {
                    'timestamp': recent_results[0].timestamp.isoformat(),
                    'type': recent_results[0].analysis_type,
                    'confidence': recent_results[0].confidence_score,
                    'key_results': recent_results[0].results
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generando reporte para {region}: {str(e)}")
            return {"error": f"Error generando reporte: {str(e)}"}

# Importar numpy para análisis estadístico
import numpy as np

def main():
    """Función principal para prueba del sistema de agentes"""
    orchestrator = AgentOrchestrator()
    
    # Iniciar análisis automatizado para algunas regiones
    test_regions = ['Andalucía', 'Cataluña', 'Madrid']
    orchestrator.start_automated_analysis(test_regions)
    
    # Simular ejecución por un tiempo
    try:
        logger.info("Sistema de agentes IA iniciado. Presiona Ctrl+C para detener.")
        while True:
            time.sleep(60)
            
            # Mostrar estado cada minuto
            for region in test_regions:
                latest_results = orchestrator.get_latest_results(region, limit=1)
                if latest_results:
                    result = latest_results[0]
                    logger.info(f"{region}: Última análisis {result.timestamp.strftime('%H:%M:%S')}, "
                              f"Confianza: {result.confidence_score:.2f}")
    
    except KeyboardInterrupt:
        logger.info("Deteniendo sistema de agentes...")
        orchestrator.stop_automated_analysis()

if __name__ == "__main__":
    main()
