import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import math
import streamlit.components.v1 as components

# --------------------
# Configuración
# --------------------
st.set_page_config(
    page_title="Port Performance Dashboard - Chile vs World",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------
# CSS
# --------------------
st.markdown("""
<style>
    .metric-card { background:#f8f9fa; padding:1rem; border-radius:.5rem;
                   border-left:4px solid #1f77b4; margin:.5rem 0; box-shadow:0 2px 4px rgba(0,0,0,.1); }
    .gap-critical { color:#fff; background:#dc3545; padding:2px 8px; border-radius:4px; font-weight:bold; }
    .gap-high     { color:#fff; background:#fd7e14; padding:2px 8px; border-radius:4px; font-weight:bold; }
    .gap-medium   { color:#000; background:#ffc107; padding:2px 8px; border-radius:4px; font-weight:bold; }
    .gap-low      { color:#fff; background:#28a745; padding:2px 8px; border-radius:4px; font-weight:bold; }
    .priority-card{ background:#fff; padding:1rem; border-radius:8px; border-left:4px solid #007bff;
                    margin:.5rem 0; box-shadow:0 2px 4px rgba(0,0,0,.1); }
</style>
""", unsafe_allow_html=True)

# --------------------
# Título / avisos
# --------------------
st.title("🚢 Dashboard Avanzado: Puertos Chilenos vs Top Performers Mundiales")
st.markdown("**Análisis Comparativo con Calculadora ROI y Recomendaciones Estratégicas**")
st.info(
    "Fuente principal de eficiencia: **CPPI (World Bank)**. "
    "El **Ranking CPPI 2023** se muestra como *menor es mejor*. "
    "Los índices de *Automatización* y *Ferrocarril* son **internos** (no pertenecen al CPPI)."
)
st.caption("Los rangos de **ROI** y **CAPEX** son orientativos y dependen del alcance y supuestos del proyecto.")
st.markdown("---")

# --------------------
# Helpers
# --------------------
def safe_pct(v, digits=1):
    try:
        v = float(v)
        return "N/D" if not math.isfinite(v) else f"{v:.{digits}f}%"
    except Exception:
        return "N/D"

def safe_money(v, digits=0):
    try:
        v = float(v)
        if not math.isfinite(v):
            return "N/D"
        return f"${v:,.{digits}f}" if digits > 0 else f"${v:,.0f}"
    except Exception:
        return "N/D"

def safe_years(v, digits=1):
    try:
        v = float(v)
        if not math.isfinite(v) or v > 1e6:
            return "N/D"
        return f"{v:.{digits}f} años"
    except Exception:
        return "N/D"

# --------------------
# Datos
# --------------------
@st.cache_data
def load_enhanced_data():
    # Top (mantengo tu "CPPI_Score" como índice interno DEMO)
    top_performers = pd.DataFrame({
        'Puerto': [
            'Yangshan (China)', 'Rey Abdullah (Arabia Saudí)', 'Hamad (Catar)',
            'Ningbo (China)', 'Mawan (China)', 'Dalian (China)',
            'Hong Kong', 'Port Said (Egipto)', 'Singapur', 'Algeciras (España)'
        ],
        'País': ['China','Arabia Saudí','Catar','China','China','China','Hong Kong','Egipto','Singapur','España'],
        'CPPI_Score': [146.3,142.8,140.5,138.2,136.7,134.9,133.1,131.8,130.5,129.2],  # demo interno (no oficial)
        'TEU_Annual': [47500000,2800000,6500000,33350000,13740000,9540000,17300000,3800000,37200000,5900000],
        'Berth_Productivity': [42,48,45,38,35,33,32,40,36,34],
        'Time_in_Port_Hours': [28.5,26.2,28.8,32.1,34.5,36.8,38.2,30.5,35.1,38.5],
        'Automation_Level': [95,88,85,90,85,82,75,70,80,65],
        'Rail_Connectivity': [85,60,45,80,75,78,40,55,70,75],
        'Digital_Systems': [95,90,88,92,88,85,82,78,85,80],
        'Cost_Per_TEU': [38,42,45,40,43,45,52,48,48,50],
        'Port_Charges': [280,320,350,290,310,320,380,340,360,340],
        'Dwell_Time_Days': [1.8,2.1,2.3,2.5,2.8,3.1,3.2,2.4,2.9,3.2]
    })
    # Ranking CPPI 2023 (↓ mejor) conocido con certeza para estos puertos:
    cppi_rank_map_top = {
        'Yangshan (China)': 1,
        'Algeciras (España)': 10,
        'Singapur': 17,
        # otros: desconocido -> NaN
    }

    chilean_ports = pd.DataFrame({
        'Puerto': ['Puerto Coronel','Puerto Valparaíso','Puerto Lirquén','Puerto San Vicente','Puerto Mejillones','Puerto Antofagasta','Puerto Arica','Puerto Iquique','Puerto San Antonio'],
        'País': ['Chile']*9,
        'CPPI_Score': [89.5,67.2,63.8,58.3,52.1,51.8,45.2,42.8,38.5],  # demo interno
        'TEU_Annual': [800000,1200000,450000,350000,280000,320000,180000,220000,1800000],
        'Berth_Productivity': [28,25,26,22,20,19,18,17,15],
        'Time_in_Port_Hours': [58.2,68.5,62.3,72.1,78.5,82.2,88.8,92.3,98.1],
        'Automation_Level': [25,20,22,15,12,10,8,8,15],
        'Rail_Connectivity': [15,8,12,10,5,8,3,5,12],
        'Digital_Systems': [30,25,28,20,18,15,12,10,20],
        'Cost_Per_TEU': [78,85,82,92,95,98,105,102,110],
        'Port_Charges': [420,480,450,520,540,560,580,570,620],
        'Dwell_Time_Days': [5.2,6.8,6.1,7.5,8.2,8.8,9.2,9.5,10.1]
    })
    cppi_rank_map_cl = {
        'Puerto Coronel': 97,
        'Puerto San Antonio': 110,
        'Puerto Valparaíso': 151,
        # otros: NaN
    }

    # Columna Ranking CPPI 2023 (unimos mapas)
    top_performers['CPPI_Rank_2023'] = top_performers['Puerto'].map(cppi_rank_map_top)
    chilean_ports['CPPI_Rank_2023']   = chilean_ports['Puerto'].map(cppi_rank_map_cl)

    all_ports = pd.concat([top_performers, chilean_ports], ignore_index=True)
    all_ports['Port_Type'] = ['Top Performer'] * len(top_performers) + ['Chilean Port'] * len(chilean_ports)

    # Históricos (demo)
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
    return all_ports, top_performers, chilean_ports, historical_data

all_ports, top_performers, chilean_ports, historical_data = load_enhanced_data()

# --------------------
# ROI
# --------------------
def calculate_roi(
    current_teu, current_productivity, target_productivity, investment,
    cost_per_teu=65, coverage=0.6, adoption=0.7, savings_factor=0.5,
    years=3, discount_rate=0.0
):
    try:
        current_teu = float(current_teu)
        cur_p = float(current_productivity)
        tgt_p = float(target_productivity)
        inv = float(investment)
        c_teu = float(cost_per_teu)
        cov = min(max(float(coverage), 0.0), 1.0)
        adop = min(max(float(adoption), 0.0), 1.0)
        eff = min(max(float(savings_factor), 0.0), 1.0)
        n = int(years)
        r = max(float(discount_rate), 0.0)

        if inv <= 0 or current_teu <= 0 or cur_p <= 0 or tgt_p <= 0:
            return {'annual_savings':0.0,'total_savings_3_years':0.0,'roi_percentage':float('nan'),
                    'payback_years':float('inf'),'productivity_improvement_pct':float('nan'),'cost_reduction_per_teu':0.0}

        improvement = max(0.0, tgt_p - cur_p) / max(tgt_p, 1e-9)
        improvement = min(improvement, 1.0)

        teu_eff = current_teu * cov
        cost_reduction_per_teu = c_teu * improvement * eff
        annual_savings = max(0.0, teu_eff * cost_reduction_per_teu * adop)

        pv = sum(annual_savings / ((1.0 + r) ** t) for t in range(1, n + 1))
        roi_percentage = ((pv - inv) / inv) * 100.0 if inv > 0 else float('nan')
        payback_years = (inv / annual_savings) if annual_savings > 0 else float('inf')

        return {'annual_savings': annual_savings, 'total_savings_3_years': pv,
                'roi_percentage': roi_percentage, 'payback_years': payback_years,
                'productivity_improvement_pct': (tgt_p - cur_p) / cur_p * 100.0,
                'cost_reduction_per_teu': cost_reduction_per_teu}
    except Exception:
        return {'annual_savings':0.0,'total_savings_3_years':0.0,'roi_percentage':float('nan'),
                'payback_years':float('inf'),'productivity_improvement_pct':float('nan'),'cost_reduction_per_teu':0.0}

def classify_gap(g):
    if g >= 60: return "CRÍTICO", "gap-critical"
    if g >= 40: return "ALTO", "gap-high"
    if g >= 20: return "MEDIO", "gap-medium"
    return "BAJO", "gap-low"

# --------------------
# Sidebar
# --------------------
st.sidebar.header("🔍 Filtros y Configuración")

year_filter = st.sidebar.selectbox("Año de Análisis:", options=[2023, 2022, 2021, 2020], index=0)

metric_options = {
    'CPPI_Rank_2023': 'Ranking CPPI 2023 (↓ mejor)',
    'CPPI_Score': 'Índice interno (demo)',
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
    index=0  # por defecto usa el Ranking CPPI 2023
)

selected_chilean_ports = st.sidebar.multiselect(
    "Puertos Chilenos a Comparar:",
    options=chilean_ports['Puerto'].tolist(),
    default=['Puerto Coronel','Puerto Valparaíso','Puerto San Antonio']
)
selected_top_ports = st.sidebar.multiselect(
    "Top Performers a Comparar:",
    options=top_performers['Puerto'].tolist(),
    default=['Yangshan (China)','Singapur','Algeciras (España)']
)

st.sidebar.markdown("---")
st.sidebar.markdown("📡 **Estado del Sistema**")
st.sidebar.success("✅ Datos: CPPI 2023 (ranking) + métricas internas")
st.sidebar.info(f"📊 Analizando año: {year_filter}")
st.sidebar.info(f"🚢 Total puertos: {len(all_ports)}")
if st.sidebar.button("♻️ Limpiar caché"):
    st.cache_data.clear()
    st.rerun()

# --------------------
# Main: comparación
# --------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📊 Comparación: {metric_options[selected_metric]}")
    filtered_chilean = chilean_ports[chilean_ports['Puerto'].isin(selected_chilean_ports)]
    filtered_top = top_performers[top_performers['Puerto'].isin(selected_top_ports)]
    filtered_data = pd.concat([filtered_top, filtered_chilean], ignore_index=True)
    filtered_data['Port_Type'] = ['Top Performer'] * len(filtered_top) + ['Chilean Port'] * len(filtered_chilean)

    # Si la métrica elegida es Ranking, quitamos NaN y adaptamos eje
    plot_df = filtered_data.dropna(subset=[selected_metric]) if selected_metric == 'CPPI_Rank_2023' else filtered_data.copy()

    if not plot_df.empty:
        fig_bar = px.bar(
            plot_df, x='Puerto', y=selected_metric, color='Port_Type',
            title=f'{metric_options[selected_metric]} - Análisis Comparativo {year_filter}',
            color_discrete_map={'Top Performer': '#1f77b4', 'Chilean Port': '#ff7f0e'},
            text=selected_metric
        )
        # Formato de etiquetas
        txtfmt = '%{text:.0f}' if selected_metric == 'CPPI_Rank_2023' else '%{text:.1f}'
        fig_bar.update_traces(texttemplate=txtfmt, textposition='outside')
        fig_bar.update_layout(xaxis_tickangle=-45, height=450, showlegend=True, xaxis_title="Puertos",
                              yaxis_title=metric_options[selected_metric])
        # En ranking, menor es mejor → invertir eje Y
        if selected_metric == 'CPPI_Rank_2023':
            fig_bar.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No hay datos para la combinación seleccionada (revisa que los puertos tengan **Ranking CPPI 2023** disponible).")

with col2:
    st.subheader("📈 KPIs Resumen")
    # KPI 1: Ranking CPPI 2023 (promedio, menor mejor)
    ch_rank = filtered_chilean['CPPI_Rank_2023'].dropna()
    top_rank = filtered_top['CPPI_Rank_2023'].dropna()
    if len(ch_rank) > 0 and len(top_rank) > 0:
        st.metric(
            "Ranking CPPI 2023 (↓ mejor)",
            f"{ch_rank.mean():.0f}",
            delta=f"{(ch_rank.mean() - top_rank.mean()):.0f}",
            delta_color="inverse",
            help="Menor es mejor; fuente World Bank CPPI 2023"
        )
    else:
        st.caption("Ranking CPPI 2023: faltan datos para alguno de los puertos seleccionados.")

    # KPI 2 y 3: product/costo (internos)
    if not filtered_chilean.empty:
        st.metric(
            "Productividad Promedio",
            f"{filtered_chilean['Berth_Productivity'].mean():.1f} moves/hr",
            delta=f"{(filtered_chilean['Berth_Productivity'].mean() - filtered_top['Berth_Productivity'].mean()):.1f}",
            help="Movimientos de contenedores por hora (interno)"
        )
        st.metric(
            "Costo Promedio por TEU",
            f"{safe_money(filtered_chilean['Cost_Per_TEU'].mean())}",
            delta=f"{safe_money(filtered_chilean['Cost_Per_TEU'].mean() - filtered_top['Cost_Per_TEU'].mean())}",
            delta_color="inverse",
            help="Costo operacional por contenedor (interno)"
        )

# --------------------
# ROI
# --------------------
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
        st.write(f"• TEU Anual: {int(port_data['TEU_Annual']):,}")
        st.write(f"• Productividad: {float(port_data['Berth_Productivity']):.1f} moves/hr")
        st.write(f"• Costo por TEU: {safe_money(port_data['Cost_Per_TEU'])}")
        st.write(f"• Automatización: {port_data['Automation_Level']:.0f}%")

with col_roi2:
    st.subheader("🎯 Objetivos de Mejora")
    investment_amount = st.number_input("Inversión Total (USD):", 100000, 100000000, 5_000_000, 500_000)
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
        st.markdown("#### Supuestos (conservadores)")
        coverage_pct = st.slider("Cobertura del proyecto (% del TEU impactado)", 0, 100, 60)
        adoption_pct = st.slider("Adopción/uso efectivo (%)", 0, 100, 70)
        savings_factor_pct = st.slider("Factor de eficiencia (%)", 0, 100, 50, help="Traduce productividad→ahorro")
        years_horizon = st.selectbox("Horizonte (años)", [1, 2, 3, 4, 5], index=2)
        discount_rate_pct = st.slider("Tasa de descuento anual (%)", 0, 20, 0)

with col_roi3:
    st.subheader("📊 Resultados ROI")

    def render_roi_card(roi_val: float, roi_text: str, horizon: int) -> str:
        is_pos = isinstance(roi_val, (int, float)) and math.isfinite(roi_val) and roi_val >= 0
        bg = "#e8f5e9" if is_pos else "#fdecea"
        border = "#28a745" if is_pos else "#dc3545"
        txt_color = "#19692c" if is_pos else "#842029"
        return f"""
<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
:root {{ color-scheme: light; }}
body {{ margin:0; font-family: system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,"Helvetica Neue",Arial; color:#111; background:transparent; }}
.card {{ background:{bg}; border-left:8px solid {border}; padding:16px; border-radius:10px; margin:6px 0; box-shadow:0 2px 6px rgba(0,0,0,.08); }}
.label {{ font-size:.95rem; opacity:.85; margin-bottom:6px; color:#111; }}
.value {{ font-size:2rem; font-weight:800; line-height:1; color:{txt_color}; -webkit-text-fill-color:{txt_color}; }}
</style></head>
<body><div class="card"><div class="label">💹 ROI a {horizon} años</div><div class="value">{roi_text}</div></div></body></html>
"""

    if target_port:
        roi_results = calculate_roi(
            current_teu=float(port_data['TEU_Annual']),
            current_productivity=float(port_data['Berth_Productivity']),
            target_productivity=float(target_productivity),
            investment=float(investment_amount),
            cost_per_teu=float(port_data['Cost_Per_TEU']),
            coverage=coverage_pct/100.0,
            adoption=adoption_pct/100.0,
            savings_factor=savings_factor_pct/100.0,
            years=years_horizon,
            discount_rate=discount_rate_pct/100.0
        )
        roi_val = roi_results['roi_percentage']
        roi_text = safe_pct(roi_val, digits=1)
        components.html(render_roi_card(roi_val, roi_text, years_horizon), height=120, scrolling=False)

        st.metric("Ahorros Anuales", safe_money(roi_results['annual_savings']))
        st.metric("Payback Period", safe_years(roi_results['payback_years']))
        st.metric("Mejora Productividad", f"+{safe_pct(roi_results['productivity_improvement_pct'])}")

# --------------------
# Brechas
# --------------------
st.markdown("---")
st.header("🎯 Análisis Detallado de Brechas")
col_gap1, col_gap2 = st.columns(2)

with col_gap1:
    st.subheader("📈 Radar Chart Comparativo")
    filtered_chilean = chilean_ports[chilean_ports['Puerto'].isin(selected_chilean_ports)]
    filtered_top = top_performers[top_performers['Puerto'].isin(selected_top_ports)]
    if not filtered_chilean.empty and not filtered_top.empty:
        ch_avg = filtered_chilean[['CPPI_Score','Berth_Productivity','Automation_Level','Rail_Connectivity','Digital_Systems']].mean()
        tp_avg = filtered_top[['CPPI_Score','Berth_Productivity','Automation_Level','Rail_Connectivity','Digital_Systems']].mean()
        metrics_radar = ['Índice (demo)','Productividad','Automatización','Ferrocarril','Digital']

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[ch_avg['CPPI_Score']/150*100, ch_avg['Berth_Productivity']/50*100,
               ch_avg['Automation_Level'], ch_avg['Rail_Connectivity'], ch_avg['Digital_Systems']],
            theta=metrics_radar, fill='toself', name='Puertos Chilenos',
            line=dict(color='#ff7f0e', width=2)
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[tp_avg['CPPI_Score']/150*100, tp_avg['Berth_Productivity']/50*100,
               tp_avg['Automation_Level'], tp_avg['Rail_Connectivity'], tp_avg['Digital_Systems']],
            theta=metrics_radar, fill='toself', name='Top Performers',
            line=dict(color='#1f77b4', width=2)
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                showlegend=True, title="Análisis Multidimensional (normalizado 0–100%)", height=400)
        st.plotly_chart(fig_radar, use_container_width=True)

