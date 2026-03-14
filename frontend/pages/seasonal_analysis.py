import streamlit as st
import plotly.express as px
from backend.climate_processor import ClimateProcessor

def render_seasonal_analysis(ds, controls):
    """Renders a 4-panel grid showing multi-year seasonal averages."""
    var = controls["variable"]
    units = controls["units"]

    st.markdown("""
    <div class="section-tag">
        <span class="tag-line" style="background:linear-gradient(90deg,#f59e0b,#ef4444)"></span>
        <h3 style="margin:0; font-size:1.25rem;">Seasonal Intelligence — Multi-Year Climatology</h3>
    </div>
    <p style="color:#475569; font-size:0.92rem; margin-bottom:1.5rem;">
        Comparative analysis of planetary states across meteorological seasons (MAM, JJA, SON, DJF).
    </p>
    """, unsafe_allow_html=True)

    with st.spinner("Processing Seasonal Flux..."):
        seasons = ClimateProcessor.get_seasonal_means(ds, var)

    if not seasons:
        st.warning("Seasonal grouping not available for this dataset coordinate system.")
        return

    # Create a 2x2 grid
    row1_c1, row1_c2 = st.columns(2)
    row2_c1, row2_c2 = st.columns(2)
    
    col_mapping = [
        (row1_c1, "Spring (MAM)"),
        (row1_c2, "Summer (JJA)"),
        (row2_c1, "Autumn (SON)"),
        (row2_c2, "Winter (DJF)")
    ]

    # Calculate spatial bounds and value ranges
    all_lats = []
    all_lons = []
    all_vals = []
    for s_df in seasons.values():
        all_lats.extend(s_df['lat'].tolist())
        all_lons.extend(s_df['lon'].tolist())
        all_vals.extend(s_df['val'].tolist())
    
    avg_lat = sum(all_lats) / len(all_lats)
    avg_lon = sum(all_lons) / len(all_lons)
    lat_range = max(all_lats) - min(all_lats)
    lon_range = max(all_lons) - min(all_lons)
    v_min, v_max = min(all_vals), max(all_vals)
    
    # Heuristic for zoom levels
    max_dist = max(lat_range, lon_range)
    is_regional = max_dist < 50

    for col, s_name in col_mapping:
        with col:
            df = seasons.get(s_name)
            if df is not None:
                st.markdown(f"""
                <div style="font-size:0.8rem; font-weight:700; color:#38bdf8; text-transform:uppercase; 
                            letter-spacing:0.1em; text-align:center; margin-bottom:0.5rem;
                            background:rgba(56,189,248,0.05); padding:0.4rem; border-radius:6px;">
                    {s_name}
                </div>
                """, unsafe_allow_html=True)
                
                # Sample for performance but keep density
                df_plot = df.sample(min(len(df), 1500))

                fig = px.scatter_geo(
                    df_plot, lat='lat', lon='lon', color='val',
                    color_continuous_scale="Turbo", # High visibility
                    range_color=[v_min, v_max],
                    labels={'val': units},
                    opacity=0.9
                )
                
                fig.update_traces(marker=dict(size=6, symbol="circle"))

                fig.update_geos(
                    showcoastlines=True, coastlinecolor="#475569",
                    showland=True, landcolor="#1e293b",
                    showocean=True, oceancolor="#0f172a",
                    bgcolor="rgba(0,0,0,0)",
                )
                
                if is_regional:
                    fig.update_geos(
                        center=dict(lat=avg_lat, lon=avg_lon),
                        projection_scale=10 if max_dist < 5 else (5 if max_dist < 20 else 2),
                        lataxis_range=[min(all_lats)-1, max(all_lats)+1],
                        lonaxis_range=[min(all_lons)-1, max(all_lons)+1]
                    )

                fig.update_layout(
                    height=350, margin=dict(l=0, r=0, t=0, b=0),
                    coloraxis_showscale=False,
                    paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"Data for {s_name} missing.")

    st.info("💡 All maps use a high-visibility scale ( {v_min:.1f} to {v_max:.1f} {units} ) focused on your data region.".format(
        v_min=v_min, v_max=v_max, units=units
    ))
