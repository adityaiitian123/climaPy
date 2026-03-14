import streamlit as st
import pandas as pd
import numpy as np
from backend.climate_processor import ClimateProcessor
from backend.echarts_renderer import render_echarts
from backend.scifi_predictor import ScifiPredictor
from frontend.components.knowledge_hub import KnowledgeHub

# ─── 6 GUIDED CLIMATE STORY STOPS ─────────────────────────────────────────────
STORY_STEPS = [
    {
        "title": "🌡️ Act I: The Rising Baseline",
        "var_hint": "temperature",
        "time_idx": -1,
        "zoom_lat": 0, "zoom_lon": 0,
        "region": "Global",
        "base_desc": "The long-term record reveals unmistakable warming. The final time slice is warmer than the first across nearly every latitude band — a planetary shift visible in the data.",
        "fact": "💡 Did You Know? The last decade (2014–2024) was the warmest decade ever recorded in human history, beating the previous record by 0.23°C.",
        "fact_color": "#ef4444"
    },
    {
        "title": "🧊 Act II: Arctic Amplification",
        "var_hint": "temperature",
        "time_idx": 0,
        "zoom_lat": 75, "zoom_lon": 0,
        "region": "Arctic Circle",
        "base_desc": "The Arctic is warming 3–4× faster than the global average — a phenomenon called Arctic Amplification. Sea ice extent shrinks every decade, creating feedback loops that accelerate global warming.",
        "fact": "💡 Did You Know? The Arctic Ocean is expected to be ice-free in summer by the 2040s. This opens new shipping routes but devastates polar ecosystems.",
        "fact_color": "#38bdf8"
    },
    {
        "title": "🌧️ Act III: Monsoon Disruption",
        "var_hint": "precipitation",
        "time_idx": 12,
        "zoom_lat": 20, "zoom_lon": 80,
        "region": "South Asia",
        "base_desc": "Changing sea surface temperatures are shifting monsoon rainfall patterns. Some regions receive more intense precipitation, others face prolonged drought — an existential threat to agriculture.",
        "fact": "💡 Did You Know? India's summer monsoon accounts for 70% of annual rainfall. A 10% disruption could lead to food insecurity for 600 million people.",
        "fact_color": "#06b6d4"
    },
    {
        "title": "🌊 Act IV: El Niño Fingerprint",
        "var_hint": "temperature",
        "time_idx": 24,
        "zoom_lat": 0, "zoom_lon": -120,
        "region": "Pacific Ocean",
        "base_desc": "The equatorial Pacific shows a distinct warm anomaly — characteristic of El Niño. This oceanic-atmospheric coupling drives extreme weather events globally, from Australian droughts to California floods.",
        "fact": "💡 Did You Know? The 2015–2016 El Niño was the strongest on record, causing $17 billion in damages and affecting 60 million people.",
        "fact_color": "#f59e0b"
    },
    {
        "title": "🔥 Act V: Heatwave Hotspots",
        "var_hint": "temperature",
        "time_idx": -1,
        "zoom_lat": 45, "zoom_lon": 20,
        "region": "Europe & Central Asia",
        "base_desc": "High-latitude land masses show the most severe temperature extremes. The data reveals persistent above-normal temperatures across regions historically unaccustomed to heat stress.",
        "fact": "💡 Did You Know? Europe's 2003 heatwave killed 70,000 people. Climate models project similar events to occur every other year by 2050.",
        "fact_color": "#f97316"
    },
    {
        "title": "🌿 Act VI: The New Normal",
        "var_hint": "temperature",
        "time_idx": -1,
        "zoom_lat": 0, "zoom_lon": 0,
        "region": "Global Assessment",
        "base_desc": "Comparing the dataset's first and final frames reveals the full scope of change. What was an anomaly 50 years ago is now the baseline. The climate system has shifted — and our choices today will determine how far it goes.",
        "fact": "💡 Did You Know? At current rates, limiting warming to 1.5°C requires halving global emissions by 2030 and reaching net-zero by 2050.",
        "fact_color": "#10b981"
    },
]

def _get_var_for_step(ds, step):
    """Try to use the hinted variable, fall back to first available."""
    hint = step.get("var_hint", "temperature")
    for v in ds.data_vars:
        if hint in v.lower():
            return v
    return list(ds.data_vars)[0]

