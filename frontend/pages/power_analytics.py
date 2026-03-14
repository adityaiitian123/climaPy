import streamlit as st
import pandas as pd
import numpy as np
from backend.climate_processor import ClimateProcessor
from backend.echarts_renderer import render_echarts

def render_power_analytics(ds, controls):
    """Renders a high-density dashboard with Power BI-style advanced visualizations."""
    var = controls["variable"]
    t_idx = controls["time_index"]
    units = controls["units"]
    
    st.markdown("""
    <div class="section-tag">
        <span class="tag-line" style="background:linear-gradient(90deg,#06b6d4,#8b5cf6)"></span>
        <h3 style="margin:0; font-size:1.25rem;">Power Intelligence Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)

    # 1. DISTRIBUTION METRICS (Funnel & Gauge)
    col_g1, col_g2, col_g3 = st.columns([1, 1, 2])
    
    stats = ClimateProcessor.get_statistical_summary(ds, var, t_idx)
    
    with col_g1:
        st.markdown("""
        <div class="glass-card" style="margin-bottom:0.5rem; text-align:center;">
            <div style='font-size:0.65rem; color:#64748b; letter-spacing:0.1em;'>GLOBAL MEAN INDEX</div>
        </div>
        """, unsafe_allow_html=True)
        val = stats.get('mean', 0)
        gauge_opt = {
            "series": [{
                "type": "gauge", "center": ["50%", "60%"], "radius": "90%", "startAngle": 210, "endAngle": -30,
                "min": float(stats.get('min', 0)), "max": float(stats.get('max', 100)),
                "progress": {"show": True, "width": 8, "itemStyle": {"color": "#06b6d4", "shadowBlur": 10, "shadowColor": "#06b6d4"}},
                "axisLine": {"lineStyle": {"width": 8, "color": [[1, "rgba(6,182,212,0.1)"]]}},
                "axisTick": {"show": False}, "splitLine": {"show": False}, "axisLabel": {"show": False},
                "pointer": {"show": True, "length": "60%", "width": 4, "itemStyle": {"color": "#06b6d4"}},
                "detail": {"valueAnimation": True, "formatter": "{value:.1f}", "color": "#f1f5f9", "fontSize": 20, "offsetCenter": [0, "50%"]},
                "data": [{"value": val, "name": "INDEX"}]
            }]
        }
        render_echarts(gauge_opt, height=200)

    with col_g2:
        st.markdown("""
        <div class="glass-card" style="margin-bottom:0.5rem; text-align:center;">
            <div style='font-size:0.65rem; color:#64748b; letter-spacing:0.1em;'>STATISTICAL SIGMA</div>
        </div>
        """, unsafe_allow_html=True)
        std_val = stats.get('std', 0)
        gauge_std_opt = {
            "series": [{
                "type": "gauge", "center": ["50%", "60%"], "radius": "90%", "startAngle": 210, "endAngle": -30,
                "progress": {"show": True, "width": 8, "itemStyle": {"color": "#8b5cf6", "shadowBlur": 10, "shadowColor": "#8b5cf6"}},
                "axisLine": {"lineStyle": {"width": 8, "color": [[1, "rgba(139,92,246,0.1)"]]}},
                "axisTick": {"show": False}, "splitLine": {"show": False}, "axisLabel": {"show": False},
                "detail": {"formatter": "{value:.1f}", "color": "#f1f5f9", "fontSize": 20, "offsetCenter": [0, "50%"]},
                "data": [{"value": std_val, "name": "SIGMA"}]
            }]
        }
        render_echarts(gauge_std_opt, height=200)

    with col_g3:
        st.markdown("""
        <div class="glass-card" style="margin-bottom:0.5rem; text-align:center;">
             <div style='font-size:0.65rem; color:#64748b; letter-spacing:0.1em;'>DISTRIBUTION FUNNEL</div>
        </div>
        """, unsafe_allow_html=True)
        counts, edges = ClimateProcessor.get_histogram_data(ds, var, t_idx, bins=5)
        labels = ["V. Low", "Low", "Median", "High", "V. High"]
        funnel_data = [{"value": counts[i], "name": labels[i]} for i in range(len(counts))]
        funnel_opt = {
            "tooltip": {"trigger": "item"},
            "series": [{
                "name": "Distribution", "type": "funnel", "left": "10%", "top": 10, "bottom": 10, "width": "80%",
                "minSize": "0%", "maxSize": "100%", "sort": "descending", "gap": 2,
                "label": {"show": True, "position": "inside", "color": "#fff", "fontSize": 10, "fontWeight": "bold"},
                "itemStyle": {"borderColor": "transparent", "borderWidth": 1},
                "data": funnel_data
            }],
            "color": ["#1e1b4b", "#312e81", "#3b82f6", "#0ea5e9", "#ef4444"]
        }
        render_echarts(funnel_opt, height=200)

    # 2. HIERARCHICAL & STATISTICAL (Sunburst & Boxplot)
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        st.markdown("""
        <div class="glass-card" style="margin-bottom:1rem;">
             <h4 style="margin:0; color:#3b82f6;">🧬 Data Hierarchy Sunburst</h4>
        </div>
        """, unsafe_allow_html=True)
        # Build a data-driven sunburst: Hemisphere -> 30° Band -> Mean
        df_z = ClimateProcessor.get_zonal_mean(ds, var, t_idx)
        if not df_z.empty:
            def get_mean(lo, hi):
                v = df_z[(df_z['lat'] >= lo) & (df_z['lat'] < hi)][var].mean()
                return float(round(v, 2)) if not np.isnan(v) else 0

            sun_data = [
                {"name": "Northern", "itemStyle": {"color": "#3b82f6"}, "children": [
                    {"name": "0-30N", "value": get_mean(0,30)},
                    {"name": "30-60N", "value": get_mean(30,60)},
                    {"name": "60-90N", "value": get_mean(60,90)},
                ]},
                {"name": "Southern", "itemStyle": {"color": "#ef4444"}, "children": [
                    {"name": "0-30S", "value": get_mean(-30,0)},
                    {"name": "30-60S", "value": get_mean(-60,-30)},
                    {"name": "60-90S", "value": get_mean(-90,-60)},
                ]}
            ]
        else:
            sun_data = []

        sun_opt = {
            "series": [{
                "type": "sunburst", "data": sun_data, "radius": [0, "90%"],
                "label": {"rotate": "radial", "fontSize": 9},
                "itemStyle": {"borderColor": "#0f172a", "borderWidth": 1}
            }],
            "color": ["#6366f1", "#8b5cf6", "#d946ef", "#f43f5e"]
        }
        render_echarts(sun_opt, height=350)

    with col_h2:
        st.markdown("""
        <div class="glass-card" style="margin-bottom:1rem;">
             <h4 style="margin:0; color:#38bdf8;">📊 Statistical Quartile Range</h4>
        </div>
        """, unsafe_allow_html=True)
        # Boxplot for statistical robustness
        box_opt = {
            "tooltip": {"trigger": "item"},
            "grid": {"left": "15%", "right": "10%", "top": "15%", "bottom": "15%"},
            "xAxis": {"type": "category", "data": ["Telemetry Sample"], "axisLabel": {"color": "#64748b"}},
            "yAxis": {"type": "value", "name": units, "axisLabel": {"color": "#64748b"}},
            "series": [{
                "name": "boxplot", "type": "boxplot",
                "data": [[stats.get('min'), stats.get('q1'), stats.get('median'), stats.get('q3'), stats.get('max')]],
                "itemStyle": {"borderColor": "#38bdf8", "borderWidth": 2, "color": "rgba(56,189,248,0.2)"}
            }]
        }
        render_echarts(box_opt, height=350)

    # 3. ANALYTICAL RELATIONSHIPS (Parallel & Waterfall)
    col_a1, col_a2 = st.columns([2, 1])
    
    with col_a1:
        st.markdown("""
        <div class="glass-card" style="margin-bottom:1rem;">
             <h4 style="margin:0; color:#06b6d4;">🔗 Multivariate Feature Correlation</h4>
        </div>
        """, unsafe_allow_html=True)
        df_slice = ClimateProcessor.get_spatial_slice(ds, var, t_idx).head(100)
        if not df_slice.empty:
            parallel_data = df_slice[['lat', 'lon', var]].values.tolist()
            parallel_opt = {
                "parallelAxis": [
                    {"dim": 0, "name": "Latitude", "areaSelectStyle": {"width": 20}, "nameTextStyle": {"color": "#64748b"}},
                    {"dim": 1, "name": "Longitude", "nameTextStyle": {"color": "#64748b"}},
                    {"dim": 2, "name": "Intensity", "nameTextStyle": {"color": "#64748b"}}
                ],
                "parallel": {"left": "10%", "right": "15%", "bottom": "15%", "top": "20%"},
                "series": {"type": "parallel", "lineStyle": {"width": 1.5, "opacity": 0.4, "color": "#06b6d4"}, "data": parallel_data}
            }
            render_echarts(parallel_opt, height=350)

    with col_a2:
        st.markdown("""
        <div class="glass-card" style="margin-bottom:1rem;">
             <h4 style="margin:0; color:#ef4444;">🌊 DRIFT (WATERFALL)</h4>
        </div>
        """, unsafe_allow_html=True)
        # Show drift over last 5 steps
        drift_steps = []
        drift_labels = []
        for i in range(max(0, t_idx-4), t_idx+1):
            drift_steps.append(ClimateProcessor.calculate_global_mean(ds, var, i))
            drift_labels.append(f"T-{t_idx-i}" if i < t_idx else "LIVE")
        
        waterfall_data = []
        base_vals = [0]
        for i in range(1, len(drift_steps)):
            diff = drift_steps[i] - drift_steps[i-1]
            waterfall_data.append({"value": round(diff, 3), "itemStyle": {"color": "#ef4444" if diff > 0 else "#10b981"}})
            base_vals.append(round(drift_steps[i-1], 3) if diff > 0 else round(drift_steps[i], 3))
        
        waterfall_opt = {
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"left": "15%", "right": "5%", "top": "20%", "bottom": "15%"},
            "xAxis": {"type": "category", "data": drift_labels, "axisLabel": {"color": "#64748b", "fontSize": 9}},
            "yAxis": {"type": "value", "axisLabel": {"color": "#64748b", "fontSize": 9}},
            "series": [
                {"name": "Base", "type": "bar", "stack": "Total", "itemStyle": {"color": "transparent"}, "data": base_vals},
                {"name": "Change", "type": "bar", "stack": "Total", "data": [{"value": drift_steps[0], "itemStyle": {"color": "#38bdf8"}}] + waterfall_data}
            ]
        }
        render_echarts(waterfall_opt, height=350)
