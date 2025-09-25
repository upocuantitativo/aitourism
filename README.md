# AI Tourism Management System

## Intelligent Tourism Impact Analysis using PLS-SEM and Artificial Intelligence

An innovative automated system that combines empirical analysis using PLS-SEM with adaptive artificial intelligence for automated management of tourism impact on employment.

![Sistema](https://img.shields.io/badge/Sistema-Tourism%20Management-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Dash](https://img.shields.io/badge/Dashboard-Dash-orange)
![AI](https://img.shields.io/badge/AI-Claude%20%2B%20Local-purple)

## 🎯 Key Features

### 📊 Integrated PLS-SEM Model
- **Structural analysis**: Causal relationships between Tourism Competitiveness → Satisfaction → Tourism Employment
- **Statistical validation**: Bootstrap, reliability (Cronbach's α), convergent and discriminant validity
- **Direct and indirect effects**: Complete measurement of tourism policy impact

### 🤖 Automated AI Agents
- **Intelligent analysis**: Agents based on Claude API and local analysis
- **Automatic recommendations**: Generation of insights and adaptive policies
- **Continuous learning**: Feedback system for constant improvement

### 📈 Automatic Data Collection
- **INE**: Hotel occupancy, tourism employment, establishments
- **TripAdvisor**: Ratings, rankings, tourism facilities
- **Exceltur-MONITUR**: Regional tourism competitiveness indices

### 🖥️ Interactive Dashboard & Web Interface
- **Real-time visualization**: KPIs, time series, correlations
- **Visual PLS-SEM model**: Interactive diagram with structural coefficients
- **Regional control panel**: Region selection, periods, report export
- **Interactive HTML Interface**: Four-tab interface (Data, Model, Results, Projection) with sensitivity analysis

## 🏗️ System Architecture

```
├── 📁 data_collectors/      # Automated data collectors
├── 📁 models/              # PLS-SEM analyzer and statistical models
├── 📁 agents/              # AI agents for analysis and recommendations
├── 📁 dashboard/           # Interactive web dashboard
├── 📁 data/               # Database and storage
├── 📁 config/             # System configurations
├── 📁 logs/               # System logs
├── 📁 exports/            # Reports and exports
├── 📄 app.html            # Interactive HTML interface
└── 📄 main.py             # Main system orchestrator
```

## 🌐 Web Interface

The system now includes a comprehensive HTML interface with four main tabs:

### 📊 Data Tab
- Upload tourism data files (Excel, CSV)
- Configure data sources (INE, Exceltur, TripAdvisor)
- Data validation and preprocessing options
- Real-time data preview

### ⚙️ Model Tab
- PLS-SEM model configuration
- AI analysis parameters
- Regional and temporal settings
- Model generation and validation

### 📈 Results Tab (Default)
- Model performance metrics
- Interactive PLS-SEM diagram
- Regional tourism performance charts
- Path coefficients and factor loadings
- Time series analysis and correlation matrices

### 🔮 Projection Tab
- Sensitivity analysis with interactive sliders
- Variable impact controls:
  - Tourism Competitiveness
  - Tourism Satisfaction
  - Economic Environment
  - Marketing Investment
  - Infrastructure Development
  - Environmental Quality
- Real-time projection updates
- Scenario comparison and export

## 🚀 Quick Installation

### ⚡ Solución Inmediata (Si hay errores)

```bash
# Windows - Solución automática
fix_dependencies.bat

# Manual - Dependencias críticas
pip install requests pandas numpy dash plotly schedule psutil

# Verificar y ejecutar
python diagnostics.py --mode quick
python main.py --mode full
```

### 1. Instalación Automática

```bash
# Windows
install_windows.bat

# Linux/Mac
chmod +x install_unix.sh
./install_unix.sh

# Manual
python setup.py --step all
```

### 2. Configurar APIs (Opcional)

Editar el archivo `.env`:

```env
# APIs para análisis avanzado (opcional)
ANTHROPIC_API_KEY=tu_clave_claude_aqui
TRIPADVISOR_API_KEY=tu_clave_tripadvisor_aqui

# Configuración dashboard
DASHBOARD_PORT=8050
DASHBOARD_DEBUG=False
```

### 3. Ejecutar Sistema

```bash
# Sistema completo (recomendado)
python main.py --mode full

# O usar scripts de inicio
# Windows: start_system.bat
# Linux/Mac: ./start_system.sh

# Modo emergencia (si hay problemas)
python emergency_start.py
```

## 📋 Modos de Ejecución

| Comando | Descripción |
|---------|-------------|
| `python main.py --mode init` | Solo inicialización del sistema |
| `python main.py --mode services` | Solo servicios automatizados |
| `python main.py --mode dashboard` | Solo dashboard web |
| `python main.py --mode full` | Sistema completo (recomendado) |
| `python main.py --mode report` | Generar reporte del sistema |

## 🎛️ Configuración del Sistema

### Variables de Entorno (.env)

```env
# API Keys
ANTHROPIC_API_KEY=your_claude_api_key_here
TRIPADVISOR_API_KEY=your_tripadvisor_api_key_here

# Base de datos
DATABASE_URL=sqlite:///data/tourism_data.db

# Dashboard
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8050
DASHBOARD_DEBUG=False

# Configuración del sistema
ENABLE_AUTO_COLLECTION=True
ENABLE_AI_ANALYSIS=True
ENABLE_PLS_ANALYSIS=True
```

### Configuración en config.py

```python
# Regiones de análisis
REGIONS = [
    'Andalucía', 'Cataluña', 'Madrid', 'Valencia', 
    'Canarias', 'Baleares', '...'
]

# Frecuencias de análisis
AGENTS_CONFIG = {
    'data_collector_frequency': 3600,  # 1 hora
    'analysis_frequency': 7200,       # 2 horas  
    'reporting_frequency': 86400,     # 24 horas
}

# Modelo PLS-SEM
PLS_SEM_CONFIG = {
    'min_sample_size': 100,
    'bootstrap_samples': 5000,
    'significance_level': 0.05
}
```

## 📊 Modelo PLS-SEM Implementado

### Variables Latentes

1. **Competitividad Turística**
   - Beneficio económico y social
   - Tasa de ocupación hotelera
   - Índice de competitividad turística

2. **Satisfacción Turística**
   - Ranking actual (normalizado)
   - Total de reseñas
   - Total de facilidades

3. **Empleo Turístico**
   - Empleo turístico directo

### Relaciones Estructurales

```
Competitividad Turística → Satisfacción (β = 0.884)
Competitividad Turística → Empleo Turístico (β = 0.319)
Satisfacción → Empleo Turístico (β = 0.580)
```

### Indicadores de Calidad

- **Confiabilidad**: Cronbach's α, Confiabilidad Compuesta
- **Validez**: Varianza Promedio Extraída (AVE), Validez Discriminante
- **Significancia**: Bootstrap con 5000 muestras, intervalos de confianza 95%

## 🤖 Sistema de Agentes IA

### Agente de Análisis Claude

```python
# Análisis avanzado con Claude API
agent = ClaudeAnalysisAgent()
result = agent.analyze(data, context={'region': 'Andalucía'})

# Resultado estructurado
{
    'performance_assessment': 'evaluación del rendimiento',
    'key_trends': ['tendencia 1', 'tendencia 2'],
    'recommendations': [
        {
            'priority': 'alta',
            'action': 'descripción acción',
            'expected_impact': 'impacto esperado',
            'timeframe': 'corto plazo'
        }
    ],
    'confidence_score': 0.85
}
```

### Agente de Análisis Local

```python
# Análisis estadístico local (sin APIs externas)
local_agent = LocalAnalysisAgent()
result = local_agent.analyze(data, context={'region': 'Cataluña'})

# Características:
# - Análisis de tendencias
# - Detección de anomalías
# - Correlaciones entre variables
# - Recomendaciones basadas en reglas
```

## 📈 Dashboard Interactivo

### Funcionalidades Principales

1. **KPIs en Tiempo Real**
   - Ocupación hotelera actual
   - Empleo turístico
   - Índice de competitividad
   - Satisfacción promedio

2. **Visualizaciones**
   - Modelo PLS-SEM interactivo
   - Series temporales de indicadores
   - Matriz de correlaciones
   - Mapas de calor

3. **Panel de Control**
   - Selector de región
   - Filtros temporales
   - Actualización automática
   - Exportación de reportes

4. **Insights de IA**
   - Análisis automatizado actual
   - Recomendaciones priorizadas
   - Métricas de confianza
   - Performance del modelo

### Acceso al Dashboard

```
URL: http://localhost:8050
Actualización: Cada 5 minutos (configurable)
Regiones: Todas las autonomías españolas
```

## 🔄 Flujo de Trabajo Automatizado

### 1. Recolección de Datos (Cada hora)
```
INE → Ocupación hotelera, empleo, establecimientos
TripAdvisor → Valoraciones, rankings, facilidades  
Exceltur → Competitividad, sostenibilidad
```

### 2. Análisis PLS-SEM (Diario)
```
Preparación de datos → Cálculo de scores compuestos → 
Análisis estructural → Bootstrap validation → 
Guardado de resultados
```

### 3. Análisis IA (Cada 2 horas)
```
Carga de datos regionales → Análisis con Claude/Local →
Generación de insights → Recomendaciones → 
Almacenamiento de resultados
```

### 4. Actualización Dashboard (Cada 5 minutos)
```
Lectura de datos → Cálculo de KPIs →
Actualización de gráficos → Refresh de insights
```

## 🛡️ Seguridad y Robustez

### Manejo de Errores
- **APIs externas**: Fallback automático a análisis local
- **Datos faltantes**: Imputación y validación de calidad
- **Conexiones**: Reintentos automáticos con backoff exponencial

### Monitoreo
- **Logs detallados**: Todos los componentes registran actividad
- **Métricas de calidad**: Confianza de análisis, completitud de datos
- **Alertas**: Notificación de fallos críticos

### Backup y Recovery
- **Base de datos**: Backup automático diario
- **Configuración**: Versionado de configuraciones
- **Resultados**: Exportación automática de análisis

## 📋 API del Sistema

### Endpoints Principales

```python
# Generar reporte regional
system.generate_system_report(region='Andalucía')

# Obtener últimos insights IA  
orchestrator.get_latest_results(region='Madrid', limit=5)

# Ejecutar análisis PLS-SEM manual
analyzer.run_pls_analysis(composite_scores)

# Recopilar datos manuales
collector.collect_all_data(regions=['Valencia'], date_range=(start, end))
```

## 🧪 Testing y Validación

### Tests Automáticos
```bash
# Tests básicos del sistema
python setup.py --step test

# Validación de modelo PLS-SEM
python -m models.pls_sem_analyzer

# Test de recolección de datos
python -m data_collectors.data_collectors

# Test de agentes IA
python -m agents.ai_agents
```

### Validación Manual
```bash
# Verificar funcionamiento completo
python main.py --mode init
python main.py --mode report --region Andalucía
```

## 📚 Documentación Técnica

### Modelo Científico

El sistema implementa el marco teórico desarrollado que integra:

1. **PLS-SEM (Partial Least Squares - Structural Equation Modeling)**
   - Enfoque de varianza para análisis de relaciones causales
   - Adecuado para modelos complejos con variables latentes
   - Robusto ante muestras pequeñas y distribuciones no normales

2. **Inteligencia Artificial Adaptativa**
   - Agentes autónomos para análisis continuo
   - Aprendizaje por retroalimentación de resultados
   - Combinación de análisis local y APIs avanzadas

3. **Gestión Inteligente de Destinos**
   - Automatización de toma de decisiones
   - Recomendaciones basadas en evidencia empírica
   - Sostenibilidad socioeconómica del turismo

### Papers de Referencia

- He et al. (2025): Smart destination management systems
- Mishra et al. (2024): AI applications in tourism analytics
- Del Vecchio et al. (2018): Tourism sustainability frameworks
- Patrichi (2024): Socioeconomic impact of tourism

## 🔧 Troubleshooting

### Problemas Comunes

**Error: Base de datos no encontrada**
```bash
python setup.py --step db  # Recrear base de datos
```

**Error: Dependencias faltantes**
```bash
pip install -r requirements.txt
```

**Error: API de Claude no responde**
```bash
# El sistema usa automáticamente análisis local como fallback
# Verificar .env para configurar API key correctamente
```

**Dashboard no carga**
```bash
# Verificar puerto 8050 disponible
python main.py --mode dashboard --debug
```

### Logs y Diagnóstico

```bash
# Ver logs en tiempo real
tail -f logs/atourism_system.log

# Logs específicos por componente
grep "DataCollector" logs/atourism_system.log
grep "PLSSEMAnalyzer" logs/atourism_system.log
grep "ClaudeAgent" logs/atourism_system.log
```

## 🤝 Contribuciones

### Estructura para Nuevas Funcionalidades

1. **Nuevos Recolectores de Datos**
   ```python
   # Heredar de DataCollector en data_collectors/
   class NuevoRecolector(DataCollector):
       def collect_data(self, region, date_range):
           # Implementar lógica específica
           pass
   ```

2. **Nuevos Agentes IA**
   ```python
   # Heredar de AIAgent en agents/
   class NuevoAgente(AIAgent):
       def analyze(self, data, context):
           # Implementar análisis personalizado
           pass
   ```

3. **Nuevas Visualizaciones**
   ```python
   # Añadir callbacks en dashboard/dashboard.py
   @app.callback(...)
   def nueva_visualizacion(data):
       # Crear gráfico con Plotly
       pass
   ```

## 📄 Licencia

Este proyecto está desarrollado para investigación académica y aplicación práctica en gestión turística regional.

## 📞 Contacto y Soporte

Para consultas sobre implementación, configuración o extensiones del sistema:

- **Documentación técnica**: `/docs` (generada automáticamente)
- **Logs del sistema**: `/logs`  
- **Configuración**: `/config`
- **Datos de ejemplo**: `/data`

---

## 🎯 Resumen Ejecutivo

El **Smart Tourism Management System** representa una solución innovadora que automatiza la gestión del impacto turístico mediante:

✅ **Análisis empírico robusto** con PLS-SEM validado estadísticamente  
✅ **IA adaptativa** para insights y recomendaciones automáticas  
✅ **Recolección de datos en tiempo real** de fuentes oficiales  
✅ **Dashboard interactivo** para visualización y control  
✅ **Sistema autónomo** con mínima intervención manual  

**Expected Impact**: Improvement in regional tourism policy decision-making, optimization of tourism employment, and socioeconomic sustainability of tourism destinations.

---

## 🌐 Quick Start with HTML Interface

To access the new interactive HTML interface:

1. **Open the interface**:
   ```bash
   # Simply open app.html in your web browser
   start app.html  # Windows
   open app.html   # macOS
   xdg-open app.html  # Linux
   ```

2. **Use the tabs**:
   - **Data**: Upload and manage your tourism data
   - **Model**: Configure PLS-SEM parameters and generate models
   - **Results**: View comprehensive analysis results (default tab)
   - **Projection**: Perform sensitivity analysis with interactive controls

The interface is fully self-contained and works offline with sample data for demonstration purposes.
