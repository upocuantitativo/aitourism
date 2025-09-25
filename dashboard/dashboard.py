"""
Interactive Dashboard for Smart Tourism Management System
Real-time visualization of tourism indicators and PLS-SEM model results
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import sqlite3
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TourismDashboard:
    """Dashboard principal para gestión inteligente del turismo"""
    
    def __init__(self):
        self.app = dash.Dash(__name__, external_stylesheets=[
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
            'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
        ])
        self.setup_layout()
        self.setup_callbacks()
        
    def setup_layout(self):
        """Configura el layout del dashboard"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1([
                    html.I(className="fas fa-chart-line", style={'margin-right': '15px', 'color': '#3498db'}),
                    "Smart Tourism Management System"
                ], className="dashboard-title"),
                html.P("Sistema de Gestión Inteligente del Turismo basado en PLS-SEM e IA", 
                       className="dashboard-subtitle"),
                html.Div([
                    html.Span("Última actualización: ", className="update-label"),
                    html.Span(id="last-update", className="update-time")
                ], className="update-info")
            ], className="header"),
            
            # Control Panel
            html.Div([
                html.Div([
                    html.Label("Seleccionar Región:", className="control-label"),
                    dcc.Dropdown(
                        id="region-selector",
                        options=[{'label': region, 'value': region} for region in Config.REGIONS],
                        value=Config.REGIONS[0],
                        className="control-dropdown"
                    )
                ], className="control-group"),
                
                html.Div([
                    html.Label("Período de Análisis:", className="control-label"),
                    dcc.DatePickerRange(
                        id="date-range-picker",
                        start_date=datetime.now() - timedelta(days=365),
                        end_date=datetime.now(),
                        display_format='YYYY-MM-DD',
                        className="control-datepicker"
                    )
                ], className="control-group"),
                
                html.Div([
                    html.Button([
                        html.I(className="fas fa-sync-alt"),
                        " Actualizar Datos"
                    ], id="update-button", className="btn-primary"),
                    html.Button([
                        html.I(className="fas fa-download"),
                        " Exportar Reporte"
                    ], id="export-button", className="btn-secondary")
                ], className="control-buttons")
            ], className="control-panel"),
            
            # KPI Cards
            html.Div(id="kpi-cards", className="kpi-container"),
            
            # Main Content
            html.Div([
                # PLS-SEM Model Visualization
                html.Div([
                    html.H3([
                        html.I(className="fas fa-project-diagram", style={'margin-right': '10px'}),
                        "Modelo PLS-SEM: Relaciones Causales"
                    ], className="section-title"),
                    dcc.Graph(id="pls-sem-model", className="chart-container")
                ], className="chart-section"),
                
                # Time Series Charts
                html.Div([
                    html.H3([
                        html.I(className="fas fa-chart-line", style={'margin-right': '10px'}),
                        "Evolución Temporal de Indicadores"
                    ], className="section-title"),
                    dcc.Graph(id="time-series-chart", className="chart-container")
                ], className="chart-section"),
                
                # Correlation Matrix
                html.Div([
                    html.H3([
                        html.I(className="fas fa-th", style={'margin-right': '10px'}),
                        "Matriz de Correlaciones"
                    ], className="section-title"),
                    dcc.Graph(id="correlation-matrix", className="chart-container")
                ], className="chart-section")
            ], className="main-content-left"),
            
            # Right Sidebar
            html.Div([
                # AI Insights Panel
                html.Div([
                    html.H3([
                        html.I(className="fas fa-robot", style={'margin-right': '10px'}),
                        "Insights de IA"
                    ], className="section-title"),
                    html.Div(id="ai-insights", className="insights-container")
                ], className="sidebar-section"),
                
                # Recommendations Panel
                html.Div([
                    html.H3([
                        html.I(className="fas fa-lightbulb", style={'margin-right': '10px'}),
                        "Recomendaciones"
                    ], className="section-title"),
                    html.Div(id="recommendations", className="recommendations-container")
                ], className="sidebar-section"),
                
                # Model Performance
                html.Div([
                    html.H3([
                        html.I(className="fas fa-tachometer-alt", style={'margin-right': '10px'}),
                        "Performance del Modelo"
                    ], className="section-title"),
                    html.Div(id="model-performance", className="performance-container")
                ], className="sidebar-section")
            ], className="sidebar"),
            
            # Modal for detailed analysis
            html.Div(id="analysis-modal", className="modal"),
            
            # Interval for auto-updates
            dcc.Interval(
                id="interval-component",
                interval=Config.DASHBOARD_CONFIG['update_interval'] * 1000,  # en milisegundos
                n_intervals=0
            ),
            
            # Store for data caching
            dcc.Store(id="data-store"),
            dcc.Store(id="pls-results-store")
            
        ], className="dashboard-container")
        
        # CSS Styles
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>Smart Tourism Management System</title>
                {%favicon%}
                {%css%}
                <style>
                    /* Dashboard Styles */
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    
                    body { 
                        font-family: 'Inter', sans-serif; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        color: #2c3e50;
                    }
                    
                    .dashboard-container {
                        display: grid;
                        grid-template-columns: 1fr 350px;
                        grid-template-rows: auto auto 1fr;
                        gap: 20px;
                        padding: 20px;
                        min-height: 100vh;
                    }
                    
                    .header {
                        grid-column: 1 / -1;
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        padding: 30px;
                        border-radius: 20px;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                        text-align: center;
                    }
                    
                    .dashboard-title {
                        font-size: 2.5rem;
                        font-weight: 700;
                        color: #2c3e50;
                        margin-bottom: 10px;
                    }
                    
                    .dashboard-subtitle {
                        font-size: 1.1rem;
                        color: #7f8c8d;
                        margin-bottom: 15px;
                    }
                    
                    .update-info {
                        font-size: 0.9rem;
                        color: #95a5a6;
                    }
                    
                    .control-panel {
                        grid-column: 1 / -1;
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        padding: 25px;
                        border-radius: 15px;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                        display: flex;
                        gap: 30px;
                        align-items: end;
                        flex-wrap: wrap;
                    }
                    
                    .control-group {
                        flex: 1;
                        min-width: 200px;
                    }
                    
                    .control-label {
                        display: block;
                        margin-bottom: 8px;
                        font-weight: 600;
                        color: #34495e;
                    }
                    
                    .control-dropdown, .control-datepicker {
                        width: 100%;
                    }
                    
                    .control-buttons {
                        display: flex;
                        gap: 15px;
                    }
                    
                    .btn-primary, .btn-secondary {
                        padding: 12px 24px;
                        border: none;
                        border-radius: 8px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }
                    
                    .btn-primary {
                        background: linear-gradient(135deg, #3498db, #2980b9);
                        color: white;
                    }
                    
                    .btn-secondary {
                        background: linear-gradient(135deg, #95a5a6, #7f8c8d);
                        color: white;
                    }
                    
                    .btn-primary:hover, .btn-secondary:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
                    }
                    
                    .kpi-container {
                        grid-column: 1 / -1;
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 20px;
                        margin-bottom: 20px;
                    }
                    
                    .kpi-card {
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        padding: 25px;
                        border-radius: 15px;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                        text-align: center;
                        transition: transform 0.3s ease;
                    }
                    
                    .kpi-card:hover {
                        transform: translateY(-5px);
                    }
                    
                    .kpi-value {
                        font-size: 2.5rem;
                        font-weight: 700;
                        margin-bottom: 8px;
                    }
                    
                    .kpi-label {
                        font-size: 1rem;
                        color: #7f8c8d;
                        margin-bottom: 10px;
                    }
                    
                    .kpi-trend {
                        font-size: 0.9rem;
                        font-weight: 600;
                        padding: 4px 12px;
                        border-radius: 20px;
                    }
                    
                    .trend-up { background: #d5e8d4; color: #27ae60; }
                    .trend-down { background: #f8d7da; color: #e74c3c; }
                    .trend-stable { background: #e8e8e8; color: #7f8c8d; }
                    
                    .main-content-left {
                        display: flex;
                        flex-direction: column;
                        gap: 20px;
                    }
                    
                    .chart-section {
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        padding: 25px;
                        border-radius: 15px;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                    }
                    
                    .section-title {
                        font-size: 1.4rem;
                        font-weight: 600;
                        color: #2c3e50;
                        margin-bottom: 20px;
                        display: flex;
                        align-items: center;
                    }
                    
                    .chart-container {
                        height: 400px;
                    }
                    
                    .sidebar {
                        display: flex;
                        flex-direction: column;
                        gap: 20px;
                    }
                    
                    .sidebar-section {
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        padding: 25px;
                        border-radius: 15px;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                    }
                    
                    .insights-container, .recommendations-container, .performance-container {
                        max-height: 300px;
                        overflow-y: auto;
                    }
                    
                    .insight-item, .recommendation-item {
                        padding: 15px;
                        margin-bottom: 10px;
                        background: #f8f9fa;
                        border-radius: 8px;
                        border-left: 4px solid #3498db;
                    }
                    
                    .insight-confidence {
                        font-size: 0.8rem;
                        color: #7f8c8d;
                        margin-top: 5px;
                    }
                    
                    .recommendation-priority {
                        display: inline-block;
                        padding: 2px 8px;
                        border-radius: 12px;
                        font-size: 0.7rem;
                        font-weight: 600;
                        margin-bottom: 8px;
                    }
                    
                    .priority-alta { background: #e74c3c; color: white; }
                    .priority-media { background: #f39c12; color: white; }
                    .priority-baja { background: #27ae60; color: white; }
                    
                    .performance-metric {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 12px 0;
                        border-bottom: 1px solid #ecf0f1;
                    }
                    
                    .performance-metric:last-child {
                        border-bottom: none;
                    }
                    
                    .metric-name {
                        font-weight: 600;
                        color: #2c3e50;
                    }
                    
                    .metric-value {
                        font-weight: 700;
                        color: #3498db;
                    }
                    
                    @media (max-width: 1200px) {
                        .dashboard-container {
                            grid-template-columns: 1fr;
                            grid-template-rows: auto auto auto 1fr;
                        }
                        
                        .sidebar {
                            grid-row: 4;
                        }
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
    
    def setup_callbacks(self):
        """Configura los callbacks del dashboard"""
        
        @self.app.callback(
            [Output('data-store', 'data'),
             Output('pls-results-store', 'data'),
             Output('last-update', 'children')],
            [Input('region-selector', 'value'),
             Input('date-range-picker', 'start_date'),
             Input('date-range-picker', 'end_date'),
             Input('update-button', 'n_clicks'),
             Input('interval-component', 'n_intervals')]
        )
        def update_data_store(region, start_date, end_date, n_clicks, n_intervals):
            """Actualiza los datos almacenados"""
            try:
                # Cargar datos de la base de datos
                data = self.load_region_data(region, start_date, end_date)
                
                # Cargar resultados PLS-SEM si existen
                pls_results = self.load_pls_results()
                
                # Timestamp de actualización
                update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                return data.to_dict('records'), pls_results, update_time
                
            except Exception as e:
                logger.error(f"Error actualizando datos: {str(e)}")
                return [], {}, "Error al actualizar"
        
        @self.app.callback(
            Output('kpi-cards', 'children'),
            [Input('data-store', 'data')]
        )
        def update_kpi_cards(data):
            """Actualiza las tarjetas KPI"""
            if not data:
                return html.Div("No hay datos disponibles", className="no-data-message")
            
            df = pd.DataFrame(data)
            if df.empty:
                return html.Div("No hay datos disponibles", className="no-data-message")
            
            # Calcular KPIs
            kpis = []
            
            # Ocupación Hotelera
            if 'room_occupancy_rate' in df.columns:
                current_occupancy = df['room_occupancy_rate'].iloc[-1] if not df['room_occupancy_rate'].empty else 0
                prev_occupancy = df['room_occupancy_rate'].iloc[-2] if len(df) > 1 else current_occupancy
                trend = "up" if current_occupancy > prev_occupancy else "down" if current_occupancy < prev_occupancy else "stable"
                
                kpis.append(
                    html.Div([
                        html.Div(f"{current_occupancy:.1f}%", className="kpi-value", style={'color': '#3498db'}),
                        html.Div("Ocupación Hotelera", className="kpi-label"),
                        html.Div(f"Tendencia {trend}", className=f"kpi-trend trend-{trend}")
                    ], className="kpi-card")
                )
            
            # Empleo Turístico
            if 'tourism_employment' in df.columns:
                current_employment = df['tourism_employment'].iloc[-1] if not df['tourism_employment'].empty else 0
                prev_employment = df['tourism_employment'].iloc[-2] if len(df) > 1 else current_employment
                trend = "up" if current_employment > prev_employment else "down" if current_employment < prev_employment else "stable"
                
                kpis.append(
                    html.Div([
                        html.Div(f"{int(current_employment):,}", className="kpi-value", style={'color': '#27ae60'}),
                        html.Div("Empleo Turístico", className="kpi-label"),
                        html.Div(f"Tendencia {trend}", className=f"kpi-trend trend-{trend}")
                    ], className="kpi-card")
                )
            
            # Competitividad
            if 'tourism_competitiveness_index' in df.columns:
                current_comp = df['tourism_competitiveness_index'].iloc[-1] if not df['tourism_competitiveness_index'].empty else 0
                prev_comp = df['tourism_competitiveness_index'].iloc[-2] if len(df) > 1 else current_comp
                trend = "up" if current_comp > prev_comp else "down" if current_comp < prev_comp else "stable"
                
                kpis.append(
                    html.Div([
                        html.Div(f"{current_comp:.1f}", className="kpi-value", style={'color': '#e74c3c'}),
                        html.Div("Índice Competitividad", className="kpi-label"),
                        html.Div(f"Tendencia {trend}", className=f"kpi-trend trend-{trend}")
                    ], className="kpi-card")
                )
            
            # Satisfacción (Rating promedio)
            if 'average_rating' in df.columns:
                current_rating = df['average_rating'].iloc[-1] if not df['average_rating'].empty else 0
                
                kpis.append(
                    html.Div([
                        html.Div(f"{current_rating:.2f}/5", className="kpi-value", style={'color': '#f39c12'}),
                        html.Div("Satisfacción Promedio", className="kpi-label"),
                        html.Div("★" * int(current_rating), className="kpi-trend", style={'color': '#f39c12'})
                    ], className="kpi-card")
                )
            
            return kpis
        
        @self.app.callback(
            Output('pls-sem-model', 'figure'),
            [Input('pls-results-store', 'data')]
        )
        def update_pls_model(pls_results):
            """Actualiza la visualización del modelo PLS-SEM"""
            
            # Crear diagrama de red del modelo PLS-SEM
            fig = go.Figure()
            
            # Posiciones de los nodos
            positions = {
                'Tourism_Competitiveness': (0, 1),
                'Satisfaction': (1, 1),
                'Tourism_Employment': (0.5, 0)
            }
            
            # Coeficientes del modelo (valores del modelo teórico)
            coefficients = {
                ('Tourism_Competitiveness', 'Satisfaction'): 0.884,
                ('Tourism_Competitiveness', 'Tourism_Employment'): 0.319,
                ('Satisfaction', 'Tourism_Employment'): 0.580
            }
            
            # Si hay resultados reales, usar esos
            if pls_results and 'pls_results' in pls_results:
                real_results = pls_results['pls_results']
                if 'TC_to_Satisfaction' in real_results:
                    coefficients[('Tourism_Competitiveness', 'Satisfaction')] = real_results['TC_to_Satisfaction'].get('coefficient', 0.884)
                if 'TC_to_Employment' in real_results:
                    coefficients[('Tourism_Competitiveness', 'Tourism_Employment')] = real_results['TC_to_Employment'].get('coefficient', 0.319)
                if 'Satisfaction_to_Employment' in real_results:
                    coefficients[('Satisfaction', 'Tourism_Employment')] = real_results['Satisfaction_to_Employment'].get('coefficient', 0.580)
            
            # Dibujar nodos
            for node, (x, y) in positions.items():
                fig.add_trace(go.Scatter(
                    x=[x], y=[y],
                    mode='markers+text',
                    marker=dict(size=80, color='lightblue', line=dict(width=2, color='darkblue')),
                    text=node.replace('_', '<br>'),
                    textposition='middle center',
                    textfont=dict(size=12, color='darkblue'),
                    showlegend=False,
                    hoverinfo='text',
                    hovertext=f"{node}<br>Variable Latente"
                ))
            
            # Dibujar aristas con coeficientes
            for (source, target), coef in coefficients.items():
                x0, y0 = positions[source]
                x1, y1 = positions[target]
                
                # Color basado en la fuerza del coeficiente
                color = 'green' if coef > 0.5 else 'orange' if coef > 0.3 else 'red'
                width = max(2, abs(coef) * 8)
                
                fig.add_trace(go.Scatter(
                    x=[x0, x1], y=[y0, y1],
                    mode='lines',
                    line=dict(width=width, color=color),
                    showlegend=False,
                    hoverinfo='text',
                    hovertext=f"{source} → {target}<br>Coeficiente: {coef:.3f}"
                ))
                
                # Añadir etiqueta del coeficiente
                mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2
                fig.add_trace(go.Scatter(
                    x=[mid_x], y=[mid_y],
                    mode='text',
                    text=f"{coef:.3f}",
                    textfont=dict(size=14, color='darkred'),
                    showlegend=False
                ))
            
            fig.update_layout(
                title="Modelo Estructural PLS-SEM - Competitividad y Empleo Turístico",
                showlegend=False,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=60, l=20, r=20, b=20),
                height=400
            )
            
            return fig
        
        @self.app.callback(
            Output('time-series-chart', 'figure'),
            [Input('data-store', 'data')]
        )
        def update_time_series(data):
            """Actualiza el gráfico de series temporales"""
            if not data:
                return go.Figure().add_annotation(
                    text="No hay datos disponibles",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
            
            df = pd.DataFrame(data)
            if df.empty or 'date' not in df.columns:
                return go.Figure().add_annotation(
                    text="No hay datos temporales disponibles",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
            
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            fig = go.Figure()
            
            # Variables principales del modelo
            variables = [
                ('room_occupancy_rate', 'Ocupación Hotelera (%)', 'blue'),
                ('tourism_employment', 'Empleo Turístico', 'green'),
                ('tourism_competitiveness_index', 'Índice Competitividad', 'red'),
                ('average_rating', 'Rating Promedio', 'orange')
            ]
            
            for var, label, color in variables:
                if var in df.columns:
                    fig.add_trace(go.Scatter(
                        x=df['date'],
                        y=df[var],
                        mode='lines+markers',
                        name=label,
                        line=dict(color=color, width=2),
                        marker=dict(size=4)
                    ))
            
            fig.update_layout(
                title="Evolución Temporal de Indicadores Clave",
                xaxis_title="Fecha",
                yaxis_title="Valor",
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=60, l=60, r=20, b=60),
                height=400
            )
            
            return fig
        
        @self.app.callback(
            Output('correlation-matrix', 'figure'),
            [Input('data-store', 'data')]
        )
        def update_correlation_matrix(data):
            """Actualiza la matriz de correlaciones"""
            if not data:
                return go.Figure().add_annotation(
                    text="No hay datos disponibles",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
            
            df = pd.DataFrame(data)
            if df.empty:
                return go.Figure().add_annotation(
                    text="No hay datos disponibles",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
            
            # Seleccionar variables numéricas clave
            numeric_vars = [
                'room_occupancy_rate', 'tourism_employment', 'tourism_competitiveness_index',
                'average_rating', 'total_reviews', 'total_facilities'
            ]
            
            available_vars = [var for var in numeric_vars if var in df.columns]
            
            if len(available_vars) < 2:
                return go.Figure().add_annotation(
                    text="Insuficientes variables para matriz de correlación",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
            
            corr_matrix = df[available_vars].corr()
            
            # Crear etiquetas más legibles
            labels = {
                'room_occupancy_rate': 'Ocupación<br>Hotelera',
                'tourism_employment': 'Empleo<br>Turístico',
                'tourism_competitiveness_index': 'Competitividad<br>Turística',
                'average_rating': 'Rating<br>Promedio',
                'total_reviews': 'Total<br>Reviews',
                'total_facilities': 'Total<br>Facilidades'
            }
            
            display_labels = [labels.get(var, var) for var in available_vars]
            
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=display_labels,
                y=display_labels,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_matrix.values, 2),
                texttemplate="%{text}",
                textfont={"size": 12},
                colorbar=dict(title="Correlación")
            ))
            
            fig.update_layout(
                title="Matriz de Correlaciones entre Variables Clave",
                margin=dict(t=60, l=80, r=20, b=60),
                height=400
            )
            
            return fig
        
        @self.app.callback(
            Output('ai-insights', 'children'),
            [Input('data-store', 'data'),
             Input('region-selector', 'value')]
        )
        def update_ai_insights(data, region):
            """Actualiza los insights de IA"""
            try:
                # Cargar insights más recientes de la base de datos
                insights = self.load_ai_insights(region)
                
                if not insights:
                    return html.Div([
                        html.I(className="fas fa-info-circle", style={'margin-right': '10px'}),
                        "No hay insights disponibles para esta región."
                    ], style={'color': '#7f8c8d', 'font-style': 'italic'})
                
                insight_elements = []
                for insight in insights[:3]:  # Mostrar solo los 3 más recientes
                    confidence = insight.get('confidence_score', 0.5)
                    confidence_color = '#27ae60' if confidence > 0.7 else '#f39c12' if confidence > 0.5 else '#e74c3c'
                    
                    insight_elements.append(
                        html.Div([
                            html.Div(insight.get('analysis_summary', 'Análisis disponible'), 
                                   style={'margin-bottom': '8px'}),
                            html.Div(f"Confianza: {confidence:.1%}", 
                                   className="insight-confidence",
                                   style={'color': confidence_color})
                        ], className="insight-item")
                    )
                
                return insight_elements
                
            except Exception as e:
                logger.error(f"Error cargando insights: {str(e)}")
                return html.Div("Error cargando insights", style={'color': '#e74c3c'})
        
        @self.app.callback(
            Output('recommendations', 'children'),
            [Input('data-store', 'data'),
             Input('region-selector', 'value')]
        )
        def update_recommendations(data, region):
            """Actualiza las recomendaciones"""
            try:
                # Cargar recomendaciones de la base de datos
                recommendations = self.load_recommendations(region)
                
                if not recommendations:
                    return html.Div([
                        html.I(className="fas fa-lightbulb", style={'margin-right': '10px'}),
                        "No hay recomendaciones disponibles."
                    ], style={'color': '#7f8c8d', 'font-style': 'italic'})
                
                rec_elements = []
                for rec in recommendations[:5]:  # Mostrar solo las 5 más recientes
                    priority = rec.get('priority', 'media')
                    
                    rec_elements.append(
                        html.Div([
                            html.Span(priority.upper(), className=f"recommendation-priority priority-{priority}"),
                            html.Div(rec.get('action', 'Recomendación disponible'),
                                   style={'margin-top': '8px'})
                        ], className="recommendation-item")
                    )
                
                return rec_elements
                
            except Exception as e:
                logger.error(f"Error cargando recomendaciones: {str(e)}")
                return html.Div("Error cargando recomendaciones", style={'color': '#e74c3c'})
        
        @self.app.callback(
            Output('model-performance', 'children'),
            [Input('pls-results-store', 'data')]
        )
        def update_model_performance(pls_results):
            """Actualiza las métricas de performance del modelo"""
            if not pls_results or 'pls_results' not in pls_results:
                return html.Div("No hay métricas de modelo disponibles", 
                              style={'color': '#7f8c8d', 'font-style': 'italic'})
            
            results = pls_results['pls_results']
            metrics = []
            
            # R² del modelo completo
            if 'Complete_Model' in results:
                r2 = results['Complete_Model'].get('r_squared', 0)
                metrics.append(
                    html.Div([
                        html.Span("R² Modelo", className="metric-name"),
                        html.Span(f"{r2:.3f}", className="metric-value")
                    ], className="performance-metric")
                )
            
            # Efectos principales
            if 'Effects' in results:
                effects = results['Effects']
                for effect_name, effect_value in effects.items():
                    display_name = effect_name.replace('_', ' ').title()
                    metrics.append(
                        html.Div([
                            html.Span(display_name, className="metric-name"),
                            html.Span(f"{effect_value:.3f}", className="metric-value")
                        ], className="performance-metric")
                    )
            
            # Confiabilidad de constructos
            if 'reliability_scores' in pls_results:
                reliability = pls_results['reliability_scores']
                for construct, scores in reliability.items():
                    alpha = scores.get('cronbach_alpha', 0)
                    metrics.append(
                        html.Div([
                            html.Span(f"Alpha {construct}", className="metric-name"),
                            html.Span(f"{alpha:.3f}", className="metric-value")
                        ], className="performance-metric")
                    )
            
            return metrics
    
    def load_region_data(self, region: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Carga datos para una región específica"""
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tourism_data.db')
            
            if not os.path.exists(db_path):
                logger.warning(f"Base de datos no encontrada: {db_path}")
                return pd.DataFrame()
            
            with sqlite3.connect(db_path) as conn:
                query = """
                SELECT * FROM integrated_data 
                WHERE region = ? 
                AND date BETWEEN ? AND ?
                ORDER BY date
                """
                data = pd.read_sql_query(query, conn, params=(region, start_date, end_date))
                
            logger.info(f"Datos cargados para {region}: {len(data)} registros")
            return data
            
        except Exception as e:
            logger.error(f"Error cargando datos para {region}: {str(e)}")
            return pd.DataFrame()
    
    def load_pls_results(self) -> Dict:
        """Carga resultados PLS-SEM"""
        try:
            results_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'pls_sem_results.json')
            
            if os.path.exists(results_path):
                with open(results_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("Archivo de resultados PLS-SEM no encontrado")
                return {}
                
        except Exception as e:
            logger.error(f"Error cargando resultados PLS-SEM: {str(e)}")
            return {}
    
    def load_ai_insights(self, region: str) -> List[Dict]:
        """Carga insights de IA para una región"""
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tourism_data.db')
            
            if not os.path.exists(db_path):
                return []
            
            with sqlite3.connect(db_path) as conn:
                query = """
                SELECT * FROM ai_analysis_results 
                WHERE region = ? 
                ORDER BY timestamp DESC 
                LIMIT 5
                """
                cursor = conn.cursor()
                cursor.execute(query, (region,))
                rows = cursor.fetchall()
                
                # Convertir a lista de diccionarios
                columns = [description[0] for description in cursor.description]
                insights = []
                
                for row in rows:
                    insight = dict(zip(columns, row))
                    # Parsear JSON de resultados
                    try:
                        insight['results_parsed'] = json.loads(insight['results'])
                        insight['analysis_summary'] = insight['results_parsed'].get('performance_assessment', 'Análisis disponible')
                    except:
                        insight['analysis_summary'] = 'Análisis disponible'
                    
                    insights.append(insight)
                
                return insights
                
        except Exception as e:
            logger.error(f"Error cargando insights para {region}: {str(e)}")
            return []
    
    def load_recommendations(self, region: str) -> List[Dict]:
        """Carga recomendaciones para una región"""
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tourism_data.db')
            
            if not os.path.exists(db_path):
                return []
            
            with sqlite3.connect(db_path) as conn:
                query = """
                SELECT recommendations FROM ai_analysis_results 
                WHERE region = ? 
                ORDER BY timestamp DESC 
                LIMIT 3
                """
                cursor = conn.cursor()
                cursor.execute(query, (region,))
                rows = cursor.fetchall()
                
                all_recommendations = []
                for row in rows:
                    try:
                        recs = json.loads(row[0])
                        if isinstance(recs, list):
                            for rec in recs:
                                if isinstance(rec, dict):
                                    all_recommendations.append(rec)
                                else:
                                    all_recommendations.append({'action': str(rec), 'priority': 'media'})
                    except:
                        continue
                
                return all_recommendations[:5]  # Máximo 5 recomendaciones
                
        except Exception as e:
            logger.error(f"Error cargando recomendaciones para {region}: {str(e)}")
            return []
    
    def run(self, debug=None, host=None, port=None):
        """Ejecuta el dashboard"""
        config = Config.DASHBOARD_CONFIG
        
        self.app.run_server(
            debug=debug if debug is not None else config['debug'],
            host=host if host is not None else config['host'],
            port=port if port is not None else config['port']
        )

def main():
    """Función principal para ejecutar el dashboard"""
    dashboard = TourismDashboard()
    
    print("Iniciando Smart Tourism Management Dashboard...")
    print(f"Dashboard disponible en: http://localhost:{Config.DASHBOARD_CONFIG['port']}")
    
    dashboard.run()

if __name__ == "__main__":
    main()
