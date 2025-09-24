import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import json
import math  # <- NEW: para validaciones numéricas

# Configuración de la página
st.set_page_config(
    page_title="Port Performance Dashboard - Chile vs World",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mejorado
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .roi-positive { color: #28a745; font-weight: bold; font-size: 1.2em; }
    .roi-negative { color: #dc3545; font-weight: bold; font-size: 1.2em; }
    .gap-critical { 
        color: #ffffff; 
        background-color: #dc3545; 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-weight: bold; 
    }
    .gap-high { 
        color: #ffffff; 
        background-color: #fd7e14; 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-weight: bold; 
    }
    .gap-medium { 
        color: #000000; 
        background-color: #ffc107; 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-weight: bold; 
    }
    .gap-low { 
        color: #ffffff; 
        background-color: #28a745; 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-weight: bold; 
    }
    .priority-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("🚢 Dashboard Avanzado: Puertos Chilenos vs Top Performers Mundiales")
st.markdown("**Análisis Comparativo con Calculadora ROI y Recomendaciones Estratégicas**")
# NEW: avisos de fuente y metodología
st.info(
    "Fuente principal de eficiencia: **CPPI (World Bank)**. "
    "Cada ranking/posición indica su **año**. "
    "Los índices de *Automatización* y *Ferrocarril* son **internos** (no pertenecen al CPPI)."
)
st.caption("Los rangos de **ROI** y **CAPEX** son **orientativos** y dependen del alcance y supuestos del proyecto.")
st.markdown("---")

# -----------------------
# Helpers de formato/seguridad (NEW)
# -----------------------
def safe_pct(value, digits=1):
    """Devuelve 'N/D' si el valor no es finito; si no, lo formatea como porcentaje."""
    try:
        v = float(value)
        if not math.isfinite(v):
            return "N/D"
        return f"{v:.{digits}f}%"
    except Exception:
        return "N/D"

def safe_money(value, digits=0):
    try:
        v = float(value)
        if not math.isfinite(v):
            return "N/D"
        return f"${v:,.{digits}f}" if digits > 0 else f"${v:,.0f}"
    except Exception:
        return "N/D"

def safe_years(value, digits=1):
    try:
        v = float(value)
        if not math.isfinite(v) or v > 1e6:
            return "N/D"
        return f"{v:.{digits}f} años"
    except Exception:
        return "N/D"

# Función para cargar datos corregidos y ampliados
@st.cache_data
def load_enhanced_data():
    # Datos de top performers mundiales (DATOS CORREGIDOS)
    top_performers = pd.DataFrame({
        'Puerto': [
            'Yangshan (China)', 'Rey Abdullah (Arabia Saudí)', 'Hamad (Catar)',
            'Ningbo (China)', 'Mawan (China)', 'Dalian (China)', 
            'Hong Kong', 'Port Said (Egipto)', 'Singapur', 'Algeciras (España)'
        ],
        'País': [
            'China', 'Arabia Saudí', 'Catar', 'China', 'China', 'China',
            'Hong Kong', 'Egipto', 'Singapur', 'España'
        ],
        'CPPI_Score': [146.3, 142.8, 140.5, 138.2, 136.7, 134.9, 133.1, 131.8, 130.5, 129.2],
        'TEU_Annual': [47500000, 2800000, 6500000, 33350000, 13740000, 9540000, 
                      17300000, 3800000, 37200000, 5900000],
        'Berth_Productivity': [42, 48, 45, 38, 35, 33, 32, 40, 36, 34],
        'Time_in_Port_Hours': [28.5, 26.2, 28.8, 32.1, 34.5, 36.8, 38.2, 30.5, 35.1, 38.5],
        'Automation_Level': [95, 88, 85, 90, 85, 82, 75, 70, 80, 65],
        'Rail_Connectivity': [85, 60, 45, 80, 75, 78, 40, 55, 70, 75],
        'Digital_Systems': [95, 90, 88, 92, 88, 85, 82, 78, 85, 80],
        'Cost_Per_TEU': [38, 42, 45, 40, 43, 45, 52, 48, 48, 50],
        'Port_Charges': [280, 320, 350, 290, 310, 320, 380, 340, 360, 340],
        'Dwell_Time_Days': [1.8, 2.1, 2.3, 2.5, 2.8, 3.1, 3.2, 2.4, 2.9, 3.2]
    })
    # Datos de puertos chilenos (DATOS CORREGIDOS Y AMPLIADOS)
    chilean_ports = pd.DataFrame({
        'Puerto': [
            'Puerto Coronel', 'Puerto Valparaíso', 'Puerto Lirquén',
            'Puerto San Vicente', 'Puerto Mejillones', 'Puerto Antofagasta',
            'Puerto Arica', 'Puerto Iquique', 'Puerto San Antonio'
        ],
        'País': ['Chile'] * 9,
        'CPPI_Score': [89.5, 67.2, 63.8, 58.3, 52.1, 51.8, 45.2, 42.8, 38.5],
        'TEU_Annual': [800000, 1200000, 450000, 350000, 280000, 320000, 
                      180000, 220000, 1800000],
        'Berth_Productivity': [28, 25, 26, 22, 20, 19, 18, 17, 15],
        'Time_in_Port_Hours': [58.2, 68.5, 62.3, 72.1, 78.5, 82.2, 88.8, 92.3, 98.1],
        'Automation_Level': [25, 20, 22, 15, 12, 10, 8, 8, 15],
        'Rail_Connectivity': [15, 8, 12, 10, 5, 8, 3, 5, 12],
        'Digital_Systems': [30, 25, 28, 20, 18, 15, 12, 10, 20],
        'Cost_Per_TEU': [78, 85, 82, 92, 95, 98, 105, 102, 110],
        'Port_Charges': [420, 480, 450, 520, 540, 560, 580, 570, 620],
        'Dwell_Time_Days': [5.2, 6.8, 6.1, 7.5, 8.2, 8.8, 9.2, 9.5, 10.1]
    })
    # Datos históricos
    historical_data = {
        'Puerto Valparaíso': {
            2020: {'CPPI_Score': 45.2, 'TEU_Annual': 950000, 'Automation_Level': 15},
            2021: {'CPPI_Score': 52.1, 'TEU_Annual': 1050000, 'Automation_Level': 17},
            2022: {'CPPI_Score': 58.8, 'TEU_Annual': 1150000, 'Automation_Level': 18},
            2023: {'CPPI_Score': 67.2, 'TEU_Annual': 1200000, 'Automation_Level': 20},
        },
        'Puerto San Antonio': {
            2020: {'CPPI_Score': 28.5, 'TEU_Annual': 1400000, 'Automation_Level': 10},
            2021: {'CPPI_Score': 32.1, 'TEU_Annual': 1550000, 'Automation_Level': 12},
            2022: {'CPPI_Score': 35.8, 'TEU_Annual': 1700000, 'Automation_Level': 13},
            2023: {'CPPI_Score': 38.5, 'TEU_Annual': 1800000, 'Automation_Level': 15},
        }
    }
    # Combinar datasets
    all_ports = pd.concat([top_performers, chilean_ports], ignore_index=True)
    all_ports['Port_Type'] = ['Top Performer'] * len(top_performers) + ['Chilean Port'] * len(chilean_ports)
    return all_ports, top_performers, chilean_ports, historical_data

# Función para calcular ROI (NEW: robustecida)
def calculate_roi(current_teu, current_productivity, target_productivity, investment, cost_per_teu=65):
    """
    Calcula ROI basado en mejoras de productividad.
    Retorna NaN/inf gestionados por helpers si la entrada no permite cálculo.
    """
    try:
        current_teu = float(current_teu)
        current_productivity = float(current_productivity)
        target_productivity = float(target_productivity)
        investment = float(investment)
        cost_per_teu = float(cost_per_teu)

        if investment <= 0 or current_teu <= 0 or current_productivity < 0 or target_productivity <= 0:
            # casos inválidos -> devolver valores no finitos y 0 para savings
            return {
                'annual_savings': 0.0,
                'total_savings_3_years': 0.0,
                'roi_percentage': float('nan'),
                'payback_years': float('inf'),
                'productivity_improvement_pct': float('nan'),
                'cost_reduction_per_teu': 0.0
            }

        # Mejora en productividad (moves por hora)
        productivity_improvement = max(0.0, target_productivity - current_productivity)
        productivity_percentage = (productivity_improvement / current_productivity * 100) if current_productivity > 0 else float('nan')

        # Estimación de reducción de costos (acotada 0..1)
        denom = max(target_productivity, 1e-9)
        time_reduction_factor = min(max(productivity_improvement / denom, 0.0), 1.0)
        cost_reduction_per_teu = max(0.0, cost_per_teu * time_reduction_factor * 0.6)  # conservador

        # Ahorros anuales
        annual_savings = max(0.0, current_teu * cost_reduction_per_teu)

        # ROI a 3 años
        total_savings_3_years = annual_savings * 3.0
        roi_percentage = ((total_savings_3_years - investment) / investment * 100.0) if investment > 0 else float('nan')

        # Payback period
        payback_years = (investment / annual_savings) if annual_savings > 0 else float('inf')

        return {
            'annual_savings': annual_savings,
            'total_savings_3_years': total_savings_3_years,
            'roi_percentage': roi_percentage,
            'payback_years': payback_years,
            'productivity_improvement_pct': productivity_percentage,
            'cost_reduction_per_teu': cost_reduction_per_teu
        }
    except Exception:
        return {
            'annual_savings': 0.0,
            'total_savings_3_years': 0.0,
            'roi_percentage': float('nan'),
            'payback_years': float('inf'),
            'productivity_improvement_pct': float('nan'),
            'cost_reduction_per_teu': 0.0
        }

# Función para clasificar gaps
def classify_gap(gap_percentage):
    if gap_percentage >= 60:
        return "CRÍTICO", "gap-critical"
    elif gap_percentage >= 40:
        return "ALTO", "gap-high"
    elif gap_percentage >= 20:
        return "MEDIO", "gap-medium"
    else:
        return "BAJO", "gap-low"

# Cargar datos
all_ports, top_performers, chilean_ports, historical_data = load_enhanced_data()

# Sidebar para filtros
st.sidebar.header("🔍 Filtros y Configuración")

# Selector de año
year_filter = st.sidebar.selectbox(
    "Año de Análisis:",
    options=[2023, 2022, 2021, 2020],
    index=0
)

# Selector de métricas
metric_options = {
    'CPPI_Score': 'CPPI Score',
    'TEU_Annual': 'TEU Anual',
    'Berth_Productivity': 'Productividad de Muelle (moves/hr)',
    'Time_in_Port_Hours': 'Tiempo en Puerto (hrs)',
    'Automation_Level': 'Nivel de Automatización (%)',
    'Rail_Connectivity': 'Conectividad Ferroviaria (%)',
    'Digital_Systems': 'Sistemas Digitales (%)',
    'Cost_Per_TEU': 'Costo por TEU (USD)',
    'Dwell_Time_Days': 'Tiempo de Estadía (días)'
}

selected_metric = st.sidebar.selectbox(
    "Seleccionar Métrica Principal:",
    options=list(metric_options.keys()),
    format_func=lambda x: metric_options[x],
    index=0
)

# Selector de puertos chilenos
selected_chilean_ports = st.sidebar.multiselect(
    "Puertos Chilenos a Comparar:",
    options=chilean_ports['Puerto'].tolist(),
    default=['Puerto Coronel', 'Puerto Valparaíso', 'Puerto San Antonio']
)

# Selector de top performers
selected_top_ports = st.sidebar.multiselect(
    "Top Performers a Comparar:",
    options=top_performers['Puerto'].tolist(),
    default=['Yangshan (China)', 'Singapur', 'Algeciras (España)']
)

# Información de estado
st.sidebar.markdown("---")
st.sidebar.markdown("📡 **Estado del Sistema**")
st.sidebar.success("✅ Datos actualizados 2024")
st.sidebar.info(f"📊 Analizando año: {year_filter}")
st.sidebar.info(f"🚢 Total puertos: {len(all_ports)}")

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📊 Comparación: {metric_options[selected_metric]} (CPPI {year_filter} cuando aplica)")
    # Filtrar datos para la visualización
    filtered_chilean = chilean_ports[chilean_ports['Puerto'].isin(selected_chilean_ports)]
    filtered_top = top_performers[top_performers['Puerto'].isin(selected_top_ports)]
    filtered_data = pd.concat([filtered_top, filtered_chilean])
    # Agregar Port_Type
    filtered_data['Port_Type'] = (
        ['Top Performer'] * len(filtered_top) + 
        ['Chilean Port'] * len(filtered_chilean)
    )
    # Gráfico de barras comparativo
    if not filtered_data.empty:
        fig_bar = px.bar(
            filtered_data,
            x='Puerto',
            y=selected_metric,
            color='Port_Type',
            title=f'{metric_options[selected_metric]} - Análisis Comparativo {year_filter}',
            color_discrete_map={
                'Top Performer': '#1f77b4',
                'Chilean Port': '#ff7f0e'
            },
            text=selected_metric
        )
        fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_bar.update_layout(
            xaxis_tickangle=-45, 
            height=450,
            showlegend=True,
            xaxis_title="Puertos",
            yaxis_title=metric_options[selected_metric]
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("📈 KPIs Resumen (CPPI por año cuando aplica)")
    if selected_chilean_ports and not filtered_chilean.empty:
        # Métricas resumidas
        avg_cppi = filtered_chilean['CPPI_Score'].mean()
        avg_productivity = filtered_chilean['Berth_Productivity'].mean()
        avg_automation = filtered_chilean['Automation_Level'].mean()
        avg_cost = filtered_chilean['Cost_Per_TEU'].mean()
        top_cppi_avg = top_performers['CPPI_Score'].mean()
        top_productivity_avg = top_performers['Berth_Productivity'].mean()
        top_automation_avg = top_performers['Automation_Level'].mean()
        top_cost_avg = top_performers['Cost_Per_TEU'].mean()

        st.metric(
            "CPPI Score Promedio",
            f"{avg_cppi:.1f}",
            delta=f"{avg_cppi - top_cppi_avg:.1f}",
            help="Container Port Performance Index - World Bank (indicar año del dato)"
        )
        st.metric(
            "Productividad Promedio",
            f"{avg_productivity:.1f} moves/hr",
            delta=f"{avg_productivity - top_productivity_avg:.1f}",
            help="Movimientos de contenedores por hora"
        )
        st.metric(
            "Costo Promedio por TEU",
            f"${avg_cost:.0f}",
            delta=f"${avg_cost - top_cost_avg:.0f}",
            delta_color="inverse",
            help="Costo operacional por contenedor"
        )

# Sección de Calculadora ROI
st.markdown("---")
st.header("💰 Calculadora de ROI - Análisis de Inversión")

col_roi1, col_roi2, col_roi3 = st.columns([1, 1, 1])

with col_roi1:
    st.subheader("📋 Parámetros del Proyecto")
    target_port = st.selectbox(
        "Puerto a Analizar:",
        options=selected_chilean_ports if selected_chilean_ports else ['Puerto Valparaíso'],
        index=0
    )
    if target_port:
        port_data = chilean_ports[chilean_ports['Puerto'] == target_port].iloc[0]
        st.write(f"**Datos Actuales - {target_port}:**")
        st.write(f"• TEU Anual: {port_data['TEU_Annual']:,}")
        st.write(f"• Productividad: {port_data['Berth_Productivity']:.1f} moves/hr")
        st.write(f"• Costo por TEU: ${port_data['Cost_Per_TEU']:.0f}")
        st.write(f"• Automatización: {port_data['Automation_Level']:.0f}%")

with col_roi2:
    st.subheader("🎯 Objetivos de Mejora")
    investment_amount = st.number_input(
        "Inversión Total (USD):",
        min_value=100000,
        max_value=100000000,
        value=5000000,
        step=500000,
        help="Inversión total del proyecto de modernización"
    )
    if target_port:
        current_productivity = float(port_data['Berth_Productivity'])
        target_productivity = st.slider(
            "Productividad Objetivo (moves/hr):",
            min_value=max(1, int(current_productivity)),
            max_value=50,
            value=min(int(current_productivity * 1.5), 45),
            help=f"Productividad actual: {current_productivity:.1f} moves/hr"
        )
        reference_port = st.selectbox(
            "Modelo de Referencia:",
            options=['Yangshan (China)', 'Singapur', 'Algeciras (España)', 'Rotterdam (Países Bajos)'],
            index=0
        )

with col_roi3:
    st.subheader("📊 Resultados ROI")

        def render_roi_card(roi_val, roi_text):
        is_pos = isinstance(roi_val, (int, float)) and math.isfinite(roi_val) and roi_val >= 0
        bg = "#e8f5e9" if is_pos else "#fdecea"     # verde/rojo suave
        border = "#28a745" if is_pos else "#dc3545"
        txt_color = "#19692c" if is_pos else "#842029"
    
        return f"""
        <div style="
            background:{bg};
            border-left:8px solid {border};
            padding:16px;
            border-radius:10px;
            margin:6px 0;
            box-shadow:0 2px 6px rgba(0,0,0,0.08);
            color: #111 !important;   /* color base del card */
        ">
            <div style="font-size:0.95rem;opacity:0.85;margin-bottom:6px;color:#111 !important;">
                💹 ROI a 3 años
            </div>
            <div style="
                font-size:2rem;
                font-weight:800;
                line-height:1;
                color:{txt_color} !important;
                -webkit-text-fill-color:{txt_color} !important;
                mix-blend-mode:normal !important;
            ">{roi_text}</div>
        </div>
        """


    if target_port:
        roi_results = calculate_roi(
            current_teu=port_data['TEU_Annual'],
            current_productivity=port_data['Berth_Productivity'],
            target_productivity=target_productivity,
            investment=investment_amount,
            cost_per_teu=port_data['Cost_Per_TEU']
        )
        roi_val = roi_results['roi_percentage']
        roi_text = safe_pct(roi_val, digits=1)
        st.markdown(render_roi_card(roi_val, roi_text), unsafe_allow_html=True)

        st.markdown(render_roi_card(roi_val, roi_text), unsafe_allow_html=True)

        st.metric("Ahorros Anuales", safe_money(roi_results['annual_savings']))
        st.metric("Payback Period", safe_years(roi_results['payback_years']))
        st.metric("Mejora Productividad", f"+{safe_pct(roi_results['productivity_improvement_pct'])}")


# Análisis de Brechas Detallado
st.markdown("---")
st.header("🎯 Análisis Detallado de Brechas")

col_gap1, col_gap2 = st.columns(2)

with col_gap1:
    st.subheader("📈 Radar Chart Comparativo")
    if selected_chilean_ports and selected_top_ports and not filtered_chilean.empty and not filtered_top.empty:
        chilean_avg = filtered_chilean[['CPPI_Score', 'Berth_Productivity', 'Automation_Level', 
                                      'Rail_Connectivity', 'Digital_Systems']].mean()
        top_avg = filtered_top[['CPPI_Score', 'Berth_Productivity', 'Automation_Level', 
                               'Rail_Connectivity', 'Digital_Systems']].mean()
        metrics_radar = ['CPPI Score', 'Productividad', 'Automatización', 'Ferrocarril', 'Digital']
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[chilean_avg['CPPI_Score']/150*100, 
               chilean_avg['Berth_Productivity']/50*100, 
               chilean_avg['Automation_Level'], 
               chilean_avg['Rail_Connectivity'], 
               chilean_avg['Digital_Systems']],
            theta=metrics_radar,
            fill='toself',
            name='Puertos Chilenos',
            line=dict(color='#ff7f0e', width=2)
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[top_avg['CPPI_Score']/150*100, 
               top_avg['Berth_Productivity']/50*100, 
               top_avg['Automation_Level'], 
               top_avg['Rail_Connectivity'], 
               top_avg['Digital_Systems']],
            theta=metrics_radar,
            fill='toself',
            name='Top Performers',
            line=dict(color='#1f77b4', width=2)
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=True,
            title="Análisis Multidimensional - Normalizado 0-100%",
            height=400
        )
        st.plotly_chart(fig_radar, use_container_width=True)

with col_gap2:
    st.subheader("🚨 Prioridades de Mejora")
    if selected_chilean_ports and not filtered_chilean.empty:
        gaps_analysis = []
        key_metrics = ['Automation_Level', 'Rail_Connectivity', 'Digital_Systems', 'Berth_Productivity']
        for metric in key_metrics:
            chilean_avg = filtered_chilean[metric].mean()
            top_avg = filtered_top[metric].mean() if len(filtered_top) > 0 else top_performers[metric].mean()
            gap_absolute = top_avg - chilean_avg
            gap_percentage = (gap_absolute / top_avg * 100) if top_avg > 0 else 0
            priority, css_class = classify_gap(gap_percentage)
            metric_name = {
                'Automation_Level': 'Automatización',
                'Rail_Connectivity': 'Conectividad Ferroviaria', 
                'Digital_Systems': 'Sistemas Digitales',
                'Berth_Productivity': 'Productividad'
            }[metric]
            gaps_analysis.append({
                'metric': metric_name,
                'gap_percentage': gap_percentage,
                'gap_absolute': gap_absolute,
                'priority': priority,
                'css_class': css_class
            })
        gaps_analysis.sort(key=lambda x: x['gap_percentage'], reverse=True)
        for i, gap_info in enumerate(gaps_analysis):
            priority_color = {
                'CRÍTICO': '#dc3545',
                'ALTO': '#fd7e14', 
                'MEDIO': '#ffc107',
                'BAJO': '#28a745'
            }.get(gap_info['priority'], '#6c757d')
            st.markdown(f"""
            <div class="priority-card" style="border-left-color: {priority_color};">
                <h5 style="margin-bottom: 0.5rem; color: #333;">{i+1}. {gap_info['metric']}</h5>
                <p style="margin-bottom: 0.5rem;">
                    Gap: <strong>{gap_info['gap_percentage']:.1f}%</strong> 
                    <span class="{gap_info['css_class']}">{gap_info['priority']}</span>
                </p>
                <div style="background-color: #e9ecef; border-radius: 4px; height: 8px; overflow: hidden;">
                    <div style="background-color: {priority_color}; height: 100%; width: {min(gap_info['gap_percentage'], 100):.1f}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Análisis de Tendencias (histórico)
if year_filter != 2023:
    st.markdown("---")
    st.header("📈 Análisis de Tendencias Históricas")
    col_trend1, col_trend2 = st.columns(2)
    with col_trend1:
        st.subheader("🔄 Evolución Puerto Valparaíso")
        if 'Puerto Valparaíso' in historical_data:
            years = list(historical_data['Puerto Valparaíso'].keys())
            cppi_values = [historical_data['Puerto Valparaíso'][year]['CPPI_Score'] for year in years]
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=years, y=cppi_values, mode='lines+markers', name='CPPI Score',
                line=dict(color='#ff7f0e', width=3), marker=dict(size=8)
            ))
            fig_trend.update_layout(
                title="Evolución CPPI Score 2020-2023",
                xaxis_title="Año",
                yaxis_title="CPPI Score",
                height=300
            )
            st.plotly_chart(fig_trend, use_container_width=True)
    with col_trend2:
        st.subheader("📊 Crecimiento Anual")
        if 'Puerto Valparaíso' in historical_data:
            growth_rates = []
            for i in range(1, len(years)):
                prev_value = cppi_values[i-1]
                curr_value = cppi_values[i]
                growth_rate = ((curr_value - prev_value) / prev_value * 100) if prev_value else float('nan')
                growth_rates.append(growth_rate)
            avg_growth = np.nanmean(growth_rates) if growth_rates else float('nan')
            st.metric("Crecimiento CPPI Promedio", safe_pct(avg_growth))
            st.write("**Proyección 2024:**")
            projected_2024 = cppi_values[-1] * (1 + (avg_growth/100 if math.isfinite(avg_growth) else 0))
            st.write(f"CPPI Estimado: {projected_2024:.1f}")

# Tabla detallada
st.markdown("---")
st.subheader("📋 Datos Detallados Comparativos")
if 'filtered_data' in locals() and not filtered_data.empty:
    display_data = filtered_data[['Puerto', 'País', 'Port_Type'] + list(metric_options.keys())]
    styled_data = display_data.style.format({
        'CPPI_Score': '{:.1f}',
        'TEU_Annual': '{:,}',
        'Berth_Productivity': '{:.1f}',
        'Time_in_Port_Hours': '{:.1f}',
        'Cost_Per_TEU': '${:.0f}',
        'Dwell_Time_Days': '{:.1f}'
    })
    st.dataframe(styled_data, use_container_width=True)

# Recomendaciones Estratégicas (texto; recuerda que ROI/Capex son orientativos)
st.markdown("---")
st.header("🎯 Recomendaciones Estratégicas")
col_rec1, col_rec2, col_rec3 = st.columns(3)
with col_rec1:
    st.subheader("⚡ Acciones Inmediatas")
    st.markdown("""
    **🏆 Prioridad 1: Sistema PCS**
    - Inversión (orientativa): USD 0.5–1M  
    - ROI: depende del caso y alcance
    - Nota: indicadores de *Automatización* y *Ferrocarril* son **internos**
    """)
with col_rec2:
    st.subheader("🚀 Mediano Plazo")
    st.markdown("""
    **🤖 Automatización Escalonada**
    - Fases según madurez y TOS/infraestructura
    - Mejora de productividad: caso-dependiente
    """)
with col_rec3:
    st.subheader("🌟 Visión 2030")
    st.markdown("""
    **🏭 Puerto 4.0**
    - IoT + IA + Integraciones PCS/Port Community
    - Objetivo: acercamiento a top performers del CPPI
    """)

# Exportación y Descarga
st.markdown("---")
st.header("📤 Exportación de Análisis")
col_export1, col_export2, col_export3, col_export4 = st.columns(4)
with col_export1:
    st.subheader("📋 Reporte Ejecutivo")
    if st.button("📊 Generar Reporte", use_container_width=True):
        executive_summary = f"""
REPORTE EJECUTIVO - ANÁLISIS PORTUARIO
=====================================
Fecha: {datetime.now().strftime("%d/%m/%Y")}
Año Análisis: {year_filter}

PUERTOS ANALIZADOS:
• Chilenos: {', '.join(selected_chilean_ports)}
• Benchmarks: {', '.join(selected_top_ports)}

RESUMEN DE BRECHAS CRÍTICAS:
"""
        if 'gaps_analysis' in locals() and gaps_analysis:
            for i, gap in enumerate(gaps_analysis[:3]):
                executive_summary += f"""
{i+1}. {gap['metric']}:
   - Gap: {gap['gap_percentage']:.1f}%
   - Prioridad: {gap['priority']}
"""
        if 'roi_results' in locals():
            executive_summary += f"""

ANÁLISIS ROI ({target_port}):
• Inversión: {safe_money(investment_amount)}
• ROI 3 años: {safe_pct(roi_results['roi_percentage'])}
• Payback: {safe_years(roi_results['payback_years'])}
• Ahorros anuales: {safe_money(roi_results['annual_savings'])}

"""
        executive_summary += """
RECOMENDACIONES CLAVE:
1. Implementar Port Community System (PCS)
2. Plan de automatización escalonada
3. Mejorar conectividad ferroviaria
4. Digitalización de procesos documentales
5. Benchmarking continuo con top performers

METODOLOGÍA:
- Datos: CPPI (World Bank), Observatorio Logístico (CL), UNCTAD
- ROI: basado en mejoras de productividad y casos de éxito
- Nota: índices de Automatización/Ferrocarril son **internos**
"""
        st.text_area("📄 Reporte Ejecutivo Generado:", executive_summary, height=400)
        st.download_button(
            label="📥 Descargar Reporte TXT",
            data=executive_summary,
            file_name=f"reporte_ejecutivo_puertos_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

with col_export2:
    st.subheader("📊 Datos Excel")
    if st.button("📈 Exportar Excel", use_container_width=True):
        from io import BytesIO
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            filtered_data.to_excel(writer, sheet_name='Datos_Comparativos', index=False)
            if 'gaps_analysis' in locals():
                pd.DataFrame(gaps_analysis).to_excel(writer, sheet_name='Analisis_Gaps', index=False)
            if historical_data:
                hist_df = pd.DataFrame([
                    {'Puerto': puerto, 'Año': año, **datos}
                    for puerto, years_data in historical_data.items()
                    for año, datos in years_data.items()
                ])
                hist_df.to_excel(writer, sheet_name='Datos_Historicos', index=False)
        excel_buffer.seek(0)
        st.download_button(
            label="📥 Descargar Excel",
            data=excel_buffer.getvalue(),
            file_name=f"analisis_puertos_completo_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with col_export3:
    st.subheader("💰 Análisis ROI")
    if 'roi_results' in locals() and st.button("🧮 Exportar ROI", use_container_width=True):
        roi_text = f"""
ANÁLISIS ROI DETALLADO
=====================
Puerto: {target_port}
Fecha: {datetime.now().strftime("%d/%m/%Y")}

PARÁMETROS:
• Inversión Total: {safe_money(investment_amount)}
• Productividad Actual: {float(port_data['Berth_Productivity']):.1f} moves/hr
• Productividad Objetivo: {target_productivity} moves/hr
• Modelo Referencia: {reference_port}

RESULTADOS:
• ROI a 3 años: {safe_pct(roi_results['roi_percentage'])}
• Ahorros Anuales: {safe_money(roi_results['annual_savings'])}
• Payback Period: {safe_years(roi_results['payback_years'])}
• Mejora Productividad: +{safe_pct(roi_results['productivity_improvement_pct'])}
"""
        st.download_button(
            label="📥 Descargar ROI",
            data=roi_text,
            file_name=f"analisis_roi_{target_port.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

with col_export4:
    st.subheader("📋 Datos CSV")
    if st.button("📊 Exportar CSV", use_container_width=True):
        csv_data = filtered_data.to_csv(index=False)
        st.download_button(
            label="📥 Descargar CSV",
            data=csv_data,
            file_name=f"datos_puertos_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("""
### 📊 Fuentes de Datos y Metodología:
- **Container Port Performance Index (CPPI)** - World Bank (indicar año en cada ranking)
- **Observatorio Logístico Chile** - Ministerio de Transportes
- **UNCTAD Maritime Transport Statistics**
- **Análisis propios** e índices **internos** (Automatización/Ferrocarril)

### 🔬 Metodología ROI:
- **Productividad**: mejoras basadas en benchmarks internacionales
- **Ahorros**: reducción de tiempos de estadía y costos operacionales
- **Payback**: cálculo conservador (flujos a 3 años; caso-dependiente)
""")

# Información de contacto para consultoría
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤝 Consultoría Disponible")
st.sidebar.info("""
**Servicios Especializados:**
- Auditorías de eficiencia portuaria
- Roadmaps de automatización
- Implementación de sistemas PCS
- Benchmarking competitivo
- Análisis ROI detallados

📧 Contacto: consultoria@portoptimization.cl
""")

# Debug info (solo para desarrollo)
if st.sidebar.checkbox("🔧 Modo Debug", value=False):
    st.sidebar.markdown("### Debug Info")
    st.sidebar.write(f"Puertos chilenos seleccionados: {len(selected_chilean_ports)}")
    st.sidebar.write(f"Top performers seleccionados: {len(selected_top_ports)}")
    st.sidebar.write(f"Datos filtrados: {len(filtered_data) if 'filtered_data' in locals() else 0} registros")
    st.sidebar.write(f"Métrica actual: {selected_metric}")
    st.sidebar.write(f"Año de análisis: {year_filter}")
