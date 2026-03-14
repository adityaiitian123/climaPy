import streamlit as st
from backend.climate_processor import ClimateProcessor
from frontend.components.atlas_renderer import InteractiveAtlasRenderer

def render_anomaly_pulse(ds, controls):
    """Renders the Climate Central style global anomaly bar chart."""
    st.markdown("""
    <div class="section-tag">
        <span class="tag-line" style="background:linear-gradient(90deg,#3b82f6,#ef4444)"></span>
        <h3 style="margin:0; font-size:1.25rem;">Planetary Temperature Pulse — Annual Anomaly Departure</h3>
    </div>
    <p style="color:#475569; font-size:0.92rem; margin-bottom:1.5rem;">
        Year-by-year global temperature anomalies relative to the historical baseline. 
        Deep blue indicates cooling, while vibrant red represents acceleration in warming.
    </p>
    """, unsafe_allow_html=True)

    with st.spinner("Analyzing Global Departure..."):
        df_anomaly = ClimateProcessor.get_global_anomaly_series(ds)

    if df_anomaly.empty:
        st.error("Dataset lacks temporal or thermal indices required for anomaly calculation.")
        return

    InteractiveAtlasRenderer.render_anomaly_bar_chart(df_anomaly)

    # Key Statistics for the Pulse
    last_val = df_anomaly['anomaly'].iloc[-1]
    peak_val = df_anomaly['anomaly'].max()
    avg_val = df_anomaly['anomaly'].mean()
    
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
        <div style="padding:1rem; background:rgba(239,68,68,0.05); border:1px solid rgba(239,68,68,0.2); border-radius:12px; text-align:center;">
            <div style="font-size:0.75rem; color:#ef4444; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;">Latest Departure</div>
            <div style="font-size:1.8rem; font-weight:700; color:#ef4444;">{last_val:+.2f}°C</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div style="padding:1rem; background:rgba(245,158,11,0.05); border:1px solid rgba(245,158,11,0.2); border-radius:12px; text-align:center;">
            <div style="font-size:0.75rem; color:#f59e0b; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;">Peak Anomaly</div>
            <div style="font-size:1.8rem; font-weight:700; color:#f59e0b;">{peak_val:+.2f}°C</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        trend_direction = "Warming" if avg_val > 0 else "Cooling"
        trend_color = "#ef4444" if avg_val > 0 else "#3b82f6"
        st.markdown(f"""
        <div style="padding:1rem; background:{trend_color}10; border:1px solid {trend_color}30; border-radius:12px; text-align:center;">
            <div style="font-size:0.75rem; color:{trend_color}; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;">Historical Trend</div>
            <div style="font-size:1.8rem; font-weight:700; color:{trend_color};">{trend_direction}</div>
        </div>
        """, unsafe_allow_html=True)
