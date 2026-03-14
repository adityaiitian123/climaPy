import streamlit as st
import pandas as pd
import numpy as np
from backend.climate_processor import ClimateProcessor
from backend.echarts_renderer import render_echarts
import scipy.stats as scipy_stats

def render_map_view(ds, controls):
    """Spatial Command Center: heatmap with time-lapse animation + anomaly glow overlay."""
    var = controls["variable"]
    t_idx = controls["time_index"]
    units = controls["units"]

    col_t1, col_t2, col_t3 = st.columns([3, 1, 1])
    with col_t1:
        st.markdown(f"""
        <div class="section-tag">
            <span class="tag-line" style="background:linear-gradient(90deg,#38bdf8,#818cf8)"></span>
            <h3 style="margin:0; font-size:1.25rem;">Command Intelligence: {var.replace('_',' ').title()}</h3>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        view_mode = st.radio("View Mode", ["3D Intelligence", "2D Heatmap"], horizontal=True, label_visibility="collapsed")
    with col_t3:
        show_anomaly = st.toggle("⚡ Anomaly Glow", value=True)

    # ─── TIME-LAPSE CONTROLS ───────────────────────────────────────────────────
    anim_col1, anim_col2, anim_col3 = st.columns([2, 1, 1])
    with anim_col1:
        if 'is_playing' not in st.session_state:
            st.session_state.is_playing = False
        if 'anim_t_idx' not in st.session_state:
            st.session_state.anim_t_idx = t_idx

        play_btn = st.button(
            "⏹ Stop Animation" if st.session_state.is_playing else "▶ Animate Time-Lapse",
            use_container_width=True
        )
        if play_btn:
            st.session_state.is_playing = not st.session_state.is_playing

    with anim_col2:
        speed = st.select_slider("Speed", options=["Slow", "Normal", "Fast"],
                                  value="Normal", label_visibility="visible")
    with anim_col3:
        if st.button("⏮ Reset", use_container_width=True):
            st.session_state.anim_t_idx = 0
            st.session_state.is_playing = False
            st.rerun()

    # Auto-advance when playing
    if st.session_state.is_playing:
        max_t = len(ds.time) - 1
        st.session_state.anim_t_idx = (st.session_state.anim_t_idx + 1) % (max_t + 1)
        t_idx = st.session_state.anim_t_idx
        import time
        delay = {"Slow": 0.8, "Normal": 0.4, "Fast": 0.1}.get(speed, 0.4)
        time.sleep(delay)
        st.rerun()
    else:
        t_idx = controls["time_index"]

    # ─── TIME LABEL ───────────────────────────────────────────────────────────
    try:
        time_label = str(ds.time.isel(time=t_idx).dt.strftime("%Y-%m-%d").values.item())
    except:
        try:
            tv = ds.time.isel(time=t_idx).values
            time_label = f"{tv.year}-{tv.month:02d}"
        except:
            time_label = f"Step {t_idx}"

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:1rem; margin-bottom:0.5rem;">
        <div style="font-size:0.7rem; color:#38bdf8; text-transform:uppercase; letter-spacing:0.1em; font-weight:600;">
            Time Frame
        </div>
        <div style="font-size:1.2rem; font-weight:700; color:#f1f5f9; font-family:'Space Grotesk',sans-serif;">
            {time_label}
        </div>
        <div style="font-size:0.7rem; color:#475569;">(Step {t_idx + 1} / {len(ds.time)})</div>
        {'<span style="display:inline-block; width:8px; height:8px; background:#10b981; border-radius:50%; box-shadow:0 0 8px #10b981; animation:pulse-dot 1s infinite; margin-left:8px;"></span><span style="font-size:0.7rem; color:#10b981; font-weight:600; margin-left:4px;">LIVE PLAYBACK</span>' if st.session_state.is_playing else ''}
    </div>""", unsafe_allow_html=True)

    # ─── PLANETARY PULSE DASHBOARD — DYNAMIC E-CHARTS ──────────────────────────
    # Injecting CSS to style the columns as cards safely
    st.markdown("""
        <style>
        [data-testid="column"]:has(div.pulse-marker) {
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(56, 189, 248, 0.15);
            border-radius: 12px;
            padding: 0.75rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        [data-testid="column"]:has(div.pulse-marker):hover {
            border-color: rgba(56, 189, 248, 0.4);
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.1);
            transform: translateY(-2px);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
    pulse_c1, pulse_c2, pulse_c3, pulse_c4, pulse_c5 = st.columns(5)

    # 1. Shaded Line Trend (Temporal Mean)
    with pulse_c1:
        st.markdown("<div class='pulse-marker'></div>", unsafe_allow_html=True)
        ts_full, _, _ = ClimateProcessor.get_time_series(ds, var, 0, 0) # Global mean proxy
        line_opt = {
            "title": {"text": "PLANETARY TREND", "left": "center", "top": 5, "textStyle": {"color": "#38bdf8", "fontSize": 10, "fontWeight": "bold", "letterSpacing": 1}},
            "grid": {"left": "5%", "right": "5%", "top": "35%", "bottom": "5%"},
            "xAxis": {"type": "category", "show": False},
            "yAxis": {"type": "value", "scale": True, "show": False},
            "series": [{
                "data": ts_full[var].round(2).tolist() if not ts_full.empty else [],
                "type": "line", "smooth": True, "symbol": "none",
                "lineStyle": {"width": 2, "color": "#38bdf8"},
                "areaStyle": {"color": "rgba(56,189,248,0.15)"}
            }]
        }
        render_echarts(line_opt, height=130)

    # 2. Shaded Area Graph (Zonal Mean)
    with pulse_c2:
        st.markdown("<div class='pulse-marker'></div>", unsafe_allow_html=True)
        df_z = ClimateProcessor.get_zonal_mean(ds, var, t_idx)
        area_opt = {
            "title": {"text": "ZONAL PROFILE", "left": "center", "top": 5, "textStyle": {"color": "#818cf8", "fontSize": 10, "fontWeight": "bold", "letterSpacing": 1}},
            "grid": {"left": "5%", "right": "5%", "top": "35%", "bottom": "5%"},
            "xAxis": {"type": "category", "show": False},
            "yAxis": {"type": "value", "scale": True, "show": False},
            "series": [{
                "data": df_z[var].round(2).tolist() if not df_z.empty else [],
                "type": "line", "smooth": True, "symbol": "none",
                "lineStyle": {"width": 2, "color": "#818cf8"},
                "areaStyle": {"color": "rgba(129,140,248,0.2)"}
            }]
        }
        render_echarts(area_opt, height=130)

    # 3. Horizontal Bar (Meridional Top Aggregates)
    with pulse_c3:
        st.markdown("<div class='pulse-marker'></div>", unsafe_allow_html=True)
        df_m = ClimateProcessor.get_meridional_mean(ds, var, t_idx)
        hbar_opt = {
            "title": {"text": "MERIDIONAL STACK", "left": "center", "top": 5, "textStyle": {"color": "#10b981", "fontSize": 10, "fontWeight": "bold", "letterSpacing": 1}},
            "grid": {"left": "10%", "right": "10%", "top": "35%", "bottom": "10%"},
            "xAxis": {"show": False},
            "yAxis": {"type": "category", "show": False},
            "series": [{
                "data": df_m[var].iloc[::5].round(2).tolist() if not df_m.empty else [],
                "type": "bar", "itemStyle": {"color": "#10b981", "borderRadius": [0, 4, 4, 0]}
            }]
        }
        render_echarts(hbar_opt, height=130)

    # 4. Vertical Bar (Anomaly Distribution)
    with pulse_c4:
        st.markdown("<div class='pulse-marker'></div>", unsafe_allow_html=True)
        counts, _ = ClimateProcessor.get_histogram_data(ds, var, t_idx, bins=12)
        vbar_opt = {
            "title": {"text": "DISTRIBUTION", "left": "center", "top": 5, "textStyle": {"color": "#f59e0b", "fontSize": 10, "fontWeight": "bold", "letterSpacing": 1}},
            "grid": {"left": "5%", "right": "5%", "top": "35%", "bottom": "5%"},
            "xAxis": {"type": "category", "show": False},
            "yAxis": {"show": False},
            "series": [{
                "data": counts if len(counts) > 0 else [],
                "type": "bar", "itemStyle": {"color": "#f59e0b", "borderRadius": [2, 2, 0, 0]}
            }]
        }
        render_echarts(vbar_opt, height=130)

    # 5. Mini Heatmap (Monthly Anomaly Evolution)
    with pulse_c5:
        st.markdown("<div class='pulse-marker'></div>", unsafe_allow_html=True)
        df_mat = ClimateProcessor.get_temporal_matrix(ds, var)
        heat_mini_data = []
        if not df_mat.empty:
            # Take a small 10x10 snippet for the mini heatmap
            subset = df_mat.iloc[:60:6] # Sample time
            for i, val in enumerate(subset[var].values[:10]):
                for j in range(5):
                    heat_mini_data.append([j, i, float(val)])
        
        heat_opt = {
            "title": {"text": "SPATIO-TEMPORAL", "left": "center", "top": 5, "textStyle": {"color": "#ef4444", "fontSize": 10, "fontWeight": "bold", "letterSpacing": 1}},
            "grid": {"left": "5%", "right": "5%", "top": "35%", "bottom": "5%"},
            "xAxis": {"show": False}, "yAxis": {"show": False},
            "visualMap": {"show": False, "min": -1, "max": 1, "inRange": {"color": ["#3b82f6", "#f8fafc", "#ef4444"]}},
            "series": [{"type": "heatmap", "data": heat_mini_data}]
        }
        render_echarts(heat_opt, height=130)

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # ─── PRIMARY MAP LAYER ────────────────────────────────────────────────────
    with st.container():
        stats = ClimateProcessor.get_statistical_summary(ds, var, t_idx)
        # Anomaly count
        anom_df = ClimateProcessor.get_anomaly_slice(ds, var, t_idx)
        anom_count = 0
        if not anom_df.empty:
            threshold = float(anom_df['anomaly'].std()) * 2
            anom_count = int((anom_df['anomaly'].abs() > threshold).sum())

        if stats:
            st.markdown(f"""
            <div class="intel-hud">
                <div class="hud-item">
                    <span class="hud-label">Time Frame</span>
                    <span class="hud-value">{time_label}</span>
                </div>
                <div class="hud-item">
                    <span class="hud-label">Global Mean</span>
                    <span class="hud-value">{stats['mean']:.2f} {units}</span>
                </div>
                <div class="hud-item">
                    <span class="hud-label">Max Intensity</span>
                    <span class="hud-value">{stats['max']:.2f}</span>
                </div>
                <div class="hud-item">
                    <span class="hud-label">Min Intensity</span>
                    <span class="hud-value">{stats['min']:.2f}</span>
                </div>
                <div class="hud-item" style="border-top:1px solid rgba(56,189,248,0.15); padding-top:4px; margin-top:4px;">
                    <span class="hud-label">⚡ Anomaly Cells</span>
                    <span class="hud-value" style="color:#f97316;">{anom_count}</span>
                </div>
            </div>
            <div class="scanline-effect" style="height: 550px; pointer-events: none;"></div>
            """, unsafe_allow_html=True)

        render_primary_map_internal(ds, controls, view_mode, t_idx, show_anomaly)

    # ─── EXPORT BUTTON ─────────────────────────
    df_export = ClimateProcessor.get_spatial_slice(ds, var, t_idx)
    if not df_export.empty:
        csv_data = df_export.to_csv(index=False)
        st.download_button(
            "⬇ Export Current Slice as CSV",
            data=csv_data,
            file_name=f"{var}_{time_label}_slice.csv",
            mime="text/csv",
            use_container_width=False
        )

    # ─── ANALYTICS GRID — 6 distinct chart varieties ─────────────────────────
    row1_c1, row1_c2, row1_c3 = st.columns(3)

    # 1. SHADED AREA LINE — Zonal Mean (Latitude vs Value)
    with row1_c1:
        st.markdown("""
        <div class='glass-card' style='margin-bottom:0.5rem;'>
            <h4 style='margin:0; font-size:1.1rem;'>① Zonal Mean</h4>
        </div>
        """, unsafe_allow_html=True)
        df_zonal = ClimateProcessor.get_zonal_mean(ds, var, t_idx)
        # ... (rest of logic)
        zonal_opt = {
            "title": {"text": "① Zonal Mean", "subtext": "Shaded Area Line",
                      "textStyle": {"color": "#94a3b8", "fontSize": 12},
                      "subtextStyle": {"color": "#334155", "fontSize": 9}},
            "tooltip": {"trigger": "axis"},
            "grid": {"left": "15%", "right": "8%", "top": "22%", "bottom": "10%"},
            "xAxis": {"type": "value", "name": units, "nameTextStyle": {"color": "#475569"},
                      "axisLabel": {"color": "#64748b", "fontSize": 9}},
            "yAxis": {"type": "category",
                      "data": df_zonal['lat'].round(1).tolist() if not df_zonal.empty else [],
                      "axisLabel": {"color": "#64748b", "fontSize": 8}},
            "series": [{
                "data": df_zonal[var].round(2).tolist() if not df_zonal.empty else [],
                "type": "line", "smooth": True, "color": "#818cf8",
                "lineStyle": {"width": 2},
                "areaStyle": {
                    "color": {"type": "linear", "x": 1, "y": 0, "x2": 0, "y2": 0,
                              "colorStops": [{"offset": 0, "color": "rgba(129,140,248,0.55)"},
                                             {"offset": 1, "color": "rgba(129,140,248,0.02)"}]}
                },
                "symbol": "none"
            }]
        }
        render_echarts(zonal_opt, height=230)
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. HORIZONTAL BAR — Meridional Mean (Longitude bands)
    with row1_c2:
        st.markdown("""
        <div class='glass-card' style='margin-bottom:0.5rem;'>
            <h4 style='margin:0; font-size:1.1rem;'>② Meridional Mean</h4>
        </div>
        """, unsafe_allow_html=True)
        df_merid = ClimateProcessor.get_meridional_mean(ds, var, t_idx)
        # Bin lons into 12 × 30° bands for legibility
        if not df_merid.empty:
            import pandas as _pd
            df_merid['band'] = (_pd.cut(df_merid['lon'],
                                        bins=[-180,-150,-120,-90,-60,-30,0,30,60,90,120,150,180],
                                        labels=["180W","150W","120W","90W","60W","30W",
                                                "0","30E","60E","90E","120E","150E"])
                               )
            band_vals = df_merid.groupby('band', observed=True)[var].mean().round(2)
            hbar_cats = band_vals.index.tolist()
            hbar_vals = band_vals.values.tolist()
        else:
            hbar_cats, hbar_vals = [], []

        merid_opt = {
            "title": {"text": "② Meridional Mean", "subtext": "Horizontal Bar",
                      "textStyle": {"color": "#94a3b8", "fontSize": 12},
                      "subtextStyle": {"color": "#334155", "fontSize": 9}},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"left": "18%", "right": "8%", "top": "22%", "bottom": "10%"},
            "xAxis": {"type": "value", "axisLabel": {"color": "#64748b", "fontSize": 9},
                      "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.04)"}}},
            "yAxis": {"type": "category", "data": hbar_cats,
                      "axisLabel": {"color": "#64748b", "fontSize": 8}},
            "series": [{
                "data": hbar_vals, "type": "bar",
                "itemStyle": {
                    "color": {"type": "linear", "x": 0, "y": 0, "x2": 1, "y2": 0,
                              "colorStops": [{"offset": 0, "color": "#0ea5e9"},
                                             {"offset": 1, "color": "#38bdf8"}]},
                    "borderRadius": [0, 4, 4, 0]
                },
                "label": {"show": False}
            }]
        }
        render_echarts(merid_opt, height=230)
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. VERTICAL BAR (gradient) — Data Distribution Histogram
    with row1_c3:
        st.markdown("""
        <div class='glass-card' style='margin-bottom:0.5rem;'>
            <h4 style='margin:0; font-size:1.1rem;'>③ Distribution</h4>
        </div>
        """, unsafe_allow_html=True)
        counts, edges = ClimateProcessor.get_histogram_data(ds, var, t_idx, bins=20)
        hist_opt = {
            "title": {"text": "③ Distribution", "subtext": "Vertical Bar",
                      "textStyle": {"color": "#94a3b8", "fontSize": 12},
                      "subtextStyle": {"color": "#334155", "fontSize": 9}},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"left": "12%", "right": "8%", "top": "22%", "bottom": "18%"},
            "xAxis": {"type": "category", "data": [round(e, 1) for e in edges[:-1]],
                      "axisLabel": {"color": "#64748b", "fontSize": 8, "rotate": 30}},
            "yAxis": {"type": "value", "axisLabel": {"color": "#64748b", "fontSize": 9},
                      "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.04)"}}},
            "series": [{
                "data": [{"value": c, "itemStyle": {
                    "color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                              "colorStops": [{"offset": 0, "color": "#f59e0b"},
                                             {"offset": 1, "color": "rgba(245,158,11,0.1)"}]}
                }} for c in counts],
                "type": "bar",
                "itemStyle": {"borderRadius": [3, 3, 0, 0]}
            }]
        }
        render_echarts(hist_opt, height=230)
        st.markdown("</div>", unsafe_allow_html=True)

    row2_c1, row2_c2, row2_c3 = st.columns(3)

    # 4. HEATMAP — Latitude-Band × Metric breakdown
    with row2_c1:
        st.markdown("""
        <div class='glass-card' style='margin-bottom:0.5rem;'>
            <h4 style='margin:0; font-size:1.1rem;'>④ Band×Metric</h4>
        </div>
        """, unsafe_allow_html=True)
        bands_lat  = [(-90,-60),(-60,-30),(-30,0),(0,30),(30,60),(60,90)]
        band_lbls  = ["90S-60S","60S-30S","30S-0","0-30N","30N-60N","60N-90N"]
        stats_box  = ClimateProcessor.get_statistical_summary(ds, var, t_idx)
        # Build a 6×8 heatmap: latitude bands × metric (extended stats)
        metric_lbls = ["Min", "Q1", "Mean", "Max", "Std", "Skew", "Kurt", "CV"]
        heat_data   = []
        if stats_box and not ClimateProcessor.get_zonal_mean(ds, var, t_idx).empty:
            df_z = ClimateProcessor.get_zonal_mean(ds, var, t_idx)
            for bi, (lo, hi) in enumerate(bands_lat):
                sub = df_z[(df_z['lat'] >= lo) & (df_z['lat'] < hi)][var]
                if not sub.empty:
                    # Calculate extended stats for each band
                    vals = [
                        float(sub.min()), float(sub.quantile(0.25)),
                        float(sub.mean()), float(sub.max()),
                        float(sub.std()), float(scipy_stats.skew(sub)) if len(sub) > 2 else 0,
                        float(scipy_stats.kurtosis(sub)) if len(sub) > 2 else 0,
                        float(sub.std()/sub.mean()) if sub.mean() !=0 else 0
                    ]
                else:
                    vals = [0] * 8
                for mi, v in enumerate(vals):
                    heat_data.append([mi, bi, round(v, 2)])
        heatmap_opt = {
            "title": {"text": "④ Band×Metric", "subtext": "Heatmap",
                      "textStyle": {"color": "#94a3b8", "fontSize": 12},
                      "subtextStyle": {"color": "#334155", "fontSize": 9}},
            "tooltip": {"position": "top", "formatter": "{c}"},
            "grid": {"left": "22%", "right": "12%", "top": "22%", "bottom": "12%"},
            "xAxis": {"type": "category", "data": metric_lbls,
                      "axisLabel": {"color": "#64748b", "fontSize": 9}, "splitArea": {"show": True}},
            "yAxis": {"type": "category", "data": band_lbls,
                      "axisLabel": {"color": "#64748b", "fontSize": 8}, "splitArea": {"show": True}},
            "visualMap": {"min": min([d[2] for d in heat_data]) if heat_data else 0,
                          "max": max([d[2] for d in heat_data]) if heat_data else 1,
                          "show": False,
                          "inRange": {"color": ["#0f172a","#1e3a5f","#0ea5e9","#38bdf8","#7dd3fc",
                                                "#bae6fd","#fef3c7","#fde68a","#f59e0b","#ef4444"]}},
            "series": [{"type": "heatmap", "data": heat_data,
                        "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.5)"}}}]
        }
        render_echarts(heatmap_opt, height=230)
        st.markdown("</div>", unsafe_allow_html=True)

    row2_c2_col, row2_c3_col = st.columns([2, 1])

    # 5. SHADED TREND LINE — Temporal-Latitudinal Matrix
    with row2_c2_col:
        st.markdown("""
        <div class='glass-card' style='margin-bottom:0.5rem;'>
            <h4 style='margin:0; font-size:1.1rem;'>⑤ Lat Trend Lines</h4>
        </div>
        """, unsafe_allow_html=True)
        df_matrix = ClimateProcessor.get_temporal_matrix(ds, var)
        if not df_matrix.empty:
            # Show as multi-line (per-latitude-band) shaded area trend
            # Pick 4 representative latitudes
            lats_avail = sorted(ds.lat.values.tolist())
            picks = [lats_avail[0], lats_avail[len(lats_avail)//4],
                     lats_avail[len(lats_avail)//2], lats_avail[-1]]
            colors = ["#38bdf8", "#a855f7", "#f59e0b", "#ef4444"]
            trend_series = []
            t_indices = list(range(len(ds.time)))
            for lat_pick, color in zip(picks, colors):
                nearest_lat = min(ds.lat.values, key=lambda x: abs(x - lat_pick))
                subset = df_matrix[df_matrix['lat'].round(2) == round(float(nearest_lat), 2)][var]
                vals = subset.values.tolist()
                if vals:
                    trend_series.append({
                        "name": f"Lat {nearest_lat:.0f}°",
                        "type": "line", "data": vals,
                        "smooth": True, "symbol": "none",
                        "lineStyle": {"width": 1.5, "color": color},
                        "areaStyle": {"color": color.replace("#", "rgba(") + ",0.08)" if False else color,
                                      "opacity": 0.08},
                        "itemStyle": {"color": color}
                    })
            matrix_opt = {
                "title": {"text": "⑤ Lat Trend Lines", "subtext": "Shaded Multi-Line",
                          "textStyle": {"color": "#94a3b8", "fontSize": 12},
                          "subtextStyle": {"color": "#334155", "fontSize": 9}},
                "tooltip": {"trigger": "axis"},
                "legend": {"bottom": 0, "textStyle": {"color": "#64748b", "fontSize": 8}},
                "grid": {"left": "8%", "right": "5%", "top": "22%", "bottom": "25%"},
                "xAxis": {"type": "category", "data": t_indices, "axisLabel": {"show": False}},
                "yAxis": {"type": "value", "axisLabel": {"color": "#64748b", "fontSize": 9},
                          "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.04)"}}},
                "series": trend_series
            }
            render_echarts(matrix_opt, height=230)
        else:
            st.info("Insufficient data for trend lines.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 6. SHADED AREA LINE — Equatorial cross-section (Lon vs Value)
    with row2_c3_col:
        st.markdown("""
        <div class='glass-card' style='margin-bottom:0.5rem;'>
            <h4 style='margin:0; font-size:1.1rem;'>⑥ Equatorial</h4>
        </div>
        """, unsafe_allow_html=True)
        try:
            eq_vals = ds[var].isel(time=t_idx).sel(lat=0, method='nearest').values.tolist()
            lon_lbls = ds.lon.values.round(0).astype(int).tolist()
            eq_opt = {
                "title": {"text": "⑥ Equatorial", "subtext": "Shaded Area",
                          "textStyle": {"color": "#94a3b8", "fontSize": 12},
                          "subtextStyle": {"color": "#334155", "fontSize": 9}},
                "tooltip": {"trigger": "axis"},
                "grid": {"left": "12%", "right": "5%", "top": "22%", "bottom": "12%"},
                "xAxis": {"type": "category", "data": lon_lbls,
                          "axisLabel": {"color": "#64748b", "fontSize": 7, "rotate": 45}},
                "yAxis": {"type": "value", "axisLabel": {"color": "#64748b", "fontSize": 9},
                          "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.04)"}}},
                "series": [{
                    "data": eq_vals, "type": "line", "smooth": True,
                    "symbol": "none",
                    "lineStyle": {"width": 2, "color": "#a855f7"},
                    "areaStyle": {
                        "color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                  "colorStops": [{"offset": 0, "color": "rgba(168,85,247,0.5)"},
                                                 {"offset": 1, "color": "rgba(168,85,247,0.02)"}]}
                    },
                    "markLine": {
                        "silent": True,
                        "data": [{"type": "average", "label": {"formatter": "avg",
                                  "color": "#f59e0b", "fontSize": 9},
                                  "lineStyle": {"color": "#f59e0b", "type": "dashed", "width": 1}}]
                    }
                }]
            }
            render_echarts(eq_opt, height=230)
        except:
            st.info("Equatorial view unavailable.")


def render_primary_map_internal(ds, controls, view_mode, t_idx, show_anomaly):
    """Sub-handler for the main geospatial heatmap with optional anomaly glow overlay."""
    var = controls["variable"]
    units = controls["units"]

    df_slice = ClimateProcessor.get_spatial_slice(ds, var, t_idx)
    if df_slice.empty:
        st.warning("No geospatial data for this selection.")
        return

    df_clean = df_slice.dropna(subset=[var])
    data = df_clean[['lon', 'lat', var]].values.tolist()

    vibrant_colors = ['#00f2fe', '#4facfe', '#7161ef', '#9b5de5', '#f15bb5', '#fee440', '#00bbf9', '#00f5d4', '#f59e0b', '#ef4444']

    # Build anomaly overlay series
    anomaly_series = []
    if show_anomaly:
        anom_df = ClimateProcessor.get_top_anomaly_regions(ds, var, t_idx, n=20)
        if not anom_df.empty:
            pos_pts = anom_df[anom_df['anomaly'] > 0][['lon', 'lat', 'anomaly']].values.tolist()
            neg_pts = anom_df[anom_df['anomaly'] < 0][['lon', 'lat', 'anomaly']].values.tolist()
            if pos_pts:
                anomaly_series.append({
                    "name": "Hot Anomaly", "type": "effectScatter",
                    "coordinateSystem": "geo" if view_mode != "3D Intelligence" else "geo",
                    "data": pos_pts, "symbolSize": 14,
                    "rippleEffect": {"brushType": "stroke", "period": 3, "scale": 3},
                    "itemStyle": {"color": "#ef4444", "shadowBlur": 10, "shadowColor": "#ef4444"}
                })
            if neg_pts:
                anomaly_series.append({
                    "name": "Cold Anomaly", "type": "effectScatter",
                    "coordinateSystem": "geo" if view_mode != "3D Intelligence" else "geo",
                    "data": neg_pts, "symbolSize": 14,
                    "rippleEffect": {"brushType": "stroke", "period": 3, "scale": 3},
                    "itemStyle": {"color": "#38bdf8", "shadowBlur": 10, "shadowColor": "#38bdf8"}
                })

    if view_mode == "3D Intelligence":
        map_opt = {
            "backgroundColor": "transparent",
            "tooltip": {"trigger": "item"},
            "visualMap": {"min": float(df_clean[var].min()), "max": float(df_clean[var].max()),
                          "calculable": True, "inRange": {"color": vibrant_colors},
                          "textStyle": {"color": "#94a3b8"}, "bottom": "5%", "left": "center", "orient": "horizontal"},
            "geo3D": {"map": "world", "roam": True,
                      "itemStyle": {"areaColor": "rgba(30,41,59,0.6)", "borderColor": "rgba(56,189,248,0.8)", "borderWidth": 1},
                      "viewControl": {"autoRotate": False, "distance": 80},
                      "light": {"main": {"intensity": 1.5, "shadow": True}, "ambient": {"intensity": 0.4}}},
            "series": [{"type": "bar3D", "coordinateSystem": "geo3D", "data": data,
                        "shading": "lambert", "barSize": 0.6, "itemStyle": {"opacity": 0.9}}]
        }
        render_echarts(map_opt, height=550, use_map=True, use_gl=True)
    else:
        map_opt = {
            "backgroundColor": "transparent",
            "tooltip": {"trigger": "item"},
            "visualMap": {"min": float(df_clean[var].min()), "max": float(df_clean[var].max()),
                          "calculable": True, "inRange": {"color": vibrant_colors},
                          "textStyle": {"color": "#94a3b8"}, "bottom": "5%", "left": "center", "orient": "horizontal"},
            "geo": {"map": "world", "roam": True, "zoom": 1.2,
                    "itemStyle": {"areaColor": "rgba(30,41,59,0.5)", "borderColor": "rgba(56,189,248,0.8)", "borderWidth": 1.5}},
            "series": [
                {"name": var.title(), "type": "scatter", "coordinateSystem": "geo", "data": data,
                 "symbolSize": 10, "itemStyle": {"opacity": 1, "shadowBlur": 10, "shadowColor": "rgba(255,255,255,0.5)"}},
                *anomaly_series
            ]
        }
        render_echarts(map_opt, height=550, use_map=True)
