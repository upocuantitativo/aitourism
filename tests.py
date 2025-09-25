"""
Tests for Smart Tourism Management System
Suite de pruebas para validar el funcionamiento del sistema
"""

import unittest
import pandas as pd
import numpy as np
import os
import sys
import tempfile
import sqlite3
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from data_collectors.data_collectors import DataCollectionOrchestrator, INEDataCollector, TripAdvisorDataCollector, ExcelturDataCollector
from models.pls_sem_analyzer import PLSSEMAnalyzer
from agents.ai_agents import AgentOrchestrator, LocalAnalysisAgent, ClaudeAnalysisAgent
from utils import DataValidator, DatabaseManager, ReportGenerator, SystemMonitor

class TestDataCollectors(unittest.TestCase):
    """Tests para recolectores de datos"""
    
    def setUp(self):
        """Configuración inicial para tests"""
        self.test_region = "Test_Region"
        self.test_date_range = (datetime.now() - timedelta(days=30), datetime.now())
    
    def test_ine_data_collector(self):
        """Test del recolector INE"""
        collector = INEDataCollector()
        data = collector.collect_data(self.test_region, self.test_date_range)
        
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        self.assertIn('room_occupancy_rate', data.columns)
        self.assertIn('tourism_employment', data.columns)
        self.assertEqual(data['region'].iloc[0], self.test_region)
    
    def test_tripadvisor_data_collector(self):
        """Test del recolector TripAdvisor"""
        collector = TripAdvisorDataCollector()
        data = collector.collect_data(self.test_region, self.test_date_range)
        
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        self.assertIn('average_rating', data.columns)
        self.assertIn('total_reviews', data.columns)
        self.assertIn('current_rank', data.columns)
    
    def test_exceltur_data_collector(self):
        """Test del recolector Exceltur"""
        collector = ExcelturDataCollector()
        data = collector.collect_data(self.test_region, self.test_date_range)
        
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        self.assertIn('tourism_competitiveness_index', data.columns)
        self.assertIn('performance_economic_social_benefit', data.columns)
    
    def test_data_collection_orchestrator(self):
        """Test del orquestador de recolección"""
        orchestrator = DataCollectionOrchestrator()
        regions = [self.test_region]
        
        integrated_data = orchestrator.collect_all_data(regions=regions, date_range=self.test_date_range)
        
        self.assertIsInstance(integrated_data, pd.DataFrame)
        self.assertFalse(integrated_data.empty)
        self.assertEqual(integrated_data['region'].iloc[0], self.test_region)

