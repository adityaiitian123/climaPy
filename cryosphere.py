import streamlit as st
import plotly.express as px
from backend.climate_processor import ClimateProcessor

def render_cryosphere(ds, controls):
    """Renders the Cryosphere Composition stacked area chart."""
    st.markdown("""
    <div class="section-tag">
        <span class="tag-line" style="background:linear-gradient(90deg,#94a3b8,#f1f5f9)"></span>
        <h3 style="margin:0; font-size:1.25rem;">Cryosphere Analytics — Composition Flux</h3>
    </div>
    <p style="color:#475569; font-size:0.92rem; margin-bottom:1.5rem;">
        Stacked analysis of sea ice extent and age categories (First-year vs Multi-year).
    </p>
    """, unsafe_allow_html=True)

    with st.spinner("Deconstructing Ice Age categories..."):
        df = ClimateProcessor.get_composition_series(ds)

    if df.empty:
        st.warning("Cryosphere decomposition not available for this data profile.")
        return

    # Create the stacked area chart
    fig = px.area(
        df, x="time", y="val", color="category",
        labels={"time": "Date", "val": "Relative Extent / Composition", "category": "Ice Category"},
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Blues_r
    )

    fig.update_layout(
        height=500,
        xaxis=dict(gridcolor="rgba(51,65,85,0.3)"),
        yaxis=dict(gridcolor="rgba(51,65,85,0.3)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 High multi-year ice content indicates a healthy, resilient ice sheet. Recent trends show a shift towards younger, thinner ice.")
