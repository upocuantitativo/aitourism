"""
Visualización del funcionamiento del Smart Tourism Management System
Grafo interactivo que muestra la arquitectura y flujo de datos
"""

import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

class SystemArchitectureGraph:
    """Clase para visualizar la arquitectura del sistema de turismo inteligente"""
    
    def __init__(self):
        self.G = nx.DiGraph()
        self.setup_nodes()
        self.setup_edges()
        self.node_colors = {
            'source': '#3498db',      # Azul - Fuentes de datos
            'processor': '#e74c3c',   # Rojo - Procesamiento
            'storage': '#2ecc71',     # Verde - Almacenamiento
            'interface': '#f39c12',   # Naranja - Interfaces
            'ml': '#9b59b6'          # Púrpura - IA/ML
        }
        
    def setup_nodes(self):
        """Define todos los nodos del sistema"""
        
        # Fuentes de Datos
        self.G.add_node('INE', 
                       label='INE\n(Instituto Nacional\nde Estadística)',
                       type='source',
                       description='Datos de ocupación hotelera, empleo turístico')
        
        self.G.add_node('TripAdvisor',
                       label='TripAdvisor\n(Reviews)',
                       type='source',
                       description='Valoraciones, rankings, facilidades turísticas')
        
        self.G.add_node('Exceltur',
                       label='Exceltur/MONITUR\n(Competitividad)',
                       type='source',
                       description='Índices de competitividad turística regional')
        
        self.G.add_node('Excel',
                       label='data_final.xlsx\n(Importación)',
                       type='source',
                       description='Datos externos importados manualmente')
        
        # Recolectores y Procesamiento
        self.G.add_node('DataCollectors',
                       label='Data Collectors\n(Automatizado)',
                       type='processor',
                       description='Recolección automática cada hora')
        
        self.G.add_node('Orchestrator',
                       label='System Orchestrator\n(main.py)',
                       type='processor',
                       description='Coordinador principal del sistema')
        
        # Almacenamiento
        self.G.add_node('Database',
                       label='SQLite Database\n(tourism_data.db)',
                       type='storage',
                       description='Base de datos con todos los datos integrados')
        
        # Análisis e IA
        self.G.add_node('PLS-SEM',
                       label='PLS-SEM Analyzer\n(Modelo Estadístico)',
                       type='ml',
                       description='Análisis de ecuaciones estructurales')
        
        self.G.add_node('AI-Agents',
                       label='AI Agents\n(Claude + Local)',
                       type='ml',
                       description='Generación de insights y recomendaciones')
        
        # Interfaces de Usuario
        self.G.add_node('Dashboard',
                       label='Dashboard Web\n(localhost:8050)',
                       type='interface',
                       description='Visualización interactiva en tiempo real')
        
        self.G.add_node('Reports',
                       label='Reports & Exports\n(JSON/CSV)',
                       type='interface',
                       description='Generación de informes automatizados')
        
        self.G.add_node('API',
                       label='System API\n(Endpoints)',
                       type='interface',
                       description='API para consultas programáticas')
        
    def setup_edges(self):
        """Define las conexiones entre componentes"""
        
        # Flujo de datos desde fuentes
        self.G.add_edge('INE', 'DataCollectors', 
                       label='Ocupación\nEmpleo',
                       flow_type='data')
        
        self.G.add_edge('TripAdvisor', 'DataCollectors',
                       label='Reviews\nRankings',
                       flow_type='data')
        
        self.G.add_edge('Exceltur', 'DataCollectors',
                       label='Competitividad',
                       flow_type='data')
        
        self.G.add_edge('Excel', 'Database',
                       label='Import directo',
                       flow_type='data')
        
        # Flujo hacia base de datos
        self.G.add_edge('DataCollectors', 'Database',
                       label='Datos\nintegrados',
                       flow_type='data')
        
        # Flujo hacia análisis
        self.G.add_edge('Database', 'PLS-SEM',
                       label='Dataset\ncompleto',
                       flow_type='analysis')
        
        self.G.add_edge('Database', 'AI-Agents',
                       label='Datos\nregionales',
                       flow_type='analysis')
        
        # Control del orquestador
        self.G.add_edge('Orchestrator', 'DataCollectors',
                       label='Control',
                       flow_type='control')
        
        self.G.add_edge('Orchestrator', 'PLS-SEM',
                       label='Ejecutar',
                       flow_type='control')
        
        self.G.add_edge('Orchestrator', 'AI-Agents',
                       label='Activar',
                       flow_type='control')
        
        # Salidas hacia interfaces
        self.G.add_edge('PLS-SEM', 'Dashboard',
                       label='Resultados',
                       flow_type='output')
        
        self.G.add_edge('AI-Agents', 'Dashboard',
                       label='Insights',
                       flow_type='output')
        
        self.G.add_edge('PLS-SEM', 'Reports',
                       label='Análisis',
                       flow_type='output')
        
        self.G.add_edge('AI-Agents', 'Reports',
                       label='Recomendaciones',
                       flow_type='output')
        
        # API connections
        self.G.add_edge('API', 'Database',
                       label='Query',
                       flow_type='api')
        
        self.G.add_edge('API', 'Reports',
                       label='Generate',
                       flow_type='api')
    
    def create_matplotlib_graph(self, title="Smart Tourism System - Arquitectura"):
        """Crea una visualización estática con matplotlib"""
        plt.figure(figsize=(16, 12))
        
        # Layout jerárquico
        pos = nx.spring_layout(self.G, k=3, iterations=50)
        
        # Ajustar posiciones manualmente para mejor visualización
        pos['INE'] = (-2, 2)
        pos['TripAdvisor'] = (-2, 1)
        pos['Exceltur'] = (-2, 0)
        pos['Excel'] = (-2, -1)
        pos['DataCollectors'] = (0, 0.5)
        pos['Database'] = (2, 0)
        pos['Orchestrator'] = (0, 2.5)
        pos['PLS-SEM'] = (4, 1.5)
        pos['AI-Agents'] = (4, -1.5)
        pos['Dashboard'] = (6, 0)
        pos['Reports'] = (6, -2)
        pos['API'] = (6, 2)
        
        # Dibujar nodos por tipo
        for node_type, color in self.node_colors.items():
            node_list = [n for n, d in self.G.nodes(data=True) if d['type'] == node_type]
            nx.draw_networkx_nodes(self.G, pos, 
                                 nodelist=node_list,
                                 node_color=color,
                                 node_size=3000,
                                 alpha=0.9)
        
        # Dibujar etiquetas
        labels = nx.get_node_attributes(self.G, 'label')
        nx.draw_networkx_labels(self.G, pos, labels, 
                              font_size=8, 
                              font_weight='bold')
        
        # Dibujar aristas con diferentes estilos
        edge_styles = {
            'data': {'style': 'solid', 'color': '#34495e', 'width': 2},
            'control': {'style': 'dashed', 'color': '#e74c3c', 'width': 2},
            'analysis': {'style': 'solid', 'color': '#3498db', 'width': 2},
            'output': {'style': 'solid', 'color': '#27ae60', 'width': 2},
            'api': {'style': 'dotted', 'color': '#f39c12', 'width': 2}
        }
        
        for flow_type, style in edge_styles.items():
            edge_list = [(u, v) for u, v, d in self.G.edges(data=True) 
                        if d.get('flow_type') == flow_type]
            nx.draw_networkx_edges(self.G, pos,
                                 edgelist=edge_list,
                                 style=style['style'],
                                 edge_color=style['color'],
                                 width=style['width'],
                                 arrows=True,
                                 arrowsize=20,
                                 arrowstyle='->')
        
        # Título y leyenda
        plt.title(title, fontsize=20, fontweight='bold', pad=20)
        
        # Crear leyenda
        from matplotlib.lines import Line2D
        legend_elements = []
        
        # Leyenda de tipos de nodos
        for node_type, color in self.node_colors.items():
            legend_elements.append(
                Line2D([0], [0], marker='o', color='w', 
                      label=node_type.capitalize(), 
                      markerfacecolor=color, markersize=15)
            )
        
        # Leyenda de tipos de flujo
        legend_elements.append(Line2D([0], [0], color='white', label=''))  # Espaciador
        legend_elements.append(Line2D([0], [0], color='#34495e', linewidth=2, 
                                    label='Flujo de datos'))
        legend_elements.append(Line2D([0], [0], color='#e74c3c', linewidth=2, 
                                    linestyle='dashed', label='Control'))
        legend_elements.append(Line2D([0], [0], color='#3498db', linewidth=2, 
                                    label='Análisis'))
        
        plt.legend(handles=legend_elements, loc='upper left', 
                  bbox_to_anchor=(0, 1), fontsize=10)
        
        plt.axis('off')
        plt.tight_layout()
        
        # Guardar imagen
        plt.savefig('smart_tourism_architecture.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_plotly_graph(self):
        """Crea una visualización interactiva con Plotly"""
        # Obtener posiciones
        pos = nx.spring_layout(self.G, k=3, iterations=50)
        
        # Ajustar posiciones manualmente
        pos['INE'] = (-2, 2)
        pos['TripAdvisor'] = (-2, 1)
        pos['Exceltur'] = (-2, 0)
        pos['Excel'] = (-2, -1)
        pos['DataCollectors'] = (0, 0.5)
        pos['Database'] = (2, 0)
        pos['Orchestrator'] = (0, 2.5)
        pos['PLS-SEM'] = (4, 1.5)
        pos['AI-Agents'] = (4, -1.5)
        pos['Dashboard'] = (6, 0)
        pos['Reports'] = (6, -2)
        pos['API'] = (6, 2)
        
        # Crear trazas para aristas
        edge_trace = []
        for edge in self.G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(
                go.Scatter(x=[x0, x1, None], 
                          y=[y0, y1, None],
                          mode='lines',
                          line=dict(width=2, color='#888'),
                          hoverinfo='none')
            )
        
        # Crear trazas para nodos
        node_trace = []
        for node_type, color in self.node_colors.items():
            nodes = [n for n, d in self.G.nodes(data=True) if d['type'] == node_type]
            if nodes:
                x = [pos[node][0] for node in nodes]
                y = [pos[node][1] for node in nodes]
                labels = [self.G.nodes[node]['label'].replace('\n', '<br>') for node in nodes]
                descriptions = [self.G.nodes[node]['description'] for node in nodes]
                
                node_trace.append(
                    go.Scatter(
                        x=x, y=y,
                        mode='markers+text',
                        text=labels,
                        textposition="middle center",
                        marker=dict(size=60, color=color),
                        hovertext=descriptions,
                        hoverinfo='text',
                        name=node_type.capitalize()
                    )
                )
        
        # Crear figura
        fig = go.Figure(data=edge_trace + node_trace)
        
        # Actualizar layout
        fig.update_layout(
            title={
                'text': 'Smart Tourism Management System - Arquitectura Interactiva',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            width=1400,
            height=800
        )
        
        # Añadir anotaciones para las aristas
        annotations = []
        for edge in self.G.edges(data=True):
            if 'label' in edge[2]:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                annotations.append(
                    dict(
                        x=(x0 + x1) / 2,
                        y=(y0 + y1) / 2,
                        text=edge[2]['label'],
                        showarrow=False,
                        font=dict(size=10, color='#333')
                    )
                )
        
        fig.update_layout(annotations=annotations)
        
        # Guardar como HTML
        fig.write_html("smart_tourism_interactive.html")
        fig.show()
    
    def analyze_system(self):
        """Analiza las características del sistema"""
        print("\n📊 ANÁLISIS DEL SISTEMA SMART TOURISM")
        print("=" * 50)
        
        # Estadísticas básicas
        print(f"\n📌 Componentes del Sistema:")
        print(f"   - Total de componentes: {self.G.number_of_nodes()}")
        print(f"   - Total de conexiones: {self.G.number_of_edges()}")
        
        # Componentes por tipo
        print(f"\n📋 Componentes por Tipo:")
        node_types = {}
        for node, data in self.G.nodes(data=True):
            node_type = data['type']
            if node_type not in node_types:
                node_types[node_type] = []
            node_types[node_type].append(node)
        
        for node_type, nodes in node_types.items():
            print(f"   - {node_type.capitalize()}: {len(nodes)} ({', '.join(nodes)})")
        
        # Análisis de centralidad
        print(f"\n🎯 Componentes Críticos (por centralidad):")
        centrality = nx.degree_centrality(self.G)
        sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        
        for node, score in sorted_centrality[:5]:
            print(f"   - {node}: {score:.3f}")
        
        # Flujo de datos
        print(f"\n🔄 Flujo de Datos:")
        print("   1. Recolección: INE, TripAdvisor, Exceltur → DataCollectors")
        print("   2. Almacenamiento: DataCollectors → Database")
        print("   3. Análisis: Database → PLS-SEM, AI-Agents")
        print("   4. Visualización: Análisis → Dashboard, Reports")
        
        # Frecuencias de actualización
        print(f"\n⏰ Frecuencias de Actualización:")
        print("   - Recolección de datos: Cada 1 hora")
        print("   - Análisis IA: Cada 2 horas")
        print("   - Análisis PLS-SEM: Diario")
        print("   - Dashboard: Cada 5 minutos")

def main():
    """Función principal para demostrar el grafo"""
    print("🏛️ VISUALIZACIÓN DEL SMART TOURISM MANAGEMENT SYSTEM")
    print("=" * 60)
    
    # Crear instancia del grafo
    graph = SystemArchitectureGraph()
    
    # Analizar el sistema
    graph.analyze_system()
    
    # Crear visualizaciones
    print("\n📊 Generando visualizaciones...")
    
    # Visualización estática con matplotlib
    print("   - Creando grafo estático (matplotlib)...")
    graph.create_matplotlib_graph()
    
    # Visualización interactiva con plotly
    print("   - Creando grafo interactivo (plotly)...")
    graph.create_plotly_graph()
    
    print("\n✅ Visualizaciones completadas:")
    print("   - smart_tourism_architecture.png (estático)")
    print("   - smart_tourism_interactive.html (interactivo)")

if __name__ == "__main__":
    main()