class TestPLSSEMAnalyzer(unittest.TestCase):
    """Tests para analizador PLS-SEM"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear datos de prueba
        np.random.seed(42)
        n_samples = 120
        
        self.test_data = pd.DataFrame({
            'region': ['Test_Region'] * n_samples,
            'date': pd.date_range(start='2023-01-01', periods=n_samples, freq='D'),
            'room_occupancy_rate': np.random.normal(65, 10, n_samples),
            'tourism_employment': np.random.normal(45000, 5000, n_samples),
            'tourism_competitiveness_index': np.random.normal(75, 8, n_samples),
            'current_rank': np.random.randint(1, 101, n_samples),
            'total_reviews': np.random.normal(5000, 1000, n_samples),
            'total_facilities': np.random.normal(850, 100, n_samples),
            'performance_economic_social_benefit': np.random.normal(78, 6, n_samples)
        })
        
        self.analyzer = PLSSEMAnalyzer()
    
    def test_data_preparation(self):
        """Test de preparación de datos"""
        latent_data = self.analyzer.prepare_data(self.test_data)
        
        self.assertIsInstance(latent_data, dict)
        self.assertIn('Tourism_Competitiveness', latent_data)
        self.assertIn('Satisfaction', latent_data)
        self.assertIn('Tourism_Employment', latent_data)
        
        # Verificar que los datos están normalizados
        for construct, data in latent_data.items():
            self.assertTrue(abs(data.mean().mean()) < 0.1)  # Media cerca de 0
    
    def test_composite_scores_calculation(self):
        """Test de cálculo de scores compuestos"""
        latent_data = self.analyzer.prepare_data(self.test_data)
        composite_scores = self.analyzer.calculate_composite_scores(latent_data)
        
        self.assertIsInstance(composite_scores, pd.DataFrame)
        self.assertEqual(len(composite_scores), len(self.test_data))
        self.assertIn('Tourism_Competitiveness', composite_scores.columns)
        self.assertIn('Satisfaction', composite_scores.columns)
        self.assertIn('Tourism_Employment', composite_scores.columns)
    
    def test_pls_analysis(self):
        """Test de análisis PLS-SEM"""
        latent_data = self.analyzer.prepare_data(self.test_data)
        composite_scores = self.analyzer.calculate_composite_scores(latent_data)
        results = self.analyzer.run_pls_analysis(composite_scores)
        
        self.assertIsInstance(results, dict)
        self.assertIn('TC_to_Satisfaction', results)
        self.assertIn('TC_to_Employment', results)
        self.assertIn('Satisfaction_to_Employment', results)
        self.assertIn('Complete_Model', results)
        self.assertIn('Effects', results)
        
        # Verificar que los coeficientes están en rango razonable
        for path, stats in results.items():
            if path != 'Effects' and path != 'Complete_Model':
                self.assertIn('coefficient', stats)
                self.assertIn('r_squared', stats)
                self.assertTrue(0 <= stats['r_squared'] <= 1)
    
    def test_reliability_validity(self):
        """Test de confiabilidad y validez"""
        latent_data = self.analyzer.prepare_data(self.test_data)
        composite_scores = self.analyzer.calculate_composite_scores(latent_data)
        reliability = self.analyzer.calculate_reliability_validity(latent_data)
        
        self.assertIsInstance(reliability, dict)
        
        for construct, scores in reliability.items():
            self.assertIn('cronbach_alpha', scores)
            self.assertIn('composite_reliability', scores)
            self.assertIn('average_variance_extracted', scores)
            self.assertIn('discriminant_validity', scores)
            
            # Verificar rangos válidos
            self.assertTrue(-1 <= scores['cronbach_alpha'] <= 1)
            self.assertTrue(0 <= scores['composite_reliability'] <= 1)
            self.assertTrue(0 <= scores['average_variance_extracted'] <= 1)

class TestAIAgents(unittest.TestCase):
    """Tests para agentes de IA"""
    
    def setUp(self):
        """Configuración inicial"""
        np.random.seed(42)
        n_samples = 50
        
        self.test_data = pd.DataFrame({
            'region': ['Test_Region'] * n_samples,
            'date': pd.date_range(start='2024-01-01', periods=n_samples, freq='D'),
            'room_occupancy_rate': np.random.normal(65, 10, n_samples),
            'tourism_employment': np.random.normal(45000, 5000, n_samples),
            'tourism_competitiveness_index': np.random.normal(75, 8, n_samples),
            'average_rating': np.random.normal(4.2, 0.3, n_samples),
            'total_reviews': np.random.normal(5000, 1000, n_samples)
        })
        
        self.test_context = {'region': 'Test_Region'}
    
    def test_local_analysis_agent(self):
        """Test del agente de análisis local"""
        agent = LocalAnalysisAgent()
        result = agent.analyze(self.test_data, self.test_context)
        
        self.assertEqual(result.region, 'Test_Region')
        self.assertEqual(result.analysis_type, 'local_statistical')
        self.assertIsInstance(result.results, dict)
        self.assertIsInstance(result.recommendations, list)
        self.assertTrue(0 <= result.confidence_score <= 1)
        
        # Verificar que hay análisis estadístico
        self.assertIn('room_occupancy_rate', result.results)
        self.assertIn('tourism_employment', result.results)
    
    @patch('requests.post')
    def test_claude_analysis_agent_fallback(self, mock_post):
        """Test del agente Claude con fallback a análisis local"""
        # Simular fallo de API
        mock_post.side_effect = Exception("API Error")
        
        agent = ClaudeAnalysisAgent()
        result = agent.analyze(self.test_data, self.test_context)
        
        self.assertEqual(result.region, 'Test_Region')
        self.assertIsInstance(result.results, dict)
        self.assertIsInstance(result.recommendations, list)
        # El fallback debería tener confianza menor
        self.assertTrue(result.confidence_score < 0.8)
    
    def test_agent_orchestrator(self):
        """Test del orquestador de agentes"""
        orchestrator = AgentOrchestrator()
        
        # Test de inicialización
        self.assertIn('claude', orchestrator.agents)
        self.assertIn('local', orchestrator.agents)
        
        # Test de obtención de resultados (sin datos reales)
        results = orchestrator.get_latest_results('Test_Region', limit=5)
        self.assertIsInstance(results, list)

class TestUtils(unittest.TestCase):
    """Tests para utilidades del sistema"""
    
    def test_data_validator(self):
        """Test del validador de datos"""
        # Datos válidos
        valid_data = pd.DataFrame({
            'region': ['A', 'B', 'C'],
            'value': [100, 200, 300],
            'date': ['2025-01-01', '2025-01-02', '2025-01-03']
        })
        
        validator = DataValidator()
        result = validator.validate_dataframe(valid_data, required_columns=['region', 'value'])
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertTrue(result['quality_score'] > 0.8)
        
        # Datos con problemas
        invalid_data = pd.DataFrame({
            'region': ['A', None, 'C'],
            'value': [100, 200, None]
        })
        
        result = validator.validate_dataframe(invalid_data, required_columns=['region', 'value', 'missing'])
        
        self.assertFalse(result['is_valid'])
        self.assertTrue(len(result['errors']) > 0)
        self.assertTrue(result['quality_score'] < 0.8)
    
    def test_database_manager(self):
        """Test del gestor de base de datos"""
        # Crear base de datos temporal
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name
        
        try:
            # Crear tabla de prueba
            with sqlite3.connect(temp_db_path) as conn:
                conn.execute("""
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    region TEXT,
                    date TEXT,
                    value REAL
                )
                """)
                
                # Insertar datos de prueba
                test_data = [
                    ('Region1', '2025-01-01', 100.0),
                    ('Region2', '2025-01-02', 200.0),
                    ('Region1', '2023-01-01', 50.0)  # Dato antiguo
                ]
                
                conn.executemany(
                    "INSERT INTO test_table (region, date, value) VALUES (?, ?, ?)",
                    test_data
                )
                conn.commit()
            
            # Test del gestor
            db_manager = DatabaseManager(temp_db_path)
            
            # Test de estadísticas
            stats = db_manager.get_table_stats('test_table')
            self.assertEqual(stats['row_count'], 3)
            self.assertEqual(stats['table_name'], 'test_table')
            
            # Test de limpieza de datos antiguos
            deleted = db_manager.clean_old_data('test_table', days_to_keep=365)
            self.assertEqual(deleted, 1)  # Debería eliminar el dato de 2023
            
        finally:
            # Limpiar archivo temporal
            os.unlink(temp_db_path)
    
    def test_system_monitor(self):
        """Test del monitor del sistema"""
        monitor = SystemMonitor()
        
        # Registrar métricas
        monitor.record_metric('test_metric', 0.75)
        monitor.record_metric('test_metric', 0.85)
        monitor.record_metric('another_metric', 100.0)
        
        # Verificar que se registraron
        self.assertIn('test_metric', monitor.metrics)
        self.assertIn('another_metric', monitor.metrics)
        self.assertEqual(len(monitor.metrics['test_metric']), 2)
        
        # Test de salud del sistema
        health = monitor.get_system_health()
        self.assertIn('uptime', health)
        self.assertIn('timestamp', health)

class TestIntegration(unittest.TestCase):
    """Tests de integración del sistema completo"""
    
    def test_end_to_end_workflow(self):
        """Test del flujo completo de extremo a extremo"""
        # 1. Recolección de datos
        orchestrator = DataCollectionOrchestrator()
        test_regions = ["Test_Region"]
        
        integrated_data = orchestrator.collect_all_data(regions=test_regions)
        
        self.assertIsInstance(integrated_data, pd.DataFrame)
        self.assertFalse(integrated_data.empty)
        
        # 2. Análisis PLS-SEM (si hay suficientes datos)
        if len(integrated_data) >= Config.PLS_SEM_CONFIG['min_sample_size']:
            analyzer = PLSSEMAnalyzer()
            
            # Simular datos en memoria en lugar de base de datos
            with patch.object(analyzer, 'load_data', return_value=integrated_data):
                latent_data = analyzer.prepare_data(integrated_data)
                composite_scores = analyzer.calculate_composite_scores(latent_data)
                results = analyzer.run_pls_analysis(composite_scores)
                
                self.assertIsInstance(results, dict)
                self.assertIn('Complete_Model', results)
        
        # 3. Análisis de IA
        ai_orchestrator = AgentOrchestrator()
        local_agent = ai_orchestrator.agents['local']
        
        ai_result = local_agent.analyze(integrated_data, {'region': 'Test_Region'})
        
        self.assertEqual(ai_result.region, 'Test_Region')
        self.assertIsInstance(ai_result.recommendations, list)
    
    def test_config_validation(self):
        """Test de validación de configuración"""
        # Test de configuración válida
        valid_config = {
            'REGIONS': ['Test1', 'Test2'],
            'PLS_SEM_CONFIG': {'min_sample_size': 100},
            'DASHBOARD_CONFIG': {'port': 8050},
            'AGENTS_CONFIG': {'frequency': 3600}
        }
        
        from utils import ConfigManager
        errors = ConfigManager.validate_config(valid_config)
        self.assertEqual(len(errors), 0)
        
        # Test de configuración inválida
        invalid_config = {
            'REGIONS': [],  # Lista vacía
            'PLS_SEM_CONFIG': {'min_sample_size': 10}  # Muy pequeño
        }
        
        errors = ConfigManager.validate_config(invalid_config)
        self.assertTrue(len(errors) > 0)

def run_all_tests():
    """Ejecuta todos los tests"""
    # Crear suite de tests
    test_classes = [
        TestDataCollectors,
        TestPLSSEMAnalyzer,
        TestAIAgents,
        TestUtils,
        TestIntegration
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print(f"\n{'='*60}")
    print(f"RESUMEN DE TESTS")
    print(f"{'='*60}")
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Éxito: {result.wasSuccessful()}")
    
    if result.errors:
        print(f"\nERRORES:")
        for test, error in result.errors:
            print(f"- {test}: {error}")
    
    if result.failures:
        print(f"\nFALLOS:")
        for test, failure in result.failures:
            print(f"- {test}: {failure}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
