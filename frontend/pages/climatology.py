import streamlit as st
import plotly.express as px
from backend.climate_processor import ClimateProcessor

def render_climatology(ds, controls):
    """Renders the Annual Climatology Mean Map."""
    var = controls["variable"]
    units = controls["units"]

    st.markdown("""
    <div class="section-tag">
        <span class="tag-line" style="background:linear-gradient(90deg,#06b6d4,#3b82f6)"></span>
        <h3 style="margin:0; font-size:1.25rem;">Annual Climatology — Historical Mean State</h3>
    </div>
    <p style="color:#475569; font-size:0.92rem; margin-bottom:1.5rem;">
        Spatial distribution of the temporal mean across the entire dataset duration.
    </p>
    """, unsafe_allow_html=True)

    with st.spinner("Synthesizing Climatology..."):
        df = ClimateProcessor.get_climatology_mean(ds, var)

    if df.empty:
        st.warning("Spatial averaging failed for this coordinate system.")
        return

    # Auto-centering logic
    avg_lat = float(df['lat'].mean())
    avg_lon = float(df['lon'].mean())
    lat_range = float(df['lat'].max() - df['lat'].min())
    lon_range = float(df['lon'].max() - df['lon'].min())
    max_dist = max(lat_range, lon_range)

    fig = px.scatter_geo(
        df, lat='lat', lon='lon', color='val',
        color_continuous_scale="Turbo",
        labels={'val': units},
        title=f"Mean {var.replace('_', ' ').title()}",
        opacity=0.8
    )

    fig.update_traces(marker=dict(size=5))
    
    fig.update_geos(
        showcoastlines=True, coastlinecolor="#475569",
        showland=True, landcolor="#1e293b",
        showocean=True, oceancolor="#0f172a",
        bgcolor="rgba(0,0,0,0)",
        center=dict(lat=avg_lat, lon=avg_lon),
        projection_scale=10 if max_dist < 5 else (5 if max_dist < 20 else 1.5)
    )

    fig.update_layout(
        height=600, margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title=units,
            thickness=15,
            len=0.5,
            bgcolor="rgba(15,23,42,0.8)",
            tickfont=dict(color="#f1f5f9")
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 Climatology provides the 'normal' state against which anomalies are typically measured.")
