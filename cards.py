import streamlit as st
import pandas as pd
from backend.climate_processor import ClimateProcessor
from backend.echarts_renderer import render_echarts

def render_kpi_cards(ds, controls):
    """Renders top-row neon KPI metric cards + ECharts sparkline + anomaly gauge."""
    var = controls["variable"]
    t_idx = controls["time_index"]
    units = controls["units"]

    current_mean = ClimateProcessor.calculate_global_mean(ds, var, t_idx)
    historical_mean = float(ds[var].mean().values)
    all_means = [round(float(ds[var].isel(time=i).mean().values), 3) for i in range(len(ds.time))]

    anom_diff = current_mean - historical_mean
    anom_pct  = (anom_diff / abs(historical_mean)) * 100 if historical_mean != 0 else 0

    df_slice  = ClimateProcessor.get_spatial_slice(ds, var, t_idx)
    slice_max = df_slice[var].max() if not df_slice.empty else 0
    slice_min = df_slice[var].min() if not df_slice.empty else 0

    # ── 4 Static KPI Cards ──────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""<div class="kpi-card cyan">
            <div class="kpi-label">Global Mean</div>
            <div class="kpi-number">{current_mean:.2f} <span class="kpi-unit">{units}</span></div>
            <div class="kpi-delta neu">▸ Spatial area average</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        sign = "+" if anom_diff > 0 else ""
        clr  = "#ef4444" if anom_diff > 0 else "#38bdf8"
        icon = "▲" if anom_diff > 0 else "▼"
        css  = "neg" if anom_diff > 0 else "pos"
        card = "red" if anom_diff > 0 else "blue"
        st.markdown(f"""<div class="kpi-card {card}">
            <div class="kpi-label">Anomaly vs Baseline</div>
            <div class="kpi-number" style="color:{clr};">{sign}{anom_diff:.2f}</div>
            <div class="kpi-delta {css}">{icon} {sign}{anom_pct:.1f}% deviation</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""<div class="kpi-card amber">
            <div class="kpi-label">Peak Intensity</div>
            <div class="kpi-number" style="color:#f59e0b;">{slice_max:.2f} <span class="kpi-unit">{units}</span></div>
            <div class="kpi-delta neu">▸ Highest grid point</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""<div class="kpi-card blue">
            <div class="kpi-label">Lowest Value</div>
            <div class="kpi-number" style="color:#3b82f6;">{slice_min:.2f} <span class="kpi-unit">{units}</span></div>
            <div class="kpi-delta neu">▸ Minimum grid point</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # ── ECharts Row: Sparkline + Gauge ──────────────────────────────────────
    col_spark, col_gauge = st.columns([3, 1])

    with col_spark:
        try:
            times_labels = ds.time.dt.strftime('%Y').values.tolist()
        except (AttributeError, TypeError):
            times_labels = [str(t.year) for t in ds.time.values]
            
        ma = pd.Series(all_means).rolling(3, min_periods=1).mean().round(3).tolist()

        spark = {
            "backgroundColor": "transparent",
            "animation": True,
            "animationDuration": 1000,
            "tooltip": {"trigger": "axis",
                        "backgroundColor": "rgba(15,23,42,0.95)",
                        "borderColor": "rgba(56,189,248,0.3)", "borderWidth": 1,
                        "textStyle": {"color": "#e2e8f0", "fontSize": 13},
                        "axisPointer": {"type": "cross",
                                        "lineStyle": {"color": "rgba(56,189,248,0.3)"}}},
            "legend": {"data": ["Mean", "3-yr MA"],
                       "textStyle": {"color": "#64748b"}, "top": 0, "right": 0},
            "grid": {"left": "4%", "right": "3%", "top": "15%", "bottom": "18%",
                     "containLabel": True},
            "dataZoom": [{"type": "inside"}, {
                "height": 20, "handleStyle": {"color": "#38bdf8"},
                "textStyle": {"color": "#64748b"},
                "fillerColor": "rgba(56,189,248,0.08)",
                "borderColor": "rgba(56,189,248,0.2)"}],
            "xAxis": {"type": "category", "data": times_labels,
                      "axisLabel": {"color": "#475569", "fontSize": 11},
                      "axisLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}}},
            "yAxis": {"type": "value", "name": units,
                      "nameTextStyle": {"color": "#475569"},
                      "axisLabel": {"color": "#475569"},
                      "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.04)", "type": "dashed"}}},
            "series": [
                {"name": "Mean", "type": "line", "data": all_means, "smooth": True,
                 "showSymbol": True, "symbolSize": 8,
                 "lineStyle": {"width": 2.5, "color": "#818cf8"},
                 "itemStyle": {"color": "#818cf8", "borderWidth": 2, "borderColor": "#0f172a"},
                 "areaStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                               "colorStops": [{"offset": 0, "color": "rgba(129,140,248,0.3)"},
                                              {"offset": 1, "color": "rgba(129,140,248,0)"}]}},
                 "markPoint": {"data": [{"type": "max", "itemStyle": {"color": "#ef4444"}},
                                        {"type": "min", "itemStyle": {"color": "#38bdf8"}}],
                               "label": {"color": "#fff", "fontSize": 11}},
                 "markLine": {"data": [{"type": "average"}],
                              "lineStyle": {"type": "dashed", "color": "#f59e0b", "width": 1.5},
                              "label": {"color": "#f59e0b"}}},
                {"name": "3-yr MA", "type": "line", "data": ma, "smooth": True,
                 "showSymbol": False, "lineStyle": {"width": 2, "type": "dashed", "color": "#f59e0b"},
                 "itemStyle": {"color": "#f59e0b"}}
            ]
        }
        st.markdown("""<div class="section-tag" style="margin-bottom:0.4rem">
            <span class="tag-line" style="background:linear-gradient(90deg,#818cf8,#a855f7)"></span>
            <span style="font-size:0.82rem;font-weight:600;color:#818cf8;text-transform:uppercase;letter-spacing:0.08em;">Global Mean Trend — All Time Steps</span>
        </div>""", unsafe_allow_html=True)
        render_echarts(spark, height=200)

    with col_gauge:
        gauge_val   = round(min(abs(anom_pct), 50), 1)
        gauge_color = "#ef4444" if anom_diff > 0 else "#38bdf8"
        gauge_label = "Warming" if anom_diff > 0 else "Cooling"

        gauge = {
            "backgroundColor": "transparent",
            "animation": True,
            "series": [{
                "type": "gauge",
                "startAngle": 200, "endAngle": -20,
                "min": 0, "max": 50,
                "radius": "95%", "center": ["50%", "60%"],
                "progress": {"show": True, "width": 12, "itemStyle": {"color": gauge_color}},
                "axisLine": {"lineStyle": {"width": 12, "color": [[1, "rgba(255,255,255,0.05)"]]}},
                "axisLabel": {"show": False}, "axisTick": {"show": False}, "splitLine": {"show": False},
                "pointer": {"show": True, "length": "55%", "width": 4, "itemStyle": {"color": gauge_color}},
                "anchor": {"show": True, "size": 10, "itemStyle": {"color": gauge_color}},
                "detail": {"valueAnimation": True, "formatter": f"{{value}}%",
                           "color": gauge_color, "fontSize": 18,
                           "fontWeight": "bold", "offsetCenter": [0, "25%"]},
                "title": {"show": True, "color": "#475569", "fontSize": 11,
                          "offsetCenter": [0, "-15%"]},
                "data": [{"value": gauge_val, "name": gauge_label}]
            }]
        }
        st.markdown("""<div class="section-tag" style="margin-bottom:0.4rem">
            <span class="tag-line" style="background:linear-gradient(90deg,#ef4444,#f59e0b)"></span>
            <span style="font-size:0.82rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;">Anomaly Gauge</span>
        </div>""", unsafe_allow_html=True)
        render_echarts(gauge, height=200)


def render_insight_panel(ds, controls, ai_client=None):
    insight_text = ClimateProcessor.generate_automated_insight(
        ds, controls["variable"], controls["time_index"], ai_client=ai_client)
    st.markdown(f"""<div class="insight-panel">
        <strong>💡 Automated Intelligence Insight</strong><br/>{insight_text}
    </div>""", unsafe_allow_html=True)