def render_story_mode(ds, controls):
    """6-stop cinematic guided tour with progress bar, anomaly spotlight, and Did You Know cards."""

    st.markdown("""
    <div class="section-tag">
        <span class="tag-line" style="background:linear-gradient(90deg,#f59e0b,#38bdf8)"></span>
        <h3 style="margin:0; font-size:1.25rem;">Executive Briefing: Climate Story Mode</h3>
    </div>
    <p style="color:#475569; font-size:0.92rem; margin-bottom:0.5rem;">
        A guided, narrative-driven tour through the most important climate signals in this dataset.
    </p>""", unsafe_allow_html=True)

    if 'story_step' not in st.session_state:
        st.session_state.story_step = 0
    if 'ai_narratives' not in st.session_state:
        st.session_state.ai_narratives = {}

    step_idx = st.session_state.story_step
    current_step = STORY_STEPS[step_idx]
    n_steps = len(STORY_STEPS)
    step_var = _get_var_for_step(ds, current_step)
    step_t_idx = current_step['time_idx']
    if step_t_idx < 0:
        step_t_idx = max(0, len(ds.time) + step_t_idx)

    # ─── PROGRESS BAR ─────────────────────────────────────────────────────────
    progress = (step_idx + 1) / n_steps
    step_dots = "".join([
        f'<span style="display:inline-block; width:10px; height:10px; border-radius:50%; margin:0 3px; '
        f'background:{"#38bdf8" if i == step_idx else "#1e293b"}; '
        f'border:1px solid {"#38bdf8" if i <= step_idx else "#334155"}; '
        f'box-shadow:{"0 0 8px #38bdf8" if i == step_idx else "none"};"></span>'
        for i in range(n_steps)
    ])
    st.markdown(f"""
    <div style="margin-bottom:0.8rem;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
            <div style="font-size:0.68rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em;">
                Dossier Fragment {step_idx+1} of {n_steps}
            </div>
            <div style="display:flex; align-items:center;">{step_dots}</div>
        </div>
        <div style="background:#1e293b; border-radius:4px; height:4px; overflow:hidden;">
            <div style="background:linear-gradient(90deg,#38bdf8,#818cf8);
                        width:{progress*100:.0f}%; height:100%; border-radius:4px;
                        transition:width 0.4s ease;"></div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ─── NAVIGATION ───────────────────────────────────────────────────────────
    col_nav1, col_nav2, col_nav3 = st.columns([1, 4, 1])
    with col_nav1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(step_idx == 0)):
            st.session_state.story_step -= 1
            st.rerun()
    with col_nav2:
        st.markdown(f"""<div style="text-align:center; padding:8px 0;">
            <span style="color:#38bdf8; font-weight:700; font-size:1rem;">{current_step['title']}</span>
            <span style="color:#475569; font-size:0.8rem; margin-left:0.5rem;">📍 {current_step['region']}</span>
        </div>""", unsafe_allow_html=True)
    with col_nav3:
        if st.button("Next ➡️", use_container_width=True, disabled=(step_idx == n_steps - 1)):
            st.session_state.story_step += 1
            st.rerun()

    # ─── MAIN CONTENT ─────────────────────────────────────────────────────────
    col_text, col_viz = st.columns([1, 2])

    with col_text:
        # Narrative card
        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid #f59e0b; padding: 1.2rem; margin-bottom:1rem;">
            <p style="font-size: 0.95rem; color: #94a3b8; line-height: 1.6; margin:0;">{current_step['base_desc']}</p>
        </div>""", unsafe_allow_html=True)

        # Knowledge Hub Integration
        if st.session_state.get("ui_mode") == "public":
            KnowledgeHub.render_infotip(current_step.get("var_hint").capitalize())
            if "Anomalies" in current_step['base_desc']:
                KnowledgeHub.render_infotip("Anomalies")

        # AI Narrator
        if step_idx not in st.session_state.ai_narratives:
            with st.spinner("🤖 AI Analyst processing data..."):
                try:
                    stats = ClimateProcessor.get_statistical_summary(ds, step_var, step_t_idx)
                    predictor = ScifiPredictor()
                    narrative = predictor.generate_story_narrative(step_var, current_step['title'], stats)
                    st.session_state.ai_narratives[step_idx] = narrative
                    st.rerun()
                except Exception as e:
                    st.session_state.ai_narratives[step_idx] = "AI uplink unavailable — data patterns remain significant."

        if step_idx in st.session_state.ai_narratives:
            st.markdown(f"""
            <div style="background:rgba(16,185,129,0.08); border:1px solid #10b981;
                        padding:1rem; border-radius:8px; margin-top:0.8rem;
                        box-shadow: 0 0 15px rgba(16,185,129,0.15);">
                <div style="font-size:0.65rem; color:#10b981; text-transform:uppercase;
                             letter-spacing:0.12em; margin-bottom:0.4rem; font-weight:700;">
                    [AI CORE NARRATIVE — ACTIVE]
                </div>
                <div style="color:#f1f5f9; font-size:0.92rem; line-height:1.55;">
                    {st.session_state.ai_narratives[step_idx]}
                </div>
            </div>""", unsafe_allow_html=True)

        # Did You Know card
        st.markdown(f"""
        <div style="background:rgba(15,23,42,0.8); border:1px solid {current_step['fact_color']}40;
                    border-left:3px solid {current_step['fact_color']};
                    padding:0.9rem 1rem; border-radius:8px; margin-top:0.8rem;">
            <div style="font-size:0.85rem; color:{current_step['fact_color']}; line-height:1.55;">
                {current_step['fact']}
            </div>
        </div>""", unsafe_allow_html=True)

        # Download dossier
        dossier_text = f"""PYCLIMAEXPLORER — CLIMATE DOSSIER
Stop {step_idx+1}: {current_step['title']}
Region: {current_step['region']}

BRIEFING:
{current_step['base_desc']}

AI ANALYSIS:
{st.session_state.ai_narratives.get(step_idx, 'N/A')}

CLIMATE FACT:
{current_step['fact']}
"""
        st.download_button(
            "⬇ Download Stop Dossier",
            data=dossier_text,
            file_name=f"dossier_stop_{step_idx+1}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col_viz:
        st.markdown("""
        <div class="glass-card" style="margin-bottom:0.5rem;">
            <h4 style="margin:0; color:#38bdf8; font-size:0.9rem;">🛰️ Orbital Intelligence Perspective</h4>
        </div>
        """, unsafe_allow_html=True)

        df_story = ClimateProcessor.get_spatial_slice(ds, step_var, step_t_idx)
        top_anomaly = ClimateProcessor.get_top_anomaly_regions(ds, step_var, step_t_idx, n=15)

        if not df_story.empty:
            df_clean = df_story.dropna(subset=[step_var])
            records = df_clean[['lon', 'lat', step_var]].values.tolist()

            # Anomaly spotlight data
            spotlight_series = []
            if not top_anomaly.empty:
                pos_pts = top_anomaly[top_anomaly['anomaly'] > 0][['lon', 'lat', 'anomaly']].values.tolist()
                neg_pts = top_anomaly[top_anomaly['anomaly'] < 0][['lon', 'lat', 'anomaly']].values.tolist()
                if pos_pts:
                    spotlight_series.append({
                        "name": "Hot Spot", "type": "effectScatter",
                        "coordinateSystem": "geo", "data": pos_pts[:8],
                        "symbolSize": 16,
                        "rippleEffect": {"brushType": "fill", "period": 2.5, "scale": 4},
                        "itemStyle": {"color": current_step['fact_color'],
                                      "shadowBlur": 20, "shadowColor": current_step['fact_color']}
                    })

            map_option = {
                "backgroundColor": "transparent",
                "tooltip": {"trigger": "item"},
                "visualMap": {
                    "min": float(df_clean[step_var].min()),
                    "max": float(df_clean[step_var].max()),
                    "calculable": True,
                    "inRange": {"color": ['#00f2fe','#4facfe','#7161ef','#9b5de5','#f15bb5','#fee440','#00bbf9','#00f5d4','#f59e0b','#ef4444']},
                    "textStyle": {"color": "#94a3b8"}, "left": "right", "bottom": "5%"
                },
                "geo": {
                    "map": "world", "roam": True,
                    "center": [current_step['zoom_lon'], current_step['zoom_lat']],
                    "zoom": 2.0 if current_step['region'] != "Global Assessment" else 1.1,
                    "itemStyle": {"areaColor": "rgba(30,41,59,0.4)",
                                  "borderColor": "rgba(56,189,248,0.4)", "borderWidth": 1.5},
                    "emphasis": {"itemStyle": {"areaColor": "rgba(56,189,248,0.15)"}}
                },
                "series": [
                    {"name": step_var.title(), "type": "scatter", "coordinateSystem": "geo",
                     "data": records, "symbolSize": 9,
                     "itemStyle": {"opacity": 0.9, "shadowBlur": 8, "shadowColor": "rgba(255,255,255,0.5)"}},
                    *spotlight_series
                ]
            }
            render_echarts(map_option, height=480, key=f"story_map_{step_idx}", use_map=True)

        # Terminate
