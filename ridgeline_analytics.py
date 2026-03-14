import streamlit as st
import plotly.graph_objects as go
from backend.climate_processor import ClimateProcessor

def render_ridgeline_analytics(ds, controls):
    """Renders the Ridgeline/Joyplot visualization for monthly distributions."""
    var = controls["variable"]
    units = controls["units"]

    st.markdown("""
    <div class="section-tag">
        <span class="tag-line" style="background:linear-gradient(90deg,#8b5cf6,#ec4899)"></span>
        <h3 style="margin:0; font-size:1.25rem;">Ridgeline Intelligence — Vertical Distribution Analysis</h3>
    </div>
    <p style="color:#475569; font-size:0.92rem; margin-bottom:1.5rem;">
        Comparative analysis of variable density across months. Inspired by the 'Joy Division' aesthetic.
    </p>
    """, unsafe_allow_html=True)

    with st.spinner("Calculating Distribution Flux..."):
        df = ClimateProcessor.get_monthly_distributions(ds, var)

    if df.empty:
        st.warning("Distribution analysis not available for this data profile.")
        return

    # Create the Ridgeline Plot using plotly.graph_objects
    fig = go.Figure()
    
    # We'll use Violin plots with side='positive' to simulate ridgelines
    # Sort months for consistent display (Jan to Dec)
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    
    # Filter for months present in data
    available_months = [m for m in months if m in df['month'].unique()]
    
    # Reverse for better stacking aesthetic (Jan at top)
    available_months.reverse()

    for month in available_months:
        month_data = df[df['month'] == month]['val']
        
        # Determine color based on mean of month
        m_mean = month_data.mean()
        # Simple color mapping logic (using Plotly's Plasma/Inferno style)
        
        fig.add_trace(go.Violin(
            x=month_data,
            line_color='#8b5cf6',
            fillcolor='rgba(139, 92, 246, 0.5)',
            name=month,
            orientation='h',
            side='positive',
            width=3, # Vertical scale factor for overlap
            points=False,
            meanline_visible=True,
            showlegend=False
        ))

    fig.update_layout(
        height=700,
        xaxis=dict(
            title=f"{var.replace('_', ' ').title()} ({units})",
            gridcolor="rgba(51,65,85,0.2)",
            zeroline=False
        ),
        yaxis=dict(
            title="Month",
            gridcolor="rgba(51,65,85,0.2)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=20, b=40),
        violingap=0, # Maximum overlap
        violinmode='overlay',
        font=dict(color="#f1f5f9", family="Space Grotesk")
    )

    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 Ridgeline plots highlight shifts in probability density. Wide curves indicate high variability, while tall peaks show consistent regional patterns.")
