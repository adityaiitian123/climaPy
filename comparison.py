import streamlit as st
import pandas as pd
import numpy as np
from backend.climate_processor import ClimateProcessor
from backend.echarts_renderer import render_echarts

def render_comparison_view(ds, controls):
    """3-panel comparison: Period A | Period B | Difference Heatmap + zonal bar chart."""
    var = controls["variable"]
    units = controls["units"]

    st.markdown("""<div class="section-tag">
        <span class="tag-line"></span>
        <h3 style="margin:0; font-size:1.25rem;">Comparative Intelligence — Period vs Period</h3>
    </div>
    <p style="color:#475569; font-size:0.92rem; margin-bottom:1.2rem;">
        Side-by-side analysis of two time periods + a <b style="color:#f43f5e">difference heatmap</b> revealing exactly where climate changed.
    </p>""", unsafe_allow_html=True)

    times = ds.time
    try:
        time_labels = times.dt.strftime('%Y-%m-%d').values.tolist()
    except (AttributeError, TypeError):
        time_labels = [f"{t.year}-{t.month:02d}-{t.day:02d}" for t in times.values]

    import plotly.express as px

    # 1. Selection logic must happen first
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("""
        <div class='glass-card' style='margin-bottom:1rem;'>
            <h4 style='margin:0; color:#38bdf8;'>📅 Baseline Period</h4>
        </div>
        """, unsafe_allow_html=True)
        t_idx_1 = st.selectbox("Select Baseline", range(len(times)),
                              format_func=lambda x: time_labels[x], index=0, key="comp1_sel")
    
    with col_s2:
        st.markdown("""
        <div class='glass-card' style='margin-bottom:1rem;'>
            <h4 style='margin:0; color:#38bdf8;'>📅 Comparison Period</h4>
        </div>
        """, unsafe_allow_html=True)
        t_idx_2 = st.selectbox("Select Comparison", range(len(times)),
                              format_func=lambda x: time_labels[x],
                              index=len(times) - 1, key="comp2_sel")

    # 2. Extract data and calculate shared range for visual consistency
    all_vals = []
    df1 = ClimateProcessor.get_spatial_slice(ds, var, t_idx_1)
    df2 = ClimateProcessor.get_spatial_slice(ds, var, t_idx_2)
    
    if not df1.empty: all_vals.extend(df1[var].values)
    if not df2.empty: all_vals.extend(df2[var].values)
    
    if all_vals:
        z_min = float(np.min(all_vals))
        z_max = float(np.max(all_vals))
    else:
        z_min, z_max = 0, 100

    # 3. Render Metric and Map Columns
    col1, col2 = st.columns(2)
    with col1:
        mean_1 = round(float(df1[var].mean()), 3) if not df1.empty else 0
        st.markdown(f"<div style='color:#64748b;font-size:0.8rem'>Global Mean</div>"
                    f"<div style='font-size:1.6rem;font-weight:700;color:#38bdf8'>"
                    f"{mean_1:.2f} <span style='font-size:0.9rem;color:#475569'>{units}</span></div>",
                    unsafe_allow_html=True)
        
        fig1 = px.density_mapbox(df1, lat='lat', lon='lon', z=var, radius=10,
            mapbox_style="carto-darkmatter", center=dict(lat=0, lon=0), zoom=0.2,
            range_color=[z_min, z_max],
            color_continuous_scale="Turbo", title=f"📅 {time_labels[t_idx_1]}")
        fig1.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)',
                           font=dict(color='white'), coloraxis_showscale=False, height=300)
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        mean_2 = round(float(df2[var].mean()), 3) if not df2.empty else 0
        delta  = round(mean_2 - mean_1, 3)
        delta_color = "#ef4444" if delta > 0 else "#10b981"
        sign = "+" if delta > 0 else ""
        st.markdown(f"<div style='color:#64748b;font-size:0.8rem'>Global Mean</div>"
                    f"<div style='font-size:1.6rem;font-weight:700;color:{delta_color}'>"
                    f"{mean_2:.2f} <span style='font-size:0.9rem;color:#475569'>{units}</span>"
                    f" <span style='font-size:1rem;font-weight:600'>{sign}{delta:.2f}</span></div>",
                    unsafe_allow_html=True)
        
        fig2 = px.density_mapbox(df2, lat='lat', lon='lon', z=var, radius=10,
            mapbox_style="carto-darkmatter", center=dict(lat=0, lon=0), zoom=0.2,
            range_color=[z_min, z_max],
            color_continuous_scale="Turbo", title=f"📅 {time_labels[t_idx_2]}")
        fig2.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)',
                           font=dict(color='white'), coloraxis_showscale=False, height=300)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── GLOBAL Δ HEADLINE ────────────────────────────────────────────────────
    delta_icon = "🔥" if delta > 0 else "❄️"
    delta_word = "WARMING" if delta > 0 else "COOLING"
    st.markdown(f"""
    <div class="glass-card" style="text-align:center; padding:1.5rem;
         border: 1px solid {delta_color}40; box-shadow: 0 0 40px {delta_color}20;">
        <div style="font-size:0.7rem; color:#64748b; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:0.4rem;">
            Global Mean Δ Change
        </div>
        <div style="font-size:3.5rem; font-weight:900; color:{delta_color};
             font-family:'Space Grotesk',sans-serif; letter-spacing:-0.03em;
             text-shadow: 0 0 40px {delta_color}60;">
            {delta_icon} {sign}{delta:.3f} {units}
        </div>
        <div style="font-size:0.9rem; color:#94a3b8; margin-top:0.3rem; font-weight:600; letter-spacing:0.08em;">
            {delta_word} detected between {time_labels[t_idx_1]} → {time_labels[t_idx_2]}
        </div>
    </div>""", unsafe_allow_html=True)

    # ─── DIFFERENCE HEATMAP ───────────────────────────────────────────────────
    st.markdown("""<div class="section-tag" style="margin-top:1.5rem">
        <span class="tag-line" style="background:linear-gradient(90deg,#ef4444,#3b82f6)"></span>
        <h4 style="margin:0; font-size:1.1rem;">🗺️ Difference Heatmap  (B − A)</h4>
    </div>
    <p style="color:#475569;font-size:0.88rem;margin-bottom:0.8rem;">
        <b style="color:#ef4444">Red</b> = warmer / higher in Period B &nbsp;·&nbsp;
        <b style="color:#38bdf8">Blue</b> = cooler / lower in Period B &nbsp;·&nbsp;
        White = no change
    </p>""", unsafe_allow_html=True)

    if not df1.empty and not df2.empty:
        df_diff = df1.copy()
        df_merged = df1.merge(df2, on=['lat', 'lon'], suffixes=('_a', '_b'), how='inner')
        df_merged['diff'] = df_merged[f"{var}_b"] - df_merged[f"{var}_a"]
        abs_max = float(df_merged['diff'].abs().quantile(0.99)) or 1.0

        fig_diff = px.density_mapbox(
            df_merged, lat='lat', lon='lon', z='diff', radius=14,
            mapbox_style="carto-darkmatter", center=dict(lat=0, lon=0), zoom=0.2,
            color_continuous_scale="RdBu_r",
            range_color=[-abs_max, abs_max],
            title=f"Δ = {time_labels[t_idx_2]} minus {time_labels[t_idx_1]}"
        )
        fig_diff.update_layout(
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='#94a3b8', size=13),
            height=380
        )
        st.plotly_chart(fig_diff, use_container_width=True)

        # Regional winner/loser cards
        top_warm = df_merged.nlargest(3, 'diff')[['lat', 'lon', 'diff']].reset_index(drop=True)
        top_cool = df_merged.nsmallest(3, 'diff')[['lat', 'lon', 'diff']].reset_index(drop=True)

        st.markdown("<div style='display:flex; gap:1rem; flex-wrap:wrap; margin-top:0.5rem;'>", unsafe_allow_html=True)
        rw_col, rc_col = st.columns(2)
        with rw_col:
            st.markdown("<div style='font-size:0.65rem; color:#ef4444; text-transform:uppercase; letter-spacing:0.1em; font-weight:700; margin-bottom:0.5rem;'>🔥 Most Warming Regions</div>", unsafe_allow_html=True)
            for _, r in top_warm.iterrows():
                lat_s = f"{'N' if r['lat'] >= 0 else 'S'}{abs(r['lat']):.0f}°"
                lon_s = f"{'E' if r['lon'] >= 0 else 'W'}{abs(r['lon']):.0f}°"
                st.markdown(f"<div style='display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span style='color:#94a3b8; font-size:0.8rem;'>{lat_s}, {lon_s}</span><span style='color:#ef4444; font-weight:700; font-size:0.85rem;'>+{r['diff']:.2f}</span></div>", unsafe_allow_html=True)
        with rc_col:
            st.markdown("<div style='font-size:0.65rem; color:#38bdf8; text-transform:uppercase; letter-spacing:0.1em; font-weight:700; margin-bottom:0.5rem;'>❄️ Most Cooling Regions</div>", unsafe_allow_html=True)
            for _, r in top_cool.iterrows():
                lat_s = f"{'N' if r['lat'] >= 0 else 'S'}{abs(r['lat']):.0f}°"
                lon_s = f"{'E' if r['lon'] >= 0 else 'W'}{abs(r['lon']):.0f}°"
                st.markdown(f"<div style='display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05);'><span style='color:#94a3b8; font-size:0.8rem;'>{lat_s}, {lon_s}</span><span style='color:#38bdf8; font-weight:700; font-size:0.85rem;'>{r['diff']:.2f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── ZONAL BAND BAR CHART ─────────────────────────────────────────────────
    st.markdown("""<div class="section-tag" style="margin-top:1.5rem">
        <span class="tag-line"></span>
        <h4 style="margin:0; font-size:1.1rem;">Zonal Mean by 30° Latitude Band</h4>
    </div>""", unsafe_allow_html=True)

    bands = [(-90,-60),(-60,-30),(-30,0),(0,30),(30,60),(60,90)]
    band_labels = ["90°S–60°S","60°S–30°S","30°S–0°","0°–30°N","30°N–60°N","60°N–90°N"]

    def zonal_mean(df):
        out = []
        for lo, hi in bands:
            sub = df[(df['lat'] >= lo) & (df['lat'] < hi)]
            out.append(round(float(sub[var].mean()), 3) if not sub.empty else 0)
        return out

    z1 = zonal_mean(df1)
    z2 = zonal_mean(df2)
    dz = [round(z2[i] - z1[i], 3) for i in range(len(z1))]

    bar_option = {
        "backgroundColor": "transparent",
        "animation": True, "animationDuration": 900, "animationEasing": "elasticOut",
        "tooltip": {"trigger": "axis", "backgroundColor": "rgba(15,23,42,0.95)",
                    "borderColor": "rgba(56,189,248,0.3)", "borderWidth": 1,
                    "textStyle": {"color": "#e2e8f0", "fontSize": 13}},
        "legend": {"data": [time_labels[t_idx_1], time_labels[t_idx_2], "Δ Change"],
                   "textStyle": {"color": "#64748b"}, "top": 0},
        "grid": {"left": "5%", "right": "3%", "bottom": "5%", "top": "15%", "containLabel": True},
        "xAxis": {"type": "category", "data": band_labels,
                  "axisLabel": {"color": "#475569", "fontSize": 11},
                  "axisLine": {"lineStyle": {"color": "rgba(255,255,255,0.08)"}}},
        "yAxis": {"type": "value", "name": units,
                  "nameTextStyle": {"color": "#475569"}, "axisLabel": {"color": "#475569"},
                  "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.04)", "type": "dashed"}}},
        "series": [
            {"name": time_labels[t_idx_1], "type": "bar", "barMaxWidth": 30, "data": z1,
             "itemStyle": {"color": "#3b82f6", "borderRadius": [4,4,0,0]}},
            {"name": time_labels[t_idx_2], "type": "bar", "barMaxWidth": 30, "data": z2,
             "itemStyle": {"color": "#38bdf8", "borderRadius": [4,4,0,0]}},
            {"name": "Δ Change", "type": "line", "data": dz, "smooth": True,
             "lineStyle": {"width": 2.5, "color": "#f59e0b"},
             "itemStyle": {"color": "#f59e0b"}, "symbolSize": 9,
             "label": {"show": True, "color": "#f59e0b", "fontSize": 11, "formatter": "{c}"}}
        ]
    }
    render_echarts(bar_option, height=360)
