import streamlit as st
import pandas as pd
import numpy as np
from backend.climate_processor import ClimateProcessor
from backend.echarts_renderer import render_echarts

# ─── HOTSPOT PRESETS ──────────────────────────────────────────────────────────
HOTSPOTS = {
    "📍 Custom Location": None,
    "🧊 Arctic Circle": (78.0, 15.0),
    "🌿 Amazon Rainforest": (-3.0, -60.0),
    "🏜️ Sahara Desert": (23.0, 13.0),
    "🌊 Maldives (Sea Level)": (4.0, 73.0),
    "🌊 Bay of Bengal": (15.0, 88.0),
    "🏔️ Himalayan Glaciers": (30.0, 80.0),
    "🔥 Australian Outback": (-25.0, 134.0),
    "❄️ Antarctic Coast": (-70.0, 0.0),
    "🌍 Sub-Saharan Africa": (10.0, 20.0),
}

def render_time_series_view(ds, controls):
    """Renders an ECharts-powered time series with ML forecast, anomaly markers, risk badge, and hotspot presets."""
    var = controls["variable"]
    units = controls["units"]

    st.markdown("""<div class="section-tag">
        <span class="tag-line" style="background:linear-gradient(90deg,#38bdf8,#10b981)"></span>
        <h3 style="margin:0; font-size:1.25rem;">Chronological Trend Analysis + ML Forecast</h3>
    </div>
    <p style="color:#475569; font-size:0.92rem; margin-bottom:1.2rem;">
        Select a climate hotspot or enter coordinates to explore temporal trends, anomaly flags, and a 5-step ML forecast.
    </p>""", unsafe_allow_html=True)

    col_input, col_chart = st.columns([1, 3])

    with col_input:
        st.markdown("""<div class="glass-card" style="margin-bottom:1rem;">
            <p style="margin:0;color:#38bdf8;font-weight:600;font-size:0.85rem;
                      text-transform:uppercase;letter-spacing:0.08em;">🌍 Location Target</p>
        </div>""",
            unsafe_allow_html=True)

        # Hotspot Preset Selector
        selected_hotspot = st.selectbox("Climate Hotspot", list(HOTSPOTS.keys()), index=0)
        preset = HOTSPOTS[selected_hotspot]

        if preset is not None:
            lat_input = st.number_input("Latitude", value=preset[0], step=2.0, min_value=-90.0, max_value=90.0)
            lon_input = st.number_input("Longitude", value=preset[1], step=2.0, min_value=-180.0, max_value=180.0)
        else:
            lat_input = st.number_input("Latitude", value=0.0, step=2.0, min_value=-90.0, max_value=90.0)
            lon_input = st.number_input("Longitude", value=0.0, step=2.0, min_value=-180.0, max_value=180.0)

        # Climate Risk Index
        risk = ClimateProcessor.get_climate_risk_index(ds, var, lat_input, lon_input)
        if risk and risk.get("label") != "UNKNOWN":
            st.markdown(f"""
            <div style="margin-top:1rem; padding:0.8rem; border-radius:10px;
                        background:rgba(15,23,42,0.8); border: 1px solid {risk['color']}40;">
                <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">Climate Risk Index</div>
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                    <span class="risk-badge" style="background:{risk['color']}22; color:{risk['color']};
                        border:1px solid {risk['color']}; padding:2px 10px; border-radius:20px;
                        font-size:0.75rem; font-weight:700; letter-spacing:0.08em;">{risk['label']}</span>
                    <span style="font-size:1.4rem; font-weight:700; color:{risk['color']};">{risk['score']}</span>
                    <span style="font-size:0.7rem; color:#64748b;">/100</span>
                </div>
                <div style="font-size:0.68rem; color:#475569; line-height:1.6;">
                    Trend: <b style="color:#94a3b8">{risk['trend_component']:.0f}</b> &nbsp;·&nbsp;
                    Anomaly Freq: <b style="color:#94a3b8">{risk['anomaly_component']:.0f}</b> &nbsp;·&nbsp;
                    Variability: <b style="color:#94a3b8">{risk['variability_component']:.0f}</b>
                </div>
            </div>""", unsafe_allow_html=True)

        # Terminate anything else

    with col_chart:
        df_ts, actual_lat, actual_lon = ClimateProcessor.get_time_series(ds, var, lat_input, lon_input)
        trend_stats = ClimateProcessor.get_trend_stats(ds, var, lat_input, lon_input)
        forecast_vals, forecast_lower, forecast_upper = ClimateProcessor.get_ml_forecast(ds, var, lat_input, lon_input, future_steps=5)

        # Time label extraction
        time_vals = df_ts['time']
        try:
            x_data = time_vals.dt.strftime('%Y').tolist()
        except (AttributeError, TypeError):
            x_data = [str(t.year) for t in time_vals]

        y_raw = df_ts[var].round(3).tolist()
        y_ma  = pd.Series(y_raw).rolling(window=3, min_periods=1).mean().round(3).tolist()
        
        # Anomaly detection: time steps > 1.5σ from mean
        mean_v = float(np.mean(y_raw))
        std_v  = float(np.std(y_raw))
        anomaly_marks = [{"xAxis": x_data[i], "lineStyle": {"color": "#f97316", "width": 1.5, "type": "dashed"},
                          "label": {"formatter": "⚠", "color": "#f97316", "fontSize": 14}}
                         for i, v in enumerate(y_raw) if abs(v - mean_v) > 1.5 * std_v]

        # Build extended x-axis labels for forecast
        forecast_x = [f"F+{i+1}" for i in range(len(forecast_vals))]
        all_x = x_data + forecast_x

        # Series data: historical + None padding for forecast zone
        raw_extended  = y_raw + [None] * len(forecast_vals)
        ma_extended   = y_ma  + [None] * len(forecast_vals)
        fc_padded     = [None] * len(y_raw) + forecast_vals
        fc_lo_padded  = [None] * len(y_raw) + forecast_lower
        fc_hi_padded  = [None] * len(y_raw) + forecast_upper

        option = {
            "backgroundColor": "transparent",
            "animation": True,
            "animationDuration": 1200,
            "animationEasing": "cubicOut",
            "title": {
                "text": f"{'🧊 Arctic' if preset and preset[0] > 65 else '📍'} Lat {actual_lat:.1f}° / Lon {actual_lon:.1f}°",
                "subtext": f"{var.replace('_',' ').title()} ({units})  |  Gray zone = ML Forecast",
                "textStyle": {"color": "#f1f5f9", "fontSize": 14, "fontWeight": "bold"},
                "subtextStyle": {"color": "#475569", "fontSize": 11}
            },
            "tooltip": {"trigger": "axis",
                        "backgroundColor": "rgba(15,23,42,0.95)",
                        "borderColor": "rgba(56,189,248,0.3)", "borderWidth": 1,
                        "textStyle": {"color": "#e2e8f0", "fontSize": 13},
                        "axisPointer": {"type": "cross", "lineStyle": {"color": "rgba(56,189,248,0.4)"}}},
            "legend": {"data": ["Raw Value", "3-pt MA", "ML Forecast"],
                       "textStyle": {"color": "#64748b"}, "top": 0, "right": 0},
            "grid": {"left": "5%", "right": "3%", "bottom": "18%", "top": "22%", "containLabel": True},
            "dataZoom": [{"type": "inside", "start": 0, "end": 100},
                         {"start": 0, "end": 100, "height": 22,
                          "handleStyle": {"color": "#38bdf8"},
                          "fillerColor": "rgba(56,189,248,0.08)",
                          "borderColor": "rgba(56,189,248,0.2)",
                          "textStyle": {"color": "#64748b"}}],
            "xAxis": {"type": "category", "data": all_x,
                      "axisLabel": {"color": "#475569", "fontSize": 10, "rotate": 30},
                      "axisLine": {"lineStyle": {"color": "rgba(255,255,255,0.08)"}},
                      "splitLine": {"show": False}},
            "yAxis": {"type": "value", "name": units,
                      "nameTextStyle": {"color": "#475569"},
                      "axisLabel": {"color": "#475569"},
                      "axisLine": {"show": True, "lineStyle": {"color": "rgba(255,255,255,0.08)"}},
                      "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.04)", "type": "dashed"}}},
            "series": [
                # Forecast confidence band (upper - rendered transparent stacked)
                {"name": "FC Upper", "type": "line", "data": fc_hi_padded, "showSymbol": False,
                 "lineStyle": {"opacity": 0}, "stack": "fcband", "silent": True,
                 "areaStyle": {"color": "rgba(99,102,241,0)", "opacity": 0}},
                {"name": "FC Lower", "type": "line", "data": fc_lo_padded, "showSymbol": False,
                 "lineStyle": {"opacity": 0}, "stack": "fcband", "silent": True,
                 "areaStyle": {"color": "rgba(99,102,241,0.15)", "opacity": 1}},
                # Raw value
                {"name": "Raw Value", "type": "line", "data": raw_extended,
                 "smooth": True, "showSymbol": True, "symbolSize": 7,
                 "lineStyle": {"width": 2.5, "color": "#38bdf8"},
                 "itemStyle": {"color": "#38bdf8", "borderWidth": 2, "borderColor": "#0f172a"},
                 "areaStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                               "colorStops": [{"offset": 0, "color": "rgba(56,189,248,0.25)"},
                                              {"offset": 1, "color": "rgba(56,189,248,0.01)"}]}},
                 "emphasis": {"focus": "series"},
                 "markPoint": {"data": [{"type": "max", "itemStyle": {"color": "#ef4444"}},
                                        {"type": "min", "itemStyle": {"color": "#10b981"}}],
                               "label": {"color": "#fff", "fontSize": 11}},
                 "markLine": {"silent": True, "data": anomaly_marks, "symbol": "none"}
                 if anomaly_marks else {}},
                # 3-pt Moving Average
                {"name": "3-pt MA", "type": "line", "data": ma_extended,
                 "smooth": True, "showSymbol": False,
                 "lineStyle": {"width": 2, "type": "dashed", "color": "#f59e0b"},
                 "itemStyle": {"color": "#f59e0b"}, "emphasis": {"focus": "series"}},
                # ML Forecast line
                {"name": "ML Forecast", "type": "line", "data": fc_padded,
                 "smooth": True, "showSymbol": True, "symbolSize": 8,
                 "lineStyle": {"width": 2.5, "type": "dotted", "color": "#a855f7"},
                 "itemStyle": {"color": "#a855f7", "borderColor": "#0f172a", "borderWidth": 2},
                 "emphasis": {"focus": "series"}},
            ]
        }
        render_echarts(option, height=440)

    # ─── TREND STATS CARD ──────────────────────────────────────────────────────
    if trend_stats:
        slope = trend_stats['slope']
        r2 = trend_stats['r_squared']
        direction_word = "📈 Warming / Rising" if slope > 0 else "📉 Cooling / Declining"
        direction_color = "#ef4444" if slope > 0 else "#10b981"
        # Estimate future value at 5 more steps
        future_val = float(np.mean(y_raw) + slope * (len(y_raw) + 5))
        st.markdown(f"""
        <div class="glass-card" style="padding:1rem; margin-top:0.5rem; display:flex; flex-wrap:wrap; gap:1.5rem; align-items:center;">
            <div>
                <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px;">Trend Direction</div>
                <div style="font-size:1rem; font-weight:700; color:{direction_color};">{direction_word}</div>
            </div>
            <div>
                <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px;">Rate of Change</div>
                <div style="font-size:1.1rem; font-weight:700; color:#f1f5f9;">{slope:+.4f} <span style="font-size:0.75rem; color:#475569;">{units}/step</span></div>
            </div>
            <div>
                <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px;">R² Fit Quality</div>
                <div style="font-size:1.1rem; font-weight:700; color:#818cf8;">{r2:.3f}</div>
            </div>
            <div>
                <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px;">Anomaly Years Flagged</div>
                <div style="font-size:1.1rem; font-weight:700; color:#f97316;">{len(anomaly_marks)}</div>
            </div>
            <div>
                <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px;">ML Projected (5 steps)</div>
                <div style="font-size:1.1rem; font-weight:700; color:#a855f7;">{future_val:.2f} {units}</div>
            </div>
        </div>""", unsafe_allow_html=True)