with col_gap2:
    st.subheader("🚨 Prioridades de Mejora")
    if not filtered_chilean.empty:
        gaps = []
        for metric, label in [('Automation_Level','Automatización'),
                              ('Rail_Connectivity','Conectividad Ferroviaria'),
                              ('Digital_Systems','Sistemas Digitales'),
                              ('Berth_Productivity','Productividad')]:
            ch = filtered_chilean[metric].mean()
            tp = filtered_top[metric].mean() if len(filtered_top) > 0 else top_performers[metric].mean()
            gap_abs = tp - ch
            gap_pct = (gap_abs / tp * 100) if tp > 0 else 0
            prio, css = classify_gap(gap_pct)
            gaps.append({'metric': label, 'gap_percentage': gap_pct, 'gap_absolute': gap_abs, 'priority': prio, 'css_class': css})
        gaps.sort(key=lambda x: x['gap_percentage'], reverse=True)

        for i, g in enumerate(gaps):
            color = {'CRÍTICO':'#dc3545','ALTO':'#fd7e14','MEDIO':'#ffc107','BAJO':'#28a745'}.get(g['priority'], '#6c757d')
            st.markdown(f"""
            <div class="priority-card" style="border-left-color:{color};">
              <h5 style="margin-bottom:.5rem;color:#333;">{i+1}. {g['metric']}</h5>
              <p style="margin-bottom:.5rem;">Gap: <strong>{g['gap_percentage']:.1f}%</strong>
                 <span class="{g['css_class']}">{g['priority']}</span></p>
              <div style="background:#e9ecef;border-radius:4px;height:8px;overflow:hidden;">
                <div style="background:{color};height:100%;width:{min(g['gap_percentage'],100):.1f}%;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# --------------------
# Tendencias (demo)
# --------------------
if year_filter != 2023:
    st.markdown("---")
    st.header("📈 Análisis de Tendencias Históricas")
    col_trend1, col_trend2 = st.columns(2)
    with col_trend1:
        st.subheader("🔄 Evolución Puerto Valparaíso")
        if 'Puerto Valparaíso' in historical_data:
            years = list(historical_data['Puerto Valparaíso'].keys())
            cppi_values = [historical_data['Puerto Valparaíso'][y]['CPPI_Score'] for y in years]
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=years, y=cppi_values, mode='lines+markers', name='Índice (demo)',
                                           line=dict(color='#ff7f0e', width=3), marker=dict(size=8)))
            fig_trend.update_layout(title="Índice (demo) 2020–2023", xaxis_title="Año", yaxis_title="Valor", height=300)
            st.plotly_chart(fig_trend, use_container_width=True)
    with col_trend2:
        st.subheader("📊 Crecimiento Anual")
        if 'Puerto Valparaíso' in historical_data:
            growth = []
            for i in range(1, len(years)):
                prev, curr = cppi_values[i-1], cppi_values[i]
                growth.append(((curr - prev) / prev * 100) if prev else float('nan'))
            avg_growth = np.nanmean(growth) if growth else float('nan')
            st.metric("Crecimiento medio", safe_pct(avg_growth))
            proj_2024 = cppi_values[-1] * (1 + (avg_growth/100 if math.isfinite(avg_growth) else 0))
            st.write(f"**Proyección 2024:** {proj_2024:.1f}")

# --------------------
# Tabla
# --------------------
st.markdown("---")
st.subheader("📋 Datos Detallados Comparativos")
if 'filtered_data' in locals() and not filtered_data.empty:
    display_cols = ['Puerto','País','Port_Type','CPPI_Rank_2023'] + [c for c in
                    ['CPPI_Score','TEU_Annual','Berth_Productivity','Time_in_Port_Hours',
                     'Automation_Level','Rail_Connectivity','Digital_Systems','Cost_Per_TEU','Dwell_Time_Days']]
    display_data = filtered_data[display_cols]
    styled = display_data.style.format({
        'CPPI_Rank_2023':'{:.0f}', 'CPPI_Score':'{:.1f}', 'TEU_Annual':'{:,}',
        'Berth_Productivity':'{:.1f}', 'Time_in_Port_Hours':'{:.1f}',
        'Cost_Per_TEU':'${:.0f}', 'Dwell_Time_Days':'{:.1f}'
    }, na_rep="N/D")
    st.dataframe(styled, use_container_width=True)

# --------------------
# Recomendaciones (texto)
# --------------------
st.markdown("---")
st.header("🎯 Recomendaciones Estratégicas")
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("⚡ Acciones Inmediatas")
    st.markdown("""
**🏆 Port Community System (PCS)**
- Inversión (orientativa): USD 0.5–1M  
- ROI: caso-dependiente
- Nota: *Automatización* y *Ferrocarril* son **índices internos**
""")
with c2:
    st.subheader("🚀 Mediano Plazo")
    st.markdown("""
**🤖 Automatización Escalonada**
- Fases según madurez y TOS/infraestructura
- Mejora de productividad: caso-dependiente
""")
with c3:
    st.subheader("🌟 Visión 2030")
    st.markdown("""
**🏭 Puerto 4.0**
- IoT + IA + Integraciones PCS/Port Community
- Objetivo: acercarse a top performers del CPPI
""")

# --------------------
# Exportación
# --------------------
st.markdown("---")
st.header("📤 Exportación de Análisis")
e1, e2, e3, e4 = st.columns(4)

with e1:
    st.subheader("📋 Reporte Ejecutivo")
    if st.button("📊 Generar Reporte", use_container_width=True):
        txt = f"""
REPORTE EJECUTIVO - ANÁLISIS PORTUARIO
=====================================
Fecha: {datetime.now().strftime("%d/%m/%Y")}
Año Análisis: {year_filter}

PUERTOS ANALIZADOS:
• Chilenos: {', '.join(selected_chilean_ports)}
• Benchmarks: {', '.join(selected_top_ports)}
"""
        st.text_area("📄 Reporte Ejecutivo Generado:", txt, height=260)
        st.download_button("📥 Descargar Reporte TXT", txt,
                           file_name=f"reporte_ejecutivo_{datetime.now().strftime('%Y%m%d')}.txt",
                           mime="text/plain")

with e2:
    st.subheader("📊 Datos Excel")
    if st.button("📈 Exportar Excel", use_container_width=True):
        from io import BytesIO
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w:
            filtered_data.to_excel(w, sheet_name='Datos_Comparativos', index=False)
        buf.seek(0)
        st.download_button("📥 Descargar Excel", buf.getvalue(),
                           file_name=f"analisis_puertos_{datetime.now().strftime('%Y%m%d')}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with e3:
    st.subheader("💰 Análisis ROI")
    if 'roi_results' in locals() and st.button("🧮 Exportar ROI", use_container_width=True):
        roi_txt = f"""
ANÁLISIS ROI
============
Puerto: {target_port}
Fecha: {datetime.now().strftime("%d/%m/%Y")}

RESULTADOS:
• ROI a {years_horizon} años: {safe_pct(roi_results['roi_percentage'])}
• Ahorros Anuales: {safe_money(roi_results['annual_savings'])}
• Payback: {safe_years(roi_results['payback_years'])}
"""
        st.download_button("📥 Descargar ROI", roi_txt,
                           file_name=f"roi_{target_port.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                           mime="text/plain")

with e4:
    st.subheader("📋 Datos CSV")
    if st.button("📊 Exportar CSV", use_container_width=True):
        st.download_button("📥 Descargar CSV", filtered_data.to_csv(index=False),
                           file_name=f"datos_{datetime.now().strftime('%Y%m%d')}.csv",
                           mime="text/csv")

# --------------------
# Footer / Contacto
# --------------------
st.markdown("---")
st.markdown("""
### 📊 Fuentes y Metodología
- **CPPI 2023 (World Bank)** – Ranking (↓ mejor) para puertos con dato disponible.
- **Observatorio Logístico (Chile)**, **UNCTAD** – contexto.
- Métricas de **Automatización/Ferrocarril/Digital** son **internas (demo)**.

### 🔬 ROI
- Basado en mejoras de productividad → reducción de tiempos/costos.
- Supuestos conservadores con cobertura/adopción/eficiencia.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🤝 Consultoría Disponible")
st.sidebar.info("""
**Servicios:**
- Auditorías de eficiencia portuaria
- Roadmaps de automatización
- Implementación PCS
- Benchmarking competitivo
- Análisis ROI

📧 consultoria@portoptimization.cl
""")

if st.sidebar.checkbox("🔧 Modo Debug", value=False):
    st.sidebar.write(f"Puertos CL: {len(selected_chilean_ports)} | Top: {len(selected_top_ports)}")
    st.sidebar.write(f"Métrica: {selected_metric}")
    st.sidebar.write(f"Registros plot: {len(filtered_data)}")
