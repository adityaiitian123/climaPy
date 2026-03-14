import streamlit as st
import pandas as pd
import numpy as np
import time
from backend.climate_processor import ClimateProcessor
from backend.scifi_predictor import ScifiPredictor
from backend.echarts_renderer import render_echarts

def render_scifi_analyst(ds, controls):
    """Renders the AI-powered Scifi Analyst intelligence briefing and future projections."""
    var = controls["variable"]
    t_idx = controls["time_index"]
    units = controls["units"]

    st.markdown(f"""
    <div class="section-tag">
        <span class="tag-line" style="background:linear-gradient(90deg,#f59e0b,#ef4444)"></span>
        <h3 style="margin:0; font-size:1.25rem;">AI Command Analysis: Project PyClima-Core</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div class='glass-card' style='margin-bottom:1.5rem;'>
            <h3 style='margin:0; color:#38bdf8;'>🛰️ Intelligence Briefing</h3>
            <p style='color:#64748b; font-size:0.85rem; margin-top:0.5rem;'>Advanced planetary telemetry analysis via PyClima-Core neural link.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("RUN DEEP ANALYSIS", type="primary", use_container_width=True):
            with st.status("Initializing AI Core...", expanded=True) as status:
                try:
                    stats = ClimateProcessor.get_statistical_summary(ds, var, t_idx)
                    predictor = ScifiPredictor()
                    
                    st.write("Fetching telemetry...")
                    time.sleep(0.5)
                    st.write("Synthesizing planetary trends...")
                    
                    briefing = predictor.generate_intelligence_briefing(ds, var, stats)
                    status.update(label="Analysis Complete", state="complete", expanded=False)
                    
                    st.markdown(f"""
                    <div style="background:rgba(2,6,23,0.9); border:1px solid #10b981; padding:1.2rem; border-radius:8px; 
                                font-family:'JetBrains Mono', 'Courier New', monospace; color:#10b981; font-size:0.85rem; line-height:1.5;
                                box-shadow: inset 0 0 20px rgba(16,185,129,0.1), 0 0 30px rgba(16,185,129,0.15);">
                        <div style="color:#64748b; margin-bottom:0.8rem; border-bottom:1px solid rgba(16,185,129,0.2); padding-bottom:4px; font-weight:700;">
                            [PYCLIMA-CORE SECURE TRANSMISSION]
                        </div>
                        {briefing.replace('\n', '<br>')}
                        <div style="margin-top:1.2rem; color:#64748b; font-size:0.7rem; border-top:1px solid rgba(16,185,129,0.2); padding-top:4px;">
                            TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}  |  ID: PC-ALPHA-{int(time.time())%10000}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"INTELLIGENCE FAILURE: {e}")
        else:
            st.info("System Standby. Awaiting command to initialize Deep Analysis.")
            st.markdown("""
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:2rem; opacity:0.6;">
                <svg width="120" height="120" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="#38bdf8" stroke-width="0.5" stroke-dasharray="10 5">
                        <animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="20s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="50" cy="50" r="35" fill="none" stroke="#818cf8" stroke-width="1" stroke-dasharray="1 10">
                        <animateTransform attributeName="transform" type="rotate" from="360 50 50" to="0 50 50" dur="10s" repeatCount="indefinite"/>
                    </circle>
                </svg>
                <div style="margin-top:1rem; font-family:'Space Grotesk', sans-serif; color:#38bdf8; font-size:0.7rem; letter-spacing:0.2em; animation: pulse 2s infinite;">PLANETARY LINK ACTIVE</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='glass-card' style='margin-bottom:1.5rem;'>
            <h3 style='margin:0; color:#38bdf8;'>🔮 Predictive Projection</h3>
            <p style='color:#64748b; font-size:0.85rem; margin-top:0.5rem;'>Stochastic simulation of future climatic states (±1.5σ uncertainty).</p>
        </div>
        """, unsafe_allow_html=True)
        
        predictor = ScifiPredictor()
        future_data = predictor.get_future_projection(ds, var)
        historical_data = ds[var].mean(dim=['lat', 'lon']).values.tolist()
        
        # Calculate confidence bands for projection
        std_hist = float(np.std(historical_data))
        future_upper = [f + (std_hist * (0.5 + i*0.1)) for i, f in enumerate(future_data)]
        future_lower = [f - (std_hist * (0.5 + i*0.1)) for i, f in enumerate(future_data)]
        
        labels = [f"T{i}" for i in range(len(historical_data) + len(future_data))]
        split_idx = len(historical_data)

        # Build chart data
        hist_series = historical_data + [None] * len(future_data)
        proj_series = [None] * (split_idx - 1) + [historical_data[-1]] + future_data
        upper_band  = [None] * (split_idx - 1) + [historical_data[-1]] + future_upper
        lower_band  = [None] * (split_idx - 1) + [historical_data[-1]] + future_lower

        option = {
            "backgroundColor": "transparent",
            "tooltip": {"trigger": "axis", "backgroundColor": "rgba(15,23,42,0.9)", "borderColor": "#38bdf8", "borderWidth": 1},
            "legend": {"data": ["Historical", "AI Projection", "Confidence Band"], "textStyle": {"color": "#64748b"}, "top": 10},
            "xAxis": {"type": "category", "data": labels, "axisLabel": {"show": False}, "axisLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}},
            "yAxis": {"type": "value", "name": units, "axisLabel": {"color": "#64748b"}, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.03)"}}},
            "series": [
                {
                    "name": "Confidence Band", "type": "line", "data": upper_band, "showSymbol": False,
                    "lineStyle": {"opacity": 0}, "stack": "confidence", "silent": True,
                    "areaStyle": {"color": "transparent"}
                },
                {
                    "name": "Confidence Band", "type": "line", "data": lower_band, "showSymbol": False,
                    "lineStyle": {"opacity": 0}, "stack": "confidence", "silent": True,
                    "areaStyle": {"color": "rgba(168,85,247,0.1)", "origin": "start"}
                },
                {
                    "name": "Historical", "type": "line", "smooth": True, "data": hist_series,
                    "lineStyle": {"width": 3, "color": "#38bdf8"},
                    "areaStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                  "colorStops": [{"offset": 0, "color": "rgba(56,189,248,0.2)"}, {"offset": 1, "color": "transparent"}]}}
                },
                {
                    "name": "AI Projection", "type": "line", "smooth": True, "data": proj_series,
                    "lineStyle": {"width": 3, "type": "dashed", "color": "#f59e0b"},
                    "areaStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                  "colorStops": [{"offset": 0, "color": "rgba(245,158,11,0.1)"}, {"offset": 1, "color": "transparent"}]}},
                    "markPoint": {"data": [{"type": "max", "name": "Peak", "itemStyle": {"color": "#ef4444"}}]}
                }
            ],
            "grid": {"left": "10%", "right": "5%", "bottom": "15%", "top": "20%"}
        }
        
        render_echarts(option, height=400)
