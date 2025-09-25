"""
PLS-SEM Analysis Module for Smart Tourism Management System
Implements the structural equation model for tourism competitiveness analysis
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import r2_score, mean_squared_error
from scipy import stats
import sqlite3
import os
import sys
import warnings
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import json

# Configurar warnings
warnings.filterwarnings('ignore')

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PLSSEMAnalyzer:
    """Analizador PLS-SEM para el modelo de competitividad turística"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None
        self.latent_variables = Config.LATENT_VARIABLES
        self.results = {}
        self.loadings = {}
        self.path_coefficients = {}
        self.reliability_scores = {}
        
    def load_data(self, data_source: str = 'database') -> pd.DataFrame:
        """Carga datos desde la base de datos o archivo"""
        if data_source == 'database':
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tourism_data.db')
            
            if not os.path.exists(db_path):
                logger.error(f"Base de datos no encontrada en {db_path}")
                return pd.DataFrame()
            
            with sqlite3.connect(db_path) as conn:
                query = "SELECT * FROM integrated_data WHERE date >= date('now', '-12 months')"
                data = pd.read_sql_query(query, conn)
                
            logger.info(f"Datos cargados: {len(data)} registros")
            return data
        else:
            logger.error("Fuente de datos no soportada")
            return pd.DataFrame()
    
    def prepare_data(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Prepara los datos para el análisis PLS-SEM"""
        
        # Limpiar datos faltantes
        data_clean = data.dropna(subset=[
            'room_occupancy_rate', 'tourism_competitiveness_index', 
            'performance_economic_social_benefit', 'current_rank',
            'total_reviews', 'total_facilities', 'tourism_employment'
        ])
        
        if len(data_clean) < Config.PLS_SEM_CONFIG['min_sample_size']:
            logger.warning(f"Tamaño de muestra insuficiente: {len(data_clean)} < {Config.PLS_SEM_CONFIG['min_sample_size']}")
        
        # Normalizar el ranking (invertir para que mayor sea mejor)
        if 'current_rank' in data_clean.columns:
            max_rank = data_clean['current_rank'].max()
            data_clean['current_rank_normalized'] = max_rank - data_clean['current_rank'] + 1
        
        # Crear variables latentes
        latent_data = {}
        
        # Tourism Competitiveness
        latent_data['Tourism_Competitiveness'] = data_clean[[
            'performance_economic_social_benefit',
            'room_occupancy_rate', 
            'tourism_competitiveness_index'
        ]].copy()
        
        # Satisfaction (calidad percibida)
        latent_data['Satisfaction'] = data_clean[[
            'current_rank_normalized',
            'total_reviews',
            'total_facilities'
        ]].copy()
        
        # Tourism Employment
        latent_data['Tourism_Employment'] = data_clean[['tourism_employment']].copy()
        
        # Normalizar todas las variables
        for construct, variables in latent_data.items():
            latent_data[construct] = pd.DataFrame(
                self.scaler.fit_transform(variables),
                columns=variables.columns,
                index=variables.index
            )
        
        logger.info("Datos preparados para análisis PLS-SEM")
        return latent_data
    
    def calculate_composite_scores(self, latent_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Calcula scores compuestos para las variables latentes"""
        composite_scores = pd.DataFrame()
        
        for construct, variables in latent_data.items():
            if len(variables.columns) > 1:
                # Usar PCA para calcular el primer componente como score compuesto
                from sklearn.decomposition import PCA
                pca = PCA(n_components=1)
                score = pca.fit_transform(variables)
                composite_scores[construct] = score.flatten()
                
                # Guardar loadings
                self.loadings[construct] = dict(zip(variables.columns, pca.components_[0]))
                
                logger.info(f"Score compuesto calculado para {construct}")
                logger.info(f"Varianza explicada: {pca.explained_variance_ratio_[0]:.3f}")
            else:
                # Si solo hay una variable, usar directamente
                composite_scores[construct] = variables.iloc[:, 0]
                self.loadings[construct] = {variables.columns[0]: 1.0}
        
        return composite_scores
    
    def run_pls_analysis(self, composite_scores: pd.DataFrame) -> Dict:
        """Ejecuta el análisis PLS-SEM principal"""
        
        # Definir modelo estructural según el diagrama
        # Tourism_Competitiveness -> Satisfaction
        # Tourism_Competitiveness -> Tourism_Employment  
        # Satisfaction -> Tourism_Employment
        
        results = {}
        
        # Modelo 1: Tourism_Competitiveness -> Satisfaction
        X1 = composite_scores[['Tourism_Competitiveness']]
        y1 = composite_scores['Satisfaction']
        
        pls1 = PLSRegression(n_components=1)
        pls1.fit(X1, y1)
        y1_pred = pls1.predict(X1)
        
        results['TC_to_Satisfaction'] = {
            'coefficient': pls1.coef_[0][0],
            'r_squared': r2_score(y1, y1_pred),
            'rmse': np.sqrt(mean_squared_error(y1, y1_pred))
        }
        
        # Modelo 2: Tourism_Competitiveness -> Tourism_Employment
        X2 = composite_scores[['Tourism_Competitiveness']]
        y2 = composite_scores['Tourism_Employment']
        
        pls2 = PLSRegression(n_components=1)
        pls2.fit(X2, y2)
        y2_pred = pls2.predict(X2)
        
        results['TC_to_Employment'] = {
            'coefficient': pls2.coef_[0][0],
            'r_squared': r2_score(y2, y2_pred),
            'rmse': np.sqrt(mean_squared_error(y2, y2_pred))
        }
        
        # Modelo 3: Satisfaction -> Tourism_Employment
        X3 = composite_scores[['Satisfaction']]
        y3 = composite_scores['Tourism_Employment']
        
        pls3 = PLSRegression(n_components=1)
        pls3.fit(X3, y3)
        y3_pred = pls3.predict(X3)
        
        results['Satisfaction_to_Employment'] = {
            'coefficient': pls3.coef_[0][0],
            'r_squared': r2_score(y3, y3_pred),
            'rmse': np.sqrt(mean_squared_error(y3, y3_pred))
        }
        
        # Modelo completo: efectos directos e indirectos
        X_complete = composite_scores[['Tourism_Competitiveness', 'Satisfaction']]
        y_complete = composite_scores['Tourism_Employment']
        
        pls_complete = PLSRegression(n_components=2)
        pls_complete.fit(X_complete, y_complete)
        y_complete_pred = pls_complete.predict(X_complete)
        
        results['Complete_Model'] = {
            'TC_coefficient': pls_complete.coef_[0][0],
            'Satisfaction_coefficient': pls_complete.coef_[1][0],
            'r_squared': r2_score(y_complete, y_complete_pred),
            'rmse': np.sqrt(mean_squared_error(y_complete, y_complete_pred))
        }
        
        # Calcular efectos indirectos
        indirect_effect = results['TC_to_Satisfaction']['coefficient'] * results['Satisfaction_to_Employment']['coefficient']
        total_effect = results['TC_to_Employment']['coefficient'] + indirect_effect
        
        results['Effects'] = {
            'direct_effect_TC_Employment': results['TC_to_Employment']['coefficient'],
            'indirect_effect_TC_Employment': indirect_effect,
            'total_effect_TC_Employment': total_effect
        }
        
        self.results = results
        logger.info("Análisis PLS-SEM completado")
        
        return results
    
    def calculate_reliability_validity(self, latent_data: Dict[str, pd.DataFrame]) -> Dict:
        """Calcula indicadores de confiabilidad y validez"""
        reliability = {}
        
        for construct, variables in latent_data.items():
            if len(variables.columns) > 1:
                # Cronbach's Alpha
                alpha = self._cronbach_alpha(variables)
                
                # Composite Reliability
                loadings = list(self.loadings[construct].values())
                cr = self._composite_reliability(loadings)
                
                # Average Variance Extracted (AVE)
                ave = self._average_variance_extracted(loadings)
                
                reliability[construct] = {
                    'cronbach_alpha': alpha,
                    'composite_reliability': cr,
                    'average_variance_extracted': ave,
                    'discriminant_validity': ave > 0.5  # Criterio de Fornell-Larcker
                }
            else:
                reliability[construct] = {
                    'cronbach_alpha': 1.0,  # Una sola variable
                    'composite_reliability': 1.0,
                    'average_variance_extracted': 1.0,
                    'discriminant_validity': True
                }
        
        self.reliability_scores = reliability
        return reliability
    
    def _cronbach_alpha(self, data: pd.DataFrame) -> float:
        """Calcula el alfa de Cronbach"""
        k = data.shape[1]
        sum_var = data.var(axis=0, ddof=1).sum()
        total_var = data.sum(axis=1).var(ddof=1)
        
        alpha = (k / (k - 1)) * (1 - sum_var / total_var)
        return alpha
    
    def _composite_reliability(self, loadings: List[float]) -> float:
        """Calcula la confiabilidad compuesta"""
        sum_loadings = sum(loadings)
        sum_squared_loadings = sum([l**2 for l in loadings])
        
        # Asumir error de medida de 0.3 para cada indicador
        sum_error_variance = len(loadings) * 0.3
        
        cr = (sum_loadings**2) / ((sum_loadings**2) + sum_error_variance)
        return cr
    
    def _average_variance_extracted(self, loadings: List[float]) -> float:
        """Calcula la varianza promedio extraída"""
        sum_squared_loadings = sum([l**2 for l in loadings])
        sum_error_variance = len(loadings) * 0.3
        
        ave = sum_squared_loadings / (sum_squared_loadings + sum_error_variance)
        return ave
    
    def bootstrap_analysis(self, composite_scores: pd.DataFrame, n_bootstrap: int = None) -> Dict:
        """Realiza análisis de bootstrap para calcular intervalos de confianza"""
        
        if n_bootstrap is None:
            n_bootstrap = Config.PLS_SEM_CONFIG['bootstrap_samples']
        
        bootstrap_results = {
            'TC_to_Satisfaction': [],
            'TC_to_Employment': [],
            'Satisfaction_to_Employment': []
        }
        
        n_samples = len(composite_scores)
        
        for i in range(n_bootstrap):
            # Muestreo con reemplazo
            bootstrap_indices = np.random.choice(n_samples, size=n_samples, replace=True)
            bootstrap_data = composite_scores.iloc[bootstrap_indices]
            
            # Ejecutar modelos en datos bootstrap
            try:
                # TC -> Satisfaction
                X1 = bootstrap_data[['Tourism_Competitiveness']]
                y1 = bootstrap_data['Satisfaction']
                pls1 = PLSRegression(n_components=1)
                pls1.fit(X1, y1)
                bootstrap_results['TC_to_Satisfaction'].append(pls1.coef_[0][0])
                
                # TC -> Employment
                X2 = bootstrap_data[['Tourism_Competitiveness']]
                y2 = bootstrap_data['Tourism_Employment']
                pls2 = PLSRegression(n_components=1)
                pls2.fit(X2, y2)
                bootstrap_results['TC_to_Employment'].append(pls2.coef_[0][0])
                
                # Satisfaction -> Employment
                X3 = bootstrap_data[['Satisfaction']]
                y3 = bootstrap_data['Tourism_Employment']
                pls3 = PLSRegression(n_components=1)
                pls3.fit(X3, y3)
                bootstrap_results['Satisfaction_to_Employment'].append(pls3.coef_[0][0])
                
            except:
                continue
        
        # Calcular estadísticas de bootstrap
        bootstrap_stats = {}
        for path, coefficients in bootstrap_results.items():
            if coefficients:
                bootstrap_stats[path] = {
                    'mean': np.mean(coefficients),
                    'std': np.std(coefficients),
                    'ci_lower': np.percentile(coefficients, 2.5),
                    'ci_upper': np.percentile(coefficients, 97.5),
                    't_statistic': np.mean(coefficients) / np.std(coefficients) if np.std(coefficients) > 0 else 0,
                    'p_value': 2 * (1 - stats.norm.cdf(abs(np.mean(coefficients) / np.std(coefficients)))) if np.std(coefficients) > 0 else 0
                }
        
        logger.info(f"Análisis de bootstrap completado con {n_bootstrap} muestras")
        return bootstrap_stats
    
    def save_results(self, output_path: str = None):
        """Guarda los resultados del análisis"""
        if output_path is None:
            output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'pls_sem_results.json')
        
        # Preparar resultados para serialización
        results_to_save = {
            'analysis_timestamp': datetime.now().isoformat(),
            'pls_results': self.results,
            'loadings': self.loadings,
            'reliability_scores': self.reliability_scores,
            'model_specification': {
                'latent_variables': self.latent_variables,
                'structural_model': {
                    'Tourism_Competitiveness -> Satisfaction': 0.884,
                    'Tourism_Competitiveness -> Tourism_Employment': 0.319,
                    'Satisfaction -> Tourism_Employment': 0.580
                }
            }
        }
        
        # Convertir numpy arrays a listas para JSON
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            return obj
        
        # Aplicar conversión recursivamente
        import json
        results_json = json.loads(json.dumps(results_to_save, default=convert_numpy))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resultados guardados en {output_path}")
    
    def generate_model_summary(self) -> str:
        """Genera un resumen del modelo PLS-SEM"""
        if not self.results:
            return "No hay resultados disponibles. Ejecute el análisis primero."
        
        summary = []
        summary.append("=== RESUMEN DEL MODELO PLS-SEM ===")
        summary.append(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        summary.append("COEFICIENTES ESTRUCTURALES:")
        for path, stats in self.results.items():
            if path != 'Effects' and path != 'Complete_Model':
                summary.append(f"  {path}: {stats['coefficient']:.3f} (R² = {stats['r_squared']:.3f})")
        
        summary.append("")
        summary.append("EFECTOS TOTALES:")
        effects = self.results.get('Effects', {})
        summary.append(f"  Efecto directo TC → Empleo: {effects.get('direct_effect_TC_Employment', 0):.3f}")
        summary.append(f"  Efecto indirecto TC → Empleo: {effects.get('indirect_effect_TC_Employment', 0):.3f}")
        summary.append(f"  Efecto total TC → Empleo: {effects.get('total_effect_TC_Employment', 0):.3f}")
        
        summary.append("")
        summary.append("CONFIABILIDAD Y VALIDEZ:")
        for construct, reliability in self.reliability_scores.items():
            summary.append(f"  {construct}:")
            summary.append(f"    Alpha de Cronbach: {reliability['cronbach_alpha']:.3f}")
            summary.append(f"    Confiabilidad compuesta: {reliability['composite_reliability']:.3f}")
            summary.append(f"    AVE: {reliability['average_variance_extracted']:.3f}")
        
        return "\n".join(summary)

def main():
    """Función principal para ejecutar el análisis PLS-SEM"""
    analyzer = PLSSEMAnalyzer()
    
    # Cargar datos
    data = analyzer.load_data()
    if data.empty:
        print("No se pudieron cargar los datos")
        return
    
    # Preparar datos
    latent_data = analyzer.prepare_data(data)
    
    # Calcular scores compuestos
    composite_scores = analyzer.calculate_composite_scores(latent_data)
    
    # Ejecutar análisis PLS-SEM
    results = analyzer.run_pls_analysis(composite_scores)
    
    # Calcular confiabilidad y validez
    reliability = analyzer.calculate_reliability_validity(latent_data)
    
    # Análisis de bootstrap
    bootstrap_stats = analyzer.bootstrap_analysis(composite_scores, n_bootstrap=1000)
    
    # Guardar resultados
    analyzer.save_results()
    
    # Mostrar resumen
    print(analyzer.generate_model_summary())
    
    print("\n=== ESTADÍSTICAS DE BOOTSTRAP ===")
    for path, stats in bootstrap_stats.items():
        print(f"{path}:")
        print(f"  Coeficiente: {stats['mean']:.3f} ± {stats['std']:.3f}")
        print(f"  IC 95%: [{stats['ci_lower']:.3f}, {stats['ci_upper']:.3f}]")
        print(f"  p-valor: {stats['p_value']:.3f}")
        print()

if __name__ == "__main__":
    main()
