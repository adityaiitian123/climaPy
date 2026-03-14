import streamlit as st
import pandas as pd
import numpy as np
from backend.research_helper import ResearchHelper
from backend.echarts_renderer import render_echarts
import textwrap

def render_research_analyst(ds, controls, ai_client=None):
    """Deep Research Lab: Dr. Aadhya AI Analyst terminal and pattern recognition."""
    var = controls["variable"]
    t_idx = controls["time_index"]
    
    st.markdown(textwrap.dedent("""
        <div class="section-tag">
            <span class="tag-line" style="background:linear-gradient(90deg,#94a3b8,#334155)"></span>
            <h3 style="margin:0; font-size:1.25rem;">Research Analyst Intelligence: Dr. Aadhya (v2.4)</h3>
        </div>
    """), unsafe_allow_html=True)

    # 1. SCIENTIST TERMINAL (Main Hub)
    col_a1, col_a2 = st.columns([2, 1])
    
    # Trigger Analysis
    report = ResearchHelper.generate_aadhya_report(ds, var, t_idx, ai_client=ai_client)

    with col_a1:
        # Added: NASA Verified Badge if applicable
        if report.get('is_nasa'):
            st.markdown("""
            <div style="background:rgba(14,165,233,0.1); border:1px solid rgba(14,165,233,0.3); border-radius:12px; padding:0.5rem 1rem; margin-bottom:1rem; display:flex; align-items:center; gap:10px;">
                <span style="color:#0ea5e9; font-size:1.2rem;">🛡️</span>
                <div>
                    <div style="font-size:0.65rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.1em;">Data Integrity</div>
                    <div style="font-size:0.85rem; color:#f1f5f9; font-weight:600;">NASA MERRA-2 AUTHENTICITY CERTIFIED</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="glass-card" style="margin-bottom:1rem;">
            <div style="font-family:'Space Grotesk', sans-serif; color:#94a3b8; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:0.5rem;">
                DR. AADHYA [AI ANALYST]
            </div>
            <div style="font-family:'Courier New', monospace; font-size:1.15rem; color:#f1f5f9; line-height:1.6; border-left:3px solid #38bdf8; padding-left:1.5rem; margin-bottom:1rem;">
                "{report['dialogue']}"
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grid Status
        cstatus1, cstatus2 = st.columns(2)
        with cstatus1:
            st.markdown(f"""
            <div style="padding:1rem; background:rgba(15,23,42,0.8); border:1px solid rgba(16,185,129,0.2); border-radius:8px;">
                <div style="font-size:0.7rem; color:#64748b; text-transform:uppercase; margin-bottom:0.5rem;">HEURISTIC STATUS</div>
                <div style="font-weight:600; color:#10b981; display:flex; align-items:center; gap:8px;">
                    <span class="status-dot"></span> SENSORY SYNC ACTIVE
                </div>
            </div>""", unsafe_allow_html=True)
        with cstatus2:
            st.markdown(f"""
            <div style="padding:1rem; background:rgba(15,23,42,0.8); border:1px solid rgba(56,189,248,0.2); border-radius:8px;">
                <div style="font-size:0.7rem; color:#64748b; text-transform:uppercase; margin-bottom:0.5rem;">MISSION LOG ID</div>
                <div style="font-family:monospace; color:#38bdf8;">{report['system_id']}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid rgba(56,189,248,0.1);">
            <div style="font-size:0.65rem; color:#475569; display:flex; justify-content:space-between;">
                <span>TRANSMISSION TIMESTAMP: {report['timestamp']}</span>
                <span>RESEARCH LEVEL: LEVEL 4 CLEARED</span>
            </div>
        </div>""", unsafe_allow_html=True)

    with col_a2:
        st.markdown("""
        <div class="glass-card" style="margin-bottom:0.5rem; text-align:center;">
            <div style='font-size:0.75rem; color:#64748b; margin-bottom:0.5rem;'>PATTERN COHERENCE SCORE</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Gauge for pattern strength
        score_val = float(report['pattern_score'])
        gauge_opt = {
            "series": [{
                "type": "gauge", "startAngle": 180, "endAngle": 0, "center": ["50%", "75%"], "radius": "100%",
                "min": 0, "max": 100,
                "progress": {"show": True, "width": 12, "itemStyle": {"color": "#ef4444" if score_val > 70 else "#0ea5e9"}},
                "axisLine": {"lineStyle": {"width": 12, "color": [[1, "rgba(255,255,255,0.05)"]]}},
                "axisTick": {"show": False}, "splitLine": {"show": False}, "axisLabel": {"show": False},
                "pointer": {"show": False},
                "detail": {"offsetCenter": [0, "-10%"], "formatter": f"{score_val:.1f}%", "color": "#f1f5f9", "fontSize": 24, "fontWeight": "bold"},
                "data": [{"value": score_val}]
            }]
        }
        render_echarts(gauge_opt, height=180)
        
        # Stability Card
        inst_val = report['cycles']['instability_index']
        inst_display = f"{inst_val:.3f}" if not np.isnan(inst_val) else "0.000"
        
        st.markdown(textwrap.dedent(f"""
        <div class="kpi-card {'red' if report['cycles']['is_volatile'] else 'cyan'}" style="margin-top:1rem;">
            <div class="kpi-label">CYCLICAL INSTABILITY</div>
            <div class="kpi-number" style="font-size:2rem;">{inst_display}</div>
            <div class="kpi-delta {'neg' if report['cycles']['is_volatile'] else 'pos'}">
                {"⚠️ HIGH VOLATILITY" if report['cycles']['is_volatile'] else "✅ STABLE CYCLE"}
            </div>
        </div>
        """), unsafe_allow_html=True)

    # 2. HIDDEN CLUSTER MAPPING
    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
    st.subheader("Planetary Spatial Clusters [Top Findings]")
    
    if report['clusters']:
        cols = st.columns(len(report['clusters']))
        for i, cluster in enumerate(report['clusters']):
            with cols[i]:
                # Color code based on type
                accent = "#ef4444" if cluster.get('type') == "WARMING" else "#0ea5e9"
                st.markdown(textwrap.dedent(f"""
                <div class="glass-card" style="padding:1rem; border-bottom:2px solid {accent}; border-radius:12px;">
                    <div style="font-size:0.65rem; color:#64748b; letter-spacing:0.1em; margin-bottom:0.4rem;">{cluster.get('type', 'CLUSTER')} {i+1}</div>
                    <div style="font-size:1.1rem; font-weight:700; color:#f1f5f9;">{cluster['intensity']} <span style='font-size:0.7rem; color:#475569;'>INDEX</span></div>
                    <div style="font-size:0.75rem; color:{accent}; font-weight:600; margin-top:0.4rem;">COORD: {cluster['lat']}N, {cluster['lon']}E</div>
                </div>
                """), unsafe_allow_html=True)
    else:
        st.info("Searching for significant spatial clusters in the grid...")

    # 3. RESEARCHER'S ANALYSIS CHART (Oscillations)
    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card" style="margin-bottom:1rem;">
        <h3 style="margin:0; font-size:1.25rem;">Global Oscillation Residuals</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Global mean residuals analysis
    ts_full = ds[var].mean(dim=['lat', 'lon']).to_series()
    # Synchronize window with backend: 3 for short data, 12 for long
    chart_window = 3 if len(ts_full) <= 24 else 12
    rolling = ts_full.rolling(window=chart_window, center=True).mean()
    residuals = (ts_full - rolling).dropna()
    
    # If still empty (very short data), use simple mean subtract
    if residuals.empty:
        residuals = (ts_full - ts_full.mean())

    if not residuals.empty:
        chart_opt = {
            "tooltip": {"trigger": "axis"},
            "grid": {"left": "5%", "right": "5%", "bottom": "15%", "top": "15%"},
            "xAxis": {"type": "category", "data": [str(d) for d in residuals.index], "axisLabel": {"show": False}},
            "yAxis": {"type": "value", "show": True, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}},
            "series": [{
                "name": "Residual Anomaly", "type": "bar", "data": [float(v) for v in residuals.tolist()],
                "itemStyle": {"color": "#ef4444", "opacity": 0.8},
                "markLine": {"data": [{"type": "average", "name": "Mean Line"}]}
            }]
        }
        render_echarts(chart_opt, height=300)
