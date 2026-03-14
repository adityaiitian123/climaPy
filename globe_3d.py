import streamlit as st
import pydeck as pdk
import numpy as np
import plotly.graph_objects as go
from backend.climate_processor import ClimateProcessor

def render_3d_globe(ds, controls):
    """Multi-mode 3D globe: Hexagon Towers | Column Grid | Heat Scatter | Plotly Globe."""
    var = controls["variable"]
    t_idx = controls["time_index"]
    units = controls["units"]

    st.markdown("""
    <div class="section-tag">
        <span class="tag-line" style="background:linear-gradient(90deg,#38bdf8,#818cf8)"></span>
        <h3 style="margin:0; font-size:1.25rem;">Global Intelligence Topography — 3D Earth</h3>
    </div>
    <p style="color:#475569; font-size:0.92rem; margin-bottom:1rem;">
        Interact with the planetary models below. Plotly Globe supports auto-rotation.
    </p>
    """, unsafe_allow_html=True)

    col_ctrl, col_globe = st.columns([1, 4])

    with col_ctrl:
        st.markdown("""
        <div class='glass-card' style='margin-bottom:1rem;'>
            <h4 style='margin:0; color:#38bdf8;'>🌍 Navigation</h4>
        </div>
        """, unsafe_allow_html=True)
        view_mode = st.radio(
            "Render Mode",
            ["🌐 Plotly Globe", "🔷 Hexagon Towers", "📊 Column Grid", "✨ Heat Scatter"],
            index=0
        )
        
        if "Plotly" not in view_mode:
            pitch = st.slider("Pitch Angle", 0, 70, 45)
            zoom = st.slider("Zoom", 1, 5, 2)
            elev_scale = st.slider("Elevation Scale", 1000, 30000, 8000, step=1000,
                                    help="Exaggerates the height of towers for dramatic effect")
        else:
            st.info("💡 Rotating Globe is interactive and supports animation via 'Play' in the chart menu.")

    with col_globe:
        df_3d = ClimateProcessor.get_spatial_slice(ds, var, t_idx)

        if df_3d.empty:
            st.warning("No data available for 3D projection.")
            return

        df_3d = df_3d.dropna(subset=[var]).rename(columns={var: 'val'})
        df_3d = df_3d[['lon', 'lat', 'val']].astype(float)
        df_3d['val_abs'] = df_3d['val'].abs()

        if "Plotly" in view_mode:
            from frontend.components.atlas_renderer import InteractiveAtlasRenderer
            InteractiveAtlasRenderer.render_interactive_atlas(df_3d, 'val', units, title=f"Planetary Intelligence: {var.replace('_',' ').title()}")
        else:
            # ─── PYDECK GLOBE IMPLEMENTATION ──────────────────────────────────────
            avg_lat = float(df_3d['lat'].mean())
            avg_lon = float(df_3d['lon'].mean())

            COLOR_RANGE = [
                [0, 242, 254],    # Cyan
                [79, 172, 254],   # Sky Blue
                [113, 97, 239],   # Purple
                [241, 91, 181],   # Pink
                [254, 228, 64],   # Yellow
                [239, 68, 68]     # Red (Critical)
            ]

            view_state = pdk.ViewState(
                latitude=avg_lat, longitude=avg_lon,
                zoom=zoom, pitch=pitch, bearing=0
            )

            if "Hexagon" in view_mode:
                layer = pdk.Layer(
                    "HexagonLayer", data=df_3d,
                    get_position=["lon", "lat"],
                    get_elevation_weight="val_abs",
                    elevation_scale=elev_scale,
                    elevation_range=[500, 150000],
                    extruded=True, radius=150000,
                    coverage=0.85, pickable=True,
                    auto_highlight=True,
                    color_range=COLOR_RANGE,
                )
            elif "Column" in view_mode:
                # Normalize values to 0-1 for elevation
                v_min, v_max = df_3d['val'].min(), df_3d['val'].max()
                df_3d['norm_val'] = ((df_3d['val'] - v_min) / (v_max - v_min + 1e-9)).clip(0, 1)
                df_3d['r'] = (df_3d['norm_val'] * 239 + 16).astype(int)
                df_3d['g'] = ((1 - df_3d['norm_val']) * 200).astype(int)
                df_3d['b'] = 254
                layer = pdk.Layer(
                    "ColumnLayer", data=df_3d,
                    get_position=["lon", "lat"],
                    get_elevation="val_abs",
                    elevation_scale=elev_scale,
                    radius=80000,
                    get_fill_color=["r", "g", "b", 230],
                    pickable=True,
                    auto_highlight=True,
                    extruded=True,
                )
            else:  # Heat Scatter
                layer = pdk.Layer(
                    "HeatmapLayer", data=df_3d,
                    get_position=["lon", "lat"],
                    get_weight="val_abs",
                    radius_pixels=40,
                    intensity=1, threshold=0.1,
                    color_range=[[0,0,255,0],[0,255,255,128],[0,255,0,200],[255,255,0,220],[255,165,0,230],[255,0,0,255]]
                )

            r = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                map_style="mapbox://styles/mapbox/dark-v9",
                tooltip={"text": "Value: {elevationValue}"}
            )

            st.pydeck_chart(r, use_container_width=True, height=540)

        # ─── TOP 5 INTENSITY LEADERBOARD ──────────────────────────────────────
        st.markdown("""
        <div class='glass-card' style='margin-bottom:0.5rem;'>
            <h4 style='margin:0; color:#38bdf8; font-size:0.8rem;'>🏆 TOP 5 INTENSITY HOTSPOTS</h4>
        </div>
        """, unsafe_allow_html=True)
        top5 = df_3d.nlargest(5, 'val_abs')[['lat', 'lon', 'val']].reset_index(drop=True)
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        cols5 = st.columns(5)
        for i, (_, row) in enumerate(top5.iterrows()):
            with cols5[i]:
                lat_label = f"{'N' if row['lat'] >= 0 else 'S'}{abs(row['lat']):.0f}°"
                lon_label = f"{'E' if row['lon'] >= 0 else 'W'}{abs(row['lon']):.0f}°"
                st.markdown(f"""
                <div style="text-align:center; padding:0.4rem 0.2rem; border:1px solid rgba(56,189,248,0.15); border-radius:8px;">
                    <div style="font-size:1.2rem;">{medals[i]}</div>
                    <div style="font-size:0.65rem; color:#94a3b8; margin:2px 0;">{lat_label}, {lon_label}</div>
                    <div style="font-size:0.9rem; font-weight:700; color:#38bdf8;">{row['val']:.2f}</div>
                    <div style="font-size:0.6rem; color:#475569;">{units}</div>
                </div>""", unsafe_allow_html=True)
