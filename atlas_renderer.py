import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

class InteractiveAtlasRenderer:
    """Renders high-performance climate visualizations with absolute stability."""
    
    @staticmethod
    def render_interactive_atlas(df, var, units, title):
        """☢️ THE NUCLEAR BYPASS: Raw dictionary rendering. 100% constructor-free."""
        if df is None or df.empty:
            st.warning("No data found for planetary projection.")
            return

        # Prepare raw data lists for 100% stability
        lats = df['lat'].tolist()
        lons = df['lon'].tolist()
        hover_text = df[var].apply(lambda x: f"{x:.2f} {units}").tolist()

        # 🛸 THE TOTAL DICTIONARY BYPASS
        # This structure avoids ALL Plotly object constructors (go.Scattergeo, go.Figure, etc.)
        # and therefore bypasses the broken validation logic in experimental Python 3.14.
        fig_dict = {
            "data": [{
                "type": "scattergeo",
                "lat": lats,
                "lon": lons,
                "mode": "markers",
                "marker": {
                    "size": 3,
                    "color": "#38bdf8",
                    "opacity": 0.8,
                    "showscale": False,
                    "line": {"width": 0}
                },
                "hoverinfo": "text",
                "text": hover_text
            }],
            "layout": {
                "title": {"text": title, "font": {"color": "#e2e8f0"}},
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "margin": {"t": 40, "b": 0, "l": 0, "r": 0},
                "geo": {
                    "projection": {"type": "orthographic"},
                    "showland": True,
                    "landcolor": "#1e293b",
                    "showcoastlines": True,
                    "coastlinecolor": "#334155",
                    "showocean": True,
                    "oceancolor": "#0f172a",
                    "bgcolor": "rgba(0,0,0,0)",
                    "showcountries": True,
                    "countrycolor": "#334155"
                },
                "height": 600
            }
        }

        try:
            st.plotly_chart(fig_dict, use_container_width=True)
        except Exception as e:
            st.info(f"💡 Visualizer in Absolute Safe Mode: {e}")
            return

    @staticmethod
    def render_climate_zone_legend():
        """Compact legend for the climate zones map."""
        zones = [
            ("Tropical", "#ef4444"),
            ("Dry/Arid", "#f59e0b"),
            ("Temperate", "#10b981"),
            ("Continental", "#3b82f6"),
            ("Polar", "#8b5cf6")
        ]
        
        for name, color in zones:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.4rem;">
                <div style="width:12px; height:12px; border-radius:3px; background:{color};"></div>
                <div style="font-size:0.75rem; color:#94a3b8;">{name}</div>
            </div>
            """, unsafe_allow_html=True)

    @staticmethod
    def get_layout_template():
        """Returns a dark theme template for all Plotly charts."""
        # Note: Using standard dict for absolute stability in Python 3.14
        return {
            "layout": {
                "plot_bgcolor": "rgba(0,0,0,0)",
                "paper_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "#94a3b8", "size": 10},
                "xaxis": {
                    "showgrid": False,
                    "zeroline": False,
                    "tickfont": {"color": "#64748b"}
                },
                "yaxis": {
                    "showgrid": True,
                    "gridcolor": "rgba(255,255,255,0.05)",
                    "zeroline": False,
                    "tickfont": {"color": "#64748b"}
                },
                "colorway": ["#38bdf8", "#818cf8", "#c084fc", "#e879f9", "#fb7185"]
            }
        }
