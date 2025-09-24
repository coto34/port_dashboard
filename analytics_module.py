"""
Módulo de Análisis Avanzado y Generación de Recomendaciones
Para Dashboard de Puertos Chile vs Top Performers
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PortAnalytics:
    """
    Clase para análisis avanzado y generación de recomendaciones estratégicas
    """
    
    def __init__(self, consolidated_data: pd.DataFrame):
        self.data = consolidated_data
        self.chilean_ports = consolidated_data[consolidated_data.get('Port_Category') == 'Chilean Port']
        self.top_performers = consolidated_data[consolidated_data.get('Port_Category') == 'Top Performer']
        
        # Métricas clave para análisis
        self.key_metrics = [
            'CPPI_Score', 'Berth_Productivity_Moves_Hour', 'Automation_Level',
            'Rail_Connectivity_Percent', 'Digital_Systems_Score', 'TEU_Annual_2023'
        ]
        
        # Pesos para cálculo de scores compuestos
        self.metric_weights = {
            'CPPI_Score': 0.25,
            'Berth_Productivity_Moves_Hour': 0.20,
            'Automation_Level': 0.20,
            'Rail_Connectivity_Percent': 0.15,
            'Digital_Systems_Score': 0.20
        }
    
    def calculate_performance_gaps(self) -> pd.DataFrame:
        """
        Calcula brechas de performance entre puertos chilenos y top performers
        """
        logger.info("Calculando brechas de performance...")
        
        gaps_data = []
        
        for _, chilean_port in self.chilean_ports.iterrows():
            port_name = chilean_port['Puerto']
            port_gaps = {'Puerto': port_name}
            
            for metric in self.key_metrics:
                if metric in self.chilean_ports.columns and metric in self.top_performers.columns:
                    chilean_value = chilean_port.get(metric, 0)
                    top_avg = self.top_performers[metric].mean()
                    top_best = self.top_performers[metric].max()
                    
                    gap_avg = top_avg - chilean_value
                    gap_best = top_best - chilean_value
                    gap_percentage = (gap_avg / top_avg * 100) if top_avg > 0 else 0
                    
                    port_gaps[f'{metric}_Gap_Average'] = gap_avg
                    port_gaps[f'{metric}_Gap_Best'] = gap_best
                    port_gaps[f'{metric}_Gap_Percentage'] = gap_percentage
            
            gaps_data.append(port_gaps)
        
        gaps_df = pd.DataFrame(gaps_data)
        
        # Calcular gap score compuesto
        gaps_df['Overall_Gap_Score'] = self._calculate_composite_gap_score(gaps_df)
        
        return gaps_df
    
    def _calculate_composite_gap_score(self, gaps_df: pd.DataFrame) -> pd.Series:
        """Calcula score compuesto de gaps"""
        composite_scores = []
        
        for _, row in gaps_df.iterrows():
            weighted_gap = 0
            total_weight = 0
            
            for metric, weight in self.metric_weights.items():
                gap_col = f'{metric}_Gap_Percentage'
                if gap_col in gaps_df.columns:
                    gap_value = abs(row.get(gap_col, 0))
                    weighted_gap += gap_value * weight
                    total_weight += weight
            
            composite_score = weighted_gap / total_weight if total_weight > 0 else 0
            composite_scores.append(round(composite_score, 2))
        
        return pd.Series(composite_scores)
    
    def identify_improvement_priorities(self) -> Dict[str, List[Dict]]:
        """
        Identifica prioridades de mejora por puerto
        """
        logger.info("Identificando prioridades de mejora...")
        
        gaps_df = self.calculate_performance_gaps()
        priorities = {}
        
        for _, row in gaps_df.iterrows():
            port_name = row['Puerto']
            port_priorities = []
            
            # Analizar cada métrica
            for metric in self.key_metrics:
                gap_col = f'{metric}_Gap_Percentage'
                if gap_col in gaps_df.columns:
                    gap_percentage = row[gap_col]
                    
                    if gap_percentage > 20:  # Gap significativo
                        priority_level = self._get_priority_level(gap_percentage)
                        impact_potential = self._estimate_impact_potential(metric, gap_percentage)
                        implementation_difficulty = self._estimate_implementation_difficulty(metric)
                        
                        port_priorities.append({
                            'metric': metric,
                            'metric_name': self._get_metric_display_name(metric),
                            'gap_percentage': gap_percentage,
                            'priority_level': priority_level,
                            'impact_potential': impact_potential,
                            'implementation_difficulty': implementation_difficulty,
                            'roi_score': impact_potential / implementation_difficulty
                        })
            
            # Ordenar por ROI score
            port_priorities.sort(key=lambda x: x['roi_score'], reverse=True)
            priorities[port_name] = port_priorities[:5]  # Top 5 prioridades
        
        return priorities
    
    def generate_benchmarking_recommendations(self) -> Dict[str, Dict]:
        """
        Genera recomendaciones basadas en benchmarking con top performers
        """
        logger.info("Generando recomendaciones de benchmarking...")
        
        recommendations = {}
        
        for _, chilean_port in self.chilean_ports.iterrows():
            port_name = chilean_port['Puerto']
            port_recommendations = {}
            
            # Encontrar mejores modelos de referencia por métrica
            for metric in self.key_metrics:
                if metric in self.top_performers.columns:
                    best_performer = self.top_performers.loc[
                        self.top_performers[metric].idxmax()
                    ]
                    
                    chilean_value = chilean_port.get(metric, 0)
                    best_value = best_performer[metric]
                    
                    if best_value > chilean_value * 1.2:  # 20% mejor al menos
                        model_recommendations = self._get_implementation_roadmap(
                            metric, chilean_value, best_value, best_performer
                        )
                        
                        port_recommendations[metric] = {
                            'reference_port': best_performer['Puerto'],
                            'reference_country': best_performer.get('País', 'N/A'),
                            'current_value': chilean_value,
                            'target_value': best_value,
                            'improvement_potential': best_value - chilean_value,
                            'roadmap': model_recommendations
                        }
            
            recommendations[port_name] = port_recommendations
        
        return recommendations
    
    def _get_implementation_roadmap(self, metric: str, current: float, 
                                  target: float, reference_port: pd.Series) -> List[Dict]:
        """
        Genera roadmap de implementación específico por métrica
        """
        roadmaps = {
            'Automation_Level': [
                {
                    'phase': 'Fase 1: Automatización Básica (6-12 meses)',
                    'actions': [
                        'Implementar sistemas automatizados de control de acceso',
                        'Instalar sensores IoT para monitoreo de equipos',
                        'Digitalizar procesos de documentación'
                    ],
                    'investment': 'USD 2-5 millones',
                    'expected_improvement': '10-15 puntos'
                },
                {
                    'phase': 'Fase 2: Automatización Intermedia (12-18 meses)',
                    'actions': [
                        'Implementar AGVs para transporte de contenedores',
                        'Automatizar grúas pórtico principales',
                        'Sistema de gestión de terminal (TOS) avanzado'
                    ],
                    'investment': 'USD 10-20 millones',
                    'expected_improvement': '15-25 puntos'
                },
                {
                    'phase': 'Fase 3: Automatización Avanzada (18-36 meses)',
                    'actions': [
                        'Terminal completamente automatizada',
                        'IA para optimización de operaciones',
                        'Integración con sistemas de shipping líneas'
                    ],
                    'investment': 'USD 30-50 millones',
                    'expected_improvement': '25-40 puntos'
                }
            ],
            
            'Digital_Systems_Score': [
                {
                    'phase': 'Fase 1: Digitalización Básica (3-6 meses)',
                    'actions': [
                        'Implementar Port Community System (PCS)',
                        'Integrar sistemas aduaneros digitales',
                        'Dashboard operacional en tiempo real'
                    ],
                    'investment': 'USD 500K - 1M',
                    'expected_improvement': '15-20 puntos'
                },
                {
                    'phase': 'Fase 2: Integración Avanzada (6-12 meses)',
                    'actions': [
                        'Blockchain para trazabilidad de carga',
                        'Sistemas predictivos de mantenimiento',
                        'Integración con sistemas ferroviarios'
                    ],
                    'investment': 'USD 1-3 millones',
                    'expected_improvement': '20-30 puntos'
                }
            ],
            
            'Rail_Connectivity_Percent': [
                {
                    'phase': 'Fase 1: Conectividad Básica (12-24 meses)',
                    'actions': [
                        'Conexión ferroviaria directa al puerto',
                        'Terminal intermodal básica',
                        'Sistemas de intercambio modal'
                    ],
                    'investment': 'USD 20-50 millones',
                    'expected_improvement': '20-30 puntos'
                },
                {
                    'phase': 'Fase 2: Optimización Ferroviaria (24-36 meses)',
                    'actions': [
                        'Duplicar vías férreas principales',
                        'Terminal ferroviaria automatizada',
                        'Integración con red ferroviaria nacional'
                    ],
                    'investment': 'USD 50-100 millones',
                    'expected_improvement': '30-50 puntos'
                }
            ],
            
            'Berth_Productivity_Moves_Hour': [
                {
                    'phase': 'Fase 1: Mejora Operacional (3-6 meses)',
                    'actions': [
                        'Optimización de procesos existentes',
                        'Capacitación intensiva de operadores',
                        'Mantenimiento predictivo de equipos'
                    ],
                    'investment': 'USD 200K - 500K',
                    'expected_improvement': '5-10 moves/hora'
                },
                {
                    'phase': 'Fase 2: Modernización de Equipos (6-18 meses)',
                    'actions': [
                        'Grúas pórtico de alta productividad',
                        'Equipos de manipulación modernos',
                        'Sistemas de posicionamiento automático'
                    ],
                    'investment': 'USD 5-15 millones',
                    'expected_improvement': '10-20 moves/hora'
                }
            ]
        }
        
        return roadmaps.get(metric, [
            {
                'phase': 'Análisis Específico Requerido',
                'actions': ['Consultoría especializada para definir roadmap'],
                'investment': 'A determinar',
                'expected_improvement': 'A determinar'
            }
        ])
    
    def _get_priority_level(self, gap_percentage: float) -> str:
        """Determina nivel de prioridad basado en el gap"""
        if gap_percentage >= 50:
            return 'CRÍTICA'
        elif gap_percentage >= 30:
            return 'ALTA'
        elif gap_percentage >= 20:
            return 'MEDIA'
        else:
            return 'BAJA'
    
    def _estimate_impact_potential(self, metric: str, gap_percentage: float) -> float:
        """Estima potencial de impacto de mejorar una métrica"""
        impact_factors = {
            'CPPI_Score': 1.0,
            'Berth_Productivity_Moves_Hour': 0.9,
            'Automation_Level': 0.8,
            'Digital_Systems_Score': 0.7,
            'Rail_Connectivity_Percent': 0.6
        }
        
        base_impact = impact_factors.get(metric, 0.5)
        gap_factor = min(gap_percentage / 100, 1.0)
        
        return base_impact * (1 + gap_factor)
    
    def _estimate_implementation_difficulty(self, metric: str) -> float:
        """Estima dificultad de implementación"""
        difficulty_scores = {
            'Digital_Systems_Score': 0.3,  # Más fácil
            'Berth_Productivity_Moves_Hour': 0.5,
            'Automation_Level': 0.7,
            'CPPI_Score': 0.8,
            'Rail_Connectivity_Percent': 1.0  # Más difícil
        }
        
        return difficulty_scores.get(metric, 0.6)
    
    def _get_metric_display_name(self, metric: str) -> str:
        """Obtiene nombres amigables para métricas"""
        display_names = {
            'CPPI_Score': 'Eficiencia General (CPPI)',
            'Berth_Productivity_Moves_Hour': 'Productividad de Muelle',
            'Automation_Level': 'Nivel de Automatización',
            'Digital_Systems_Score': 'Sistemas Digitales',
            'Rail_Connectivity_Percent': 'Conectividad Ferroviaria',
            'TEU_Annual_2023': 'Capacidad Anual (TEU)'
        }
        
        return display_names.get(metric, metric)
    
    def generate_executive_summary(self) -> Dict:
        """
        Genera resumen ejecutivo del análisis
        """
        logger.info("Generando resumen ejecutivo...")
        
        gaps_df = self.calculate_performance_gaps()
        priorities = self.identify_improvement_priorities()
        
        # Estadísticas generales
        avg_cppi_chile = self.chilean_ports['CPPI_Score'].mean()
        avg_cppi_top = self.top_performers['CPPI_Score'].mean()
        overall_gap = ((avg_cppi_top - avg_cppi_chile) / avg_cppi_top * 100)
        
        # Puerto con mejor performance
        best_chilean = self.chilean_ports.loc[
            self.chilean_ports['CPPI_Score'].idxmax()
        ]
        
        # Puerto con mayor potencial de mejora
        worst_gap_port = gaps_df.loc[gaps_df['Overall_Gap_Score'].idxmax()]
        
        # Métricas más críticas
        critical_metrics = self._identify_critical_metrics()
        
        summary = {
            'analysis_date': datetime.now().isoformat(),
            'overall_performance': {
                'chile_avg_cppi': round(avg_cppi_chile, 1),
                'top_performers_avg_cppi': round(avg_cppi_top, 1),
                'overall_gap_percentage': round(overall_gap, 1),
                'gap_classification': 'CRÍTICO' if overall_gap > 40 else 'SIGNIFICATIVO' if overall_gap > 25 else 'MODERADO'
            },
            'best_performer_chile': {
                'name': best_chilean['Puerto'],
                'cppi_score': best_chilean['CPPI_Score'],
                'ranking_global': best_chilean.get('CPPI_Rank_Global', 'N/A')
            },
            'highest_potential': {
                'name': worst_gap_port['Puerto'],
                'gap_score': worst_gap_port['Overall_Gap_Score'],
                'improvement_potential': 'ALTO' if worst_gap_port['Overall_Gap_Score'] > 40 else 'MEDIO'
            },
            'critical_areas': critical_metrics,
            'total_ports_analyzed': len(self.chilean_ports),
            'benchmarks_used': len(self.top_performers),
            'key_recommendations': self._get_key_recommendations()
        }
        
        return summary
    
    def _identify_critical_metrics(self) -> List[Dict]:
        """Identifica métricas más críticas a nivel nacional"""
        gaps_df = self.calculate_performance_gaps()
        
        metric_criticality = []
        
        for metric in self.key_metrics:
            gap_col = f'{metric}_Gap_Percentage'
            if gap_col in gaps_df.columns:
                avg_gap = gaps_df[gap_col].mean()
                ports_affected = len(gaps_df[gaps_df[gap_col] > 30])  # Gap > 30%
                
                metric_criticality.append({
                    'metric': self._get_metric_display_name(metric),
                    'average_gap': round(avg_gap, 1),
                    'ports_critically_affected': ports_affected,
                    'criticality_score': avg_gap * (ports_affected / len(gaps_df))
                })
        
        # Ordenar por criticidad
        metric_criticality.sort(key=lambda x: x['criticality_score'], reverse=True)
        
        return metric_criticality[:3]  # Top 3 críticas
    
    def _get_key_recommendations(self) -> List[str]:
        """Genera recomendaciones clave del análisis"""
        return [
            "Implementar Port Community System (PCS) como primera prioridad",
            "Desarrollar plan nacional de automatización portuaria escalonada",
            "Mejorar conectividad ferroviaria en puertos principales",
            "Establecer benchmarking continuo con puertos top performers",
            "Crear programa de capacitación en tecnologías portuarias avanzadas"
        ]
    
    def export_analysis_report(self, filename: str = None) -> str:
        """
        Exporta reporte completo de análisis
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"port_analysis_report_{timestamp}.json"
        
        report = {
            'executive_summary': self.generate_executive_summary(),
            'performance_gaps': self.calculate_performance_gaps().to_dict('records'),
            'improvement_priorities': self.identify_improvement_priorities(),
            'benchmarking_recommendations': self.generate_benchmarking_recommendations(),
            'methodology': {
                'data_sources': [
                    'Container Port Performance Index (CPPI) - Banco Mundial',
                    'Observatorio Logístico Chile',
                    'Estudios especializados en eficiencia portuaria'
                ],
                'metrics_analyzed': len(self.key_metrics),
                'weight_distribution': self.metric_weights,
                'analysis_framework': 'Benchmarking comparativo con top performers globales'
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Reporte de análisis exportado: {filename}")
        return filename

def create_strategic_recommendations(analytics: PortAnalytics) -> Dict:
    """
    Crea recomendaciones estratégicas específicas para consultoría
    """
    
    executive_summary = analytics.generate_executive_summary()
    priorities = analytics.identify_improvement_priorities()
    
    strategic_recommendations = {
        'immediate_actions': [
            {
                'action': 'Implementar Port Community System (PCS)',
                'timeline': '3-6 meses',
                'investment': 'USD 500K - 1M',
                'expected_roi': '300-500% en 2 años',
                'success_cases': ['Valencia Port', 'Singapore Port']
            },
            {
                'action': 'Digitalizar procesos aduaneros y documentales',
                'timeline': '2-4 meses',
                'investment': 'USD 200K - 500K',
                'expected_roi': '200-400% en 18 meses',
                'success_cases': ['Port of Rotterdam', 'Hamburg Port']
            }
        ],
        
        'medium_term_initiatives': [
            {
                'initiative': 'Programa de Automatización Escalonada',
                'timeline': '12-24 meses',
                'phases': [
                    'Automatización de accesos y documentación',
                    'AGVs para transporte interno',
                    'Grúas automatizadas'
                ],
                'total_investment': 'USD 10-30M por puerto',
                'productivity_increase': '40-60%'
            }
        ],
        
        'long_term_vision': [
            {
                'vision': 'Puerto 4.0 - Completamente Digitalizado',
                'timeline': '3-5 años',
                'key_technologies': [
                    'Internet of Things (IoT)',
                    'Inteligencia Artificial',
                    'Blockchain',
                    'Gemelos Digitales',
                    'Automatización Completa'
                ]
            }
        ],
        
        'consulting_opportunities': [
            'Auditoría de eficiencia operacional',
            'Diseño de roadmap de automatización',
            'Implementación de sistemas PCS',
            'Benchmarking continuo con top performers',
            'Capacitación en mejores prácticas internacionales'
        ]
    }
    
    return strategic_recommendations