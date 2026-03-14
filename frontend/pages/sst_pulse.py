import streamlit as st
import plotly.express as px
from backend.climate_processor import ClimateProcessor

def render_sst_pulse(ds, controls):
    """Renders the multi-year 'spaghetti' plot for Climate Pulse verification."""
    var = controls["variable"]
    units = controls["units"]

    st.markdown("""
    <div class="section-tag">
        <span class="tag-line" style="background:linear-gradient(90deg,#ef4444,#f97316)"></span>
        <h3 style="margin:0; font-size:1.25rem;">Climate Pulse — Spaghetti Visualization</h3>
    </div>
    <p style="color:#475569; font-size:0.92rem; margin-bottom:1.5rem;">
        Daily global mean comparison across multiple years to identify record-breaking trends.
    </p>
    """, unsafe_allow_html=True)

    with st.spinner("Analyzing Multi-Year Flux..."):
        df = ClimateProcessor.get_spaghetti_data(ds, var)

    if df.empty:
        st.warning("Temporal spaghetti-grouping not available for this dataset.")
        return

    # Create the spaghetti plot
    fig = px.line(
        df, x="doy", y="val", color="year",
        line_group="year",
        labels={"doy": "Day of Year", "val": f"{var} ({units})", "year": "Year"},
        template="plotly_dark"
    )

    # Highlight the most recent year if multiple exist
    latest_year = df['year'].max()
    fig.update_traces(opacity=0.3) # Dim historical years
    
    # Re-apply full opacity to latest year
    for trace in fig.data:
        if str(latest_year) in trace.name:
            trace.line.width = 4
            trace.opacity = 1.0

    fig.update_layout(
        height=500,
        xaxis=dict(gridcolor="rgba(51,65,85,0.3)"),
        yaxis=dict(gridcolor="rgba(51,65,85,0.3)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"💡 This visualization mimics the C3S/ECMWF daily monitoring tool. Bold line represents {latest_year}.")
