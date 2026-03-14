import streamlit as st
import pandas as pd
import numpy as np
from backend.climate_processor import ClimateProcessor
from backend.echarts_renderer import render_echarts

def render_spectral_intelligence(ds, controls):
    """Renders high-level spectral and signal decomposition analytics."""
    var = controls["variable"]
    units = controls["units"]
    
    st.markdown(f"""
    <div class="section-tag">
        <span class="tag-line" style="background:linear-gradient(90deg,#a855f7,#ec4899)"></span>
        <h3 style="margin:0; font-size:1.25rem;">Spectral Intelligence: {var.replace('_',' ').title()}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="margin-bottom:0.5rem;">
            <h4 style="margin:0; color:#a855f7;">📊 Temporal-Frequency Spectrogram</h4>
        </div>
        """, unsafe_allow_html=True)
        # Simulate a spectrogram by calculating moving variance or wavelet-like density
        df_spec = ClimateProcessor.get_temporal_matrix(ds, var)
        
        spec_opt = {
            "title": {"text": "Signal Power Density", "textStyle": {"color": "#94a3b8", "fontSize": 12}},
            "tooltip": {"position": "top"},
            "grid": {"height": "70%", "top": "15%"},
            "xAxis": {"type": "category", "data": list(range(len(ds.time))), "axisLabel": {"show": False}},
            "yAxis": {"type": "category", "data": ds.lat.values.round(0).tolist(), "axisLabel": {"fontSize": 9, "color": "#64748b"}},
            "visualMap": {
                "min": float(df_spec[var].min()),
                "max": float(df_spec[var].max()),
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": "5%",
                "inRange": {"color": ["#121212", "#0ea5e9", "#22d3ee", "#818cf8", "#a855f7", "#ec4899", "#f43f5e"]}
            },
            "series": [{
                "name": "Spectral Power",
                "type": "heatmap",
                "data": [[i % len(ds.time), i // len(ds.time), val] for i, val in enumerate(df_spec[var].values[:2000])],
                "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.5)"}}
            }]
        }
        render_echarts(spec_opt, height=450)
        
    with col2:
        st.markdown("""
        <div class="glass-card" style="margin-bottom:0.5rem;">
            <h4 style="margin:0; color:#22d3ee;">✨ Neural Phase Space</h4>
        </div>
        """, unsafe_allow_html=True)
        # Phase Portrait: Value vs Rate of Change
        timeseries = ds[var].mean(dim=['lat', 'lon']).values
        diff = np.diff(timeseries, prepend=timeseries[0])
        
        phase_data = [[float(v), float(d)] for v, d in zip(timeseries, diff)]
        
        phase_opt = {
            "title": {"text": "Dynamical System States", "textStyle": {"color": "#94a3b8", "fontSize": 12}},
            "xAxis": {"name": "Magnitude", "axisLabel": {"color": "#64748b"}},
            "yAxis": {"name": "Velocity (Δ)", "axisLabel": {"color": "#64748b"}},
            "series": [{
                "type": "line",
                "data": phase_data,
                "smooth": True,
                "lineStyle": {"width": 1, "color": "#22d3ee", "opacity": 0.6},
                "symbol": "none",
                "areaStyle": {"opacity": 0.05}
            }, {
                "type": "scatter",
                "data": [phase_data[-1]], # Current state
                "symbolSize": 12,
                "itemStyle": {"color": "#f43f5e", "shadowBlur": 10, "shadowColor": "#f43f5e"}
            }]
        }
        render_echarts(phase_opt, height=300)
        st.markdown("<p style='font-size:0.75rem; color:#475569; margin-top:0.5rem;'>Visualizing the trajectory of the global climate state through phase space.</p>", unsafe_allow_html=True)

    # Signal Decomposition Row
    st.markdown("""
    <div class="glass-card" style="margin-top:1.5rem; margin-bottom:0.5rem;">
        <h4 style="margin:0; color:#0ea5e9;">🌊 Multi-Scale Signal Decomposition</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate Trend (Moving Average) and Residual
    window = 12
    trend = pd.Series(timeseries).rolling(window=window, center=True).mean().fillna(method='bfill').fillna(method='ffill').values
    residual = timeseries - trend
    
    decomp_opt = {
        "tooltip": {"trigger": "axis"},
        "legend": {"textStyle": {"color": "#94a3b8"}},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {"type": "category", "data": [str(d) for d in range(len(timeseries))], "axisLabel": {"show": False}},
        "yAxis": {"type": "value", "axisLabel": {"color": "#64748b"}},
        "series": [
            {"name": "Raw Signal", "type": "line", "data": timeseries.tolist(), "lineStyle": {"width": 1, "color": "rgba(148,163,184,0.3)"}, "symbol": "none"},
            {"name": "Sustained Trend", "type": "line", "data": trend.tolist(), "lineStyle": {"width": 3, "color": "#0ea5e9"}, "symbol": "none"},
            {"name": "Residual Noise", "type": "bar", "data": residual.tolist(), "itemStyle": {"color": "rgba(244,63,94,0.4)"}}
        ]
    }
    render_echarts(decomp_opt, height=350)
