"""
Diagrama de Flujo Temporal del Smart Tourism Management System
Muestra la secuencia de operaciones y el ciclo de vida del sistema
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
import numpy as np
from datetime import datetime, timedelta

def create_timeline_diagram():
    """Crea un diagrama temporal del funcionamiento del sistema"""
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Configurar el eje
    ax.set_xlim(0, 24)  # 24 horas
    ax.set_ylim(0, 10)
    ax.set_xlabel('Tiempo (Horas)', fontsize=12, fontweight='bold')
    ax.set_title('Smart Tourism System - Ciclo de Operación (24 Horas)', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Definir componentes y sus tiempos de ejecución
    components = {
        'Data Collection': {
            'y': 8,
            'color': '#3498db',
            'executions': list(range(0, 24, 1)),  # Cada hora
            'duration': 0.3,
            'description': 'Recolección de INE, TripAdvisor, Exceltur'
        },
        'Database Update': {
            'y': 7,
            'color': '#2ecc71',
            'executions': list(range(0, 24, 1)),  # Después de cada recolección
            'duration': 0.2,
            'description': 'Actualización de SQLite DB'
        },
        'AI Analysis': {
            'y': 6,
            'color': '#9b59b6',
            'executions': [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22],  # Cada 2 horas
            'duration': 0.5,
            'description': 'Análisis con Claude + Local AI'
        },
        'PLS-SEM Analysis': {
            'y': 5,
            'color': '#e74c3c',
            'executions': [3, 15],  # Dos veces al día
            'duration': 1,
            'description': 'Modelo de Ecuaciones Estructurales'
        },
        'Dashboard Update': {
            'y': 4,
            'color': '#f39c12',
            'executions': [i/12 for i in range(0, 24*12, 1)],  # Cada 5 minutos
            'duration': 0.1,
            'description': 'Actualización del Dashboard Web'
        },
        'Report Generation': {
            'y': 3,
            'color': '#16a085',
            'executions': [6, 12, 18],  # Tres veces al día
            'duration': 0.3,
            'description': 'Generación de Informes'
        }
    }
    
    # Dibujar componentes
    for comp_name, comp_data in components.items():
        y = comp_data['y']
        
        # Etiqueta del componente
        ax.text(-0.5, y, comp_name, fontsize=10, fontweight='bold', 
                ha='right', va='center')
        
        # Línea base
        ax.plot([0, 24], [y, y], 'k-', alpha=0.2, linewidth=1)
        
        # Dibujar ejecuciones
        for exec_time in comp_data['executions']:
            if exec_time <= 24:
                rect = Rectangle((exec_time, y - 0.2), 
                               comp_data['duration'], 0.4,
                               facecolor=comp_data['color'],
                               edgecolor='none',
                               alpha=0.8)
                ax.add_patch(rect)
        
        # Descripción
        ax.text(24.5, y, comp_data['description'], fontsize=8, 
                va='center', style='italic', color='gray')
    
    # Añadir flechas de dependencia
    arrow_props = dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', 
                      color='gray', alpha=0.5, linewidth=1.5)
    
    # Data Collection → Database Update
    for hour in range(0, 24):
        ax.annotate('', xy=(hour + 0.2, 7.2), xytext=(hour + 0.15, 7.8),
                   arrowprops=arrow_props)
    
    # Database → AI Analysis (cada 2 horas)
    for hour in [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]:
        ax.annotate('', xy=(hour + 0.1, 6.2), xytext=(hour + 0.1, 6.8),
                   arrowprops=arrow_props)
    
    # Database → PLS-SEM
    for hour in [3, 15]:
        ax.annotate('', xy=(hour, 5.2), xytext=(hour, 6.8),
                   arrowprops=arrow_props)
    
    # Añadir leyenda de colores
    legend_elements = [
        mpatches.Patch(color='#3498db', label='Fuentes de Datos'),
        mpatches.Patch(color='#2ecc71', label='Almacenamiento'),
        mpatches.Patch(color='#9b59b6', label='Inteligencia Artificial'),
        mpatches.Patch(color='#e74c3c', label='Análisis Estadístico'),
        mpatches.Patch(color='#f39c12', label='Interfaces'),
        mpatches.Patch(color='#16a085', label='Reportes')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9)
    
    # Añadir líneas verticales para marcar horas importantes
    important_hours = [0, 6, 12, 18]
    for hour in important_hours:
        ax.axvline(x=hour, color='red', linestyle='--', alpha=0.3)
        ax.text(hour, 9.5, f'{hour}:00', ha='center', fontsize=9, 
               color='red', fontweight='bold')
    
    # Configurar el grid
    ax.grid(True, axis='x', alpha=0.3, linestyle=':', linewidth=0.5)
    ax.set_xticks(range(0, 25, 2))
    ax.set_xticklabels([f'{h}:00' for h in range(0, 25, 2)], rotation=45)
    
    # Eliminar spines innecesarios
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_yticks([])
    
    # Añadir anotaciones informativas
    info_text = """
    Frecuencias de Actualización:
    • Recolección de Datos: Cada hora (24 veces/día)
    • Análisis IA: Cada 2 horas (12 veces/día)
    • Análisis PLS-SEM: 2 veces/día (3:00 y 15:00)
    • Dashboard: Cada 5 minutos (288 veces/día)
    • Reportes: 3 veces/día (6:00, 12:00, 18:00)
    """
    
    ax.text(1, 1.5, info_text, fontsize=9, 
           bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8),
           verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig('smart_tourism_timeline.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_data_flow_diagram():
    """Crea un diagrama del flujo de datos a través del sistema"""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Título
    ax.text(5, 9.5, 'Flujo de Datos - Smart Tourism System', 
           fontsize=18, fontweight='bold', ha='center')
    
    # Definir cajas y sus posiciones
    boxes = {
        'External Sources': {
            'pos': (1, 7),
            'size': (1.8, 2),
            'color': '#3498db',
            'items': ['INE API', 'TripAdvisor', 'Exceltur', 'Excel Import']
        },
        'Data Collection': {
            'pos': (3.5, 7),
            'size': (1.5, 1.5),
            'color': '#e74c3c',
            'items': ['Collectors', 'Validators', 'Normalizers']
        },
        'Database': {
            'pos': (5.5, 7),
            'size': (1.5, 1.5),
            'color': '#2ecc71',
            'items': ['SQLite', 'Tables', 'Indexes']
        },
        'Analytics': {
            'pos': (4.5, 4.5),
            'size': (3, 1.5),
            'color': '#9b59b6',
            'items': ['PLS-SEM Model', 'AI Agents', 'Statistics']
        },
        'Outputs': {
            'pos': (4.5, 2),
            'size': (4, 1.5),
            'color': '#f39c12',
            'items': ['Dashboard', 'Reports', 'API', 'Alerts']
        }
    }
    
    # Dibujar cajas
    for box_name, box_data in boxes.items():
        x, y = box_data['pos']
        w, h = box_data['size']
        
        # Caja principal
        fancy_box = FancyBboxPatch((x-w/2, y-h/2), w, h,
                                  boxstyle="round,pad=0.1",
                                  facecolor=box_data['color'],
                                  edgecolor='black',
                                  alpha=0.7,
                                  linewidth=2)
        ax.add_patch(fancy_box)
        
        # Título de la caja
        ax.text(x, y+h/2-0.2, box_name, fontsize=12, fontweight='bold',
               ha='center', va='top', color='white')
        
        # Items dentro de la caja
        for i, item in enumerate(box_data['items']):
            ax.text(x, y+h/2-0.5-i*0.3, f'• {item}', fontsize=9,
                   ha='center', va='top', color='white')
    
    # Dibujar flechas
    arrows = [
        # External → Collection
        {'start': (1.9, 7), 'end': (2.75, 7), 'label': 'Raw Data'},
        # Collection → Database
        {'start': (4.25, 7), 'end': (4.75, 7), 'label': 'Cleaned'},
        # Database → Analytics
        {'start': (5.5, 6.25), 'end': (5.5, 5.25), 'label': 'Query'},
        # Analytics → Outputs
        {'start': (4.5, 3.75), 'end': (4.5, 2.75), 'label': 'Results'},
        # Feedback loop
        {'start': (3, 2), 'end': (3, 6.25), 'label': 'Feedback', 'curved': True}
    ]
    
    for arrow in arrows:
        if arrow.get('curved', False):
            arrow_patch = FancyArrowPatch(arrow['start'], arrow['end'],
                                        connectionstyle="arc3,rad=-.3",
                                        arrowstyle='-|>',
                                        mutation_scale=20,
                                        linewidth=2,
                                        color='gray')
        else:
            arrow_patch = FancyArrowPatch(arrow['start'], arrow['end'],
                                        arrowstyle='-|>',
                                        mutation_scale=20,
                                        linewidth=2,
                                        color='gray')
        ax.add_patch(arrow_patch)
        
        # Etiqueta de la flecha
        mid_x = (arrow['start'][0] + arrow['end'][0]) / 2
        mid_y = (arrow['start'][1] + arrow['end'][1]) / 2
        ax.text(mid_x, mid_y, arrow['label'], fontsize=9,
               ha='center', va='bottom', color='gray',
               bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
    
    # Añadir métricas clave
    metrics_text = """
    Métricas del Sistema:
    • Datos procesados: ~50,000 registros/día
    • Regiones monitoreadas: 19
    • Tiempo de actualización: 5 min
    • Precisión del modelo: >85%
    """
    
    ax.text(8.5, 7, metrics_text, fontsize=10,
           bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8),
           verticalalignment='top')
    
    # Añadir variables del modelo PLS-SEM
    model_vars = """
    Variables del Modelo:
    
    Latentes:
    • Competitividad Turística
    • Satisfacción
    • Empleo Turístico
    
    Observadas:
    • Ocupación hotelera
    • Rankings/Reviews
    • Índices económicos
    """
    
    ax.text(0.5, 3.5, model_vars, fontsize=9,
           bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
           verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig('smart_tourism_dataflow.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Genera todos los diagramas del sistema"""
    print("📊 Generando diagramas del Smart Tourism System...")
    
    # Diagrama temporal
    print("⏰ Creando diagrama temporal...")
    create_timeline_diagram()
    
    # Diagrama de flujo de datos
    print("🔄 Creando diagrama de flujo de datos...")
    create_data_flow_diagram()
    
    print("\n✅ Diagramas generados:")
    print("   - smart_tourism_timeline.png")
    print("   - smart_tourism_dataflow.png")
    
    # Resumen del funcionamiento
    print("\n📋 RESUMEN DEL FUNCIONAMIENTO:")
    print("=" * 50)
    print("""
    1. RECOLECCIÓN AUTOMÁTICA (Cada hora):
       - INE: Datos de ocupación hotelera y empleo
       - TripAdvisor: Reviews y rankings turísticos
       - Exceltur: Índices de competitividad regional
       - Excel: Importación manual de datos externos
    
    2. PROCESAMIENTO Y ALMACENAMIENTO:
       - Validación y normalización de datos
       - Integración en base de datos SQLite
       - Indexación para consultas rápidas
    
    3. ANÁLISIS INTELIGENTE:
       - PLS-SEM: Modelo causal (2 veces/día)
       - IA Agents: Insights y recomendaciones (12 veces/día)
       - Estadísticas: Métricas en tiempo real
    
    4. VISUALIZACIÓN Y REPORTES:
       - Dashboard web interactivo (actualizaciones cada 5 min)
       - Generación automática de informes (3 veces/día)
       - API para consultas programáticas
    
    5. RETROALIMENTACIÓN:
       - Ajuste automático de parámetros
       - Aprendizaje continuo del sistema
       - Mejora de precisión con el tiempo
    """)

if __name__ == "__main__":
    main()
