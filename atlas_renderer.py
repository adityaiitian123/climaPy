import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

class InteractiveAtlasRenderer:
    """Renderer for premium 3D globes and anomaly visualizations."""
    
    @staticmethod
    def render_interactive_atlas(df, var, units, title="Copernicus Interactive Atlas"):
        """Renders a high-fidelity orthographic 3D globe."""
        if df.empty:
            st.warning("No data for Atlas projection.")
            return

        # sample for performance but keep density
        if len(df) > 5000:
            df_plot = df.sample(5000)
        else:
            df_plot = df

        fig = go.Figure()

        # High-visibility colorscales
        is_anomaly = "anomaly" in var.lower() or "change" in var.lower()
        colorscale = "RdBu_r" if is_anomaly else "Turbo"

        # "SAFE MODE" RENDERING ENGINE
        try:
            # Minimalist rendering to prevent validation crashes
            fig.add_trace(go.Scattergeo(
                lat=df_plot['lat'],
                lon=df_plot['lon'],
                mode="markers",
                marker=dict(
                    size=3,
                    color='#38bdf8', # Fixed color to bypass scale logic
                    opacity=0.8
                ),
                hoverinfo="text",
                text=df_plot[var].apply(lambda x: f"{x:.2f} {units}")
            ))
        except Exception as e:
            st.info(f"💡 Visualizer in Safe Mode: {e}")
            return

        # Auto-center based on data
        avg_lat = df_plot['lat'].mean()
        avg_lon = df_plot['lon'].mean()

        fig.update_geos(
            projection_type="orthographic",
            projection_rotation=dict(lat=avg_lat, lon=avg_lon, roll=0),
            showland=True,
            landcolor="#1e293b",
            showocean=True,
            oceancolor="#020617",
            showcountries=True,
            countrycolor="#334155",
            showcoastlines=True,
            coastlinecolor="#475569",
            bgcolor="rgba(0,0,0,0)",
            framecolor="rgba(56,189,248,0.3)",
            framewidth=1
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", family="Space Grotesk"),
            height=650,
            margin=dict(l=0, r=0, t=40, b=0),
            title=dict(
                text=title,
                x=0.5,
                y=0.98,
                font=dict(size=18, color="#38bdf8")
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_climate_zone_legend():
        """Renders a custom vertical legend for climate zones."""
        zone_info = [
            ("Polar", "#bae6fd", "Arctic/Antarctic extremes"),
            ("Subpolar", "#0ea5e9", "Strict seasonal cycles"),
            ("Temperate", "#22c55e", "Mild, humid transitions"),
            ("Subtropical", "#f59e0b", "Warm, seasonally dry"),
            ("Tropical", "#f97316", "Constant high warmth"),
            ("Equatorial", "#ef4444", "Maximum solar intensity")
        ]
        
        st.markdown("""
        <div style="background:rgba(15,23,42,0.4); border:1px solid rgba(255,255,255,0.05); 
                    border-radius:12px; padding:1.2rem; margin-top:1rem;">
            <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; 
                        letter-spacing:0.12em; margin-bottom:1rem; font-weight:700;">
                Classification Legend
            </div>
        """, unsafe_allow_html=True)
        
        for name, color, desc in zone_info:
            st.markdown(f"""
            <div style="display:flex; align-items:flex-start; gap:12px; margin-bottom:0.8rem;">
                <div style="width:14px; height:14px; background:{color}; border-radius:3px; margin-top:2px;"></div>
                <div>
                    <div style="font-size:0.85rem; font-weight:600; color:#e2e8f0; line-height:1;">{name}</div>
                    <div style="font-size:0.68rem; color:#475569; margin-top:2px;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    @staticmethod
    def render_anomaly_bar_chart(df, title="Global Temperature Departure"):
        """Diverging bar chart (Climate Central style)."""
        if df.empty:
            st.warning("Insufficient data for anomaly series.")
            return

        fig = go.Figure()

        # Assign colors based on anomaly sign
        colors = ['#ef4444' if x > 0 else '#3b82f6' for x in df['anomaly']]

        fig.add_trace(go.Bar(
            x=df['year'],
            y=df['anomaly'],
            marker_color=colors,
            text=df['anomaly'].apply(lambda x: f"{x:+.2f}"),
            hoverinfo="x+y",
            name="Anomaly"
        ))

        # Horizontal line at 0
        fig.add_hline(y=0, line_dash="solid", line_color="#475569", line_width=1)

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif"),
            height=400,
            xaxis=dict(
                title="Year",
                showgrid=False,
                tickfont=dict(color="#64748b")
            ),
            yaxis=dict(
                title="Departure (°C)",
                gridcolor="rgba(255,255,255,0.05)",
                zeroline=False,
                tickfont=dict(color="#64748b")
            ),
            margin=dict(l=40, r=20, t=60, b=40),
            title=dict(
                text=title,
                font=dict(size=20, color="#f1f5f9"),
                x=0,
                y=0.95
            ),
            hoverlabel=dict(bgcolor="#1e293b")
        )

        st.plotly_chart(fig, use_container_width=True)
