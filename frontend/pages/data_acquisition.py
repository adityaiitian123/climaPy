import streamlit as st
import os
import datetime
from dotenv import load_dotenv
from backend.era5_downloader import ERA5Downloader

load_dotenv()


def render_data_acquisition_view():
    """Ultra-modern ERA5 Acquisition Portal. Integrates directly with CDS API."""

    st.markdown("""
        <div class="section-tag">
            <span class="tag-line" style="background:linear-gradient(90deg,#f59e0b,#ef4444)"></span>
            <h2 style="margin:0; font-size:1.5rem;">Orbital Data Acquisition Portal</h2>
        </div>
        <p style="color:#64748b; font-size:0.9rem; margin-top:0.5rem;">
            Direct interface to the Copernicus Climate Data Store (CDS). Retrieve planetary-scale ERA5
            reanalysis data for deep intelligence analysis.
        </p>
    """, unsafe_allow_html=True)

    # ─── API CONFIGURATION CARD ──────────────────────────────────────────────
    env_key = os.environ.get('CDS_API_KEY', '')
    env_url = os.environ.get('CDS_URL', 'https://cds.climate.copernicus.eu/api')

    with st.container():
        st.markdown("""
            <div class="glass-card" style="padding:1.5rem; margin-bottom:1.5rem; border-left:4px solid #f59e0b;">
                <h3 style="margin:0; color:#f59e0b; font-size:1.1rem;">🛰️ CDS API Intelligence Access</h3>
                <p style="font-size:0.8rem; color:#94a3b8; margin-top:0.5rem;">
                    API v3 — key only (no UID needed).
                    Get yours at <a href="https://cds.climate.copernicus.eu/how-to-api" target="_blank"
                    style="color:#38bdf8;">cds.climate.copernicus.eu</a>.
                </p>
            </div>
        """, unsafe_allow_html=True)

        col_url, col_key = st.columns([1, 2])
        with col_url:
            cds_url = st.text_input("CDS URL", value=env_url, help="Copernicus CDS API Endpoint (v3)")
        with col_key:
            cds_key = st.text_input("CDS API Key", type="password", value=env_key,
                                     help="Your Personal API Key from your CDS Profile")

        if env_key:
            st.markdown("""
                <div style="display:flex; align-items:center; gap:8px; margin-top:-8px; margin-bottom:4px;">
                    <span style="display:inline-block; width:7px; height:7px; background:#10b981;
                                 border-radius:50%; box-shadow:0 0 5px #10b981;"></span>
                    <span style="font-size:0.75rem; color:#10b981;">KEY LOADED FROM ENVIRONMENT — READY TO TRANSMIT</span>
                </div>
            """, unsafe_allow_html=True)

    # ─── REQUEST PARAMETERS ──────────────────────────────────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    form_col1, form_col2 = st.columns([1, 1])

    with form_col1:
        st.subheader("📍 Geospatial Target")

        var_options = {
            "2m Temperature":           "2m_temperature",
            "Total Precipitation":      "total_precipitation",
            "Mean Sea Level Pressure":  "mean_sea_level_pressure",
            "10m U-Wind":               "10m_u_component_of_wind",
            "10m V-Wind":               "10m_v_component_of_wind",
            "Surface Pressure":         "surface_pressure",
            "Orography":                "orography",
        }
        variable = st.multiselect("Variable(s)", options=list(var_options.keys()), default=["2m Temperature"])

        region = st.selectbox("Intelligence Region",
                              ["Global", "Europe", "North America", "Custom Coordinates"])

        area = [90, -180, -90, 180]
        if region == "Europe":
            area = [71, -25, 34, 45]
        elif region == "North America":
            area = [72, -170, 15, -50]
        elif region == "Custom Coordinates":
            c1, c2 = st.columns(2)
            with c1:
                n = st.number_input("North Lat", value=90.0)
                w = st.number_input("West Lon",  value=-180.0)
            with c2:
                s = st.number_input("South Lat", value=-90.0)
                e = st.number_input("East Lon",  value=180.0)
            area = [n, w, s, e]

    with form_col2:
        st.subheader("⏳ Temporal Window")
        today = datetime.date.today()
        start_date = st.date_input("Start Date", value=today - datetime.timedelta(days=7))
        end_date   = st.date_input("End Date",   value=today - datetime.timedelta(days=1))
        times = st.multiselect("Temporal Steps (Daily)",
                               options=[f"{h:02d}:00" for h in range(24)],
                               default=["00:00", "12:00"])

    # ─── ACTION SECTION ──────────────────────────────────────────────────────
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    target_filename = st.text_input(
        "Target Filename",
        value=f"era5_download_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.nc"
    )

    if st.button("🚀 INITIATE ACQUISITION", use_container_width=True, type="primary"):
        if not cds_key:
            st.error("❌ Authentication Breach: CDS API Key is required.")
        else:
            with st.status("📡 Establishing Connection to Copernicus Climate Data Store...",
                           expanded=True) as status:
                try:
                    downloader = ERA5Downloader(api_key=cds_key, url=cds_url)
                    var_codes = [var_options[v] for v in variable]

                    delta     = (end_date - start_date).days + 1
                    all_dates = [start_date + datetime.timedelta(days=i) for i in range(delta)]
                    years  = sorted(list(set([str(d.year)         for d in all_dates])))
                    months = sorted(list(set([f"{d.month:02d}"   for d in all_dates])))
                    days   = sorted(list(set([f"{d.day:02d}"     for d in all_dates])))

                    req_dict = downloader.create_request_dict(
                        variable=var_codes, years=years,
                        months=months, days=days, times=times, area=area
                    )
                    output_path = os.path.join("data", "downloads", target_filename)

                    st.write("🛰️ Validating parameters...")
                    st.write(f"📥 Target: `{target_filename}`")
                    st.write(f"💼 Payload: `{len(var_codes)} vars | {len(years)} years | {len(days)} days`")

                    status.update(
                        label="🧬 Processing on CDS Infrastructure... (may take several minutes)",
                        state="running"
                    )

                    filepath = downloader.download_request(
                        'reanalysis-era5-single-levels', req_dict, output_path
                    )

                    status.update(label="✅ Acquisition Complete. Data Integrated.",
                                  state="complete", expanded=False)
                    st.success(f"Successfully downloaded to `{filepath}`")
                    st.session_state.era5_ready_path = filepath

                except Exception as e:
                    st.error(f"📡 Acquisition Failure: {str(e)}")
                    status.update(label="❌ Acquisition Aborted", state="error")

    # ─── INJECT CARD (persists across reruns via session_state) ──────────────
    if st.session_state.get('era5_ready_path'):
        ready_path = st.session_state.era5_ready_path
        ready_name = os.path.basename(ready_path)
        st.markdown(f"""
            <div style="padding:1rem; border:1px solid #10b981; border-radius:12px;
                        background:rgba(16,185,129,0.05); margin-top:1.5rem;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.5rem;">
                    <span style="display:inline-block; width:9px; height:9px; background:#10b981;
                                 border-radius:50%; box-shadow:0 0 8px #10b981;"></span>
                    <span style="color:#10b981; font-weight:700; font-size:0.9rem;">Intelligence Ready</span>
                </div>
                <div style="font-size:0.8rem; color:#94a3b8; font-family:monospace;">{ready_name}</div>
                <div style="font-size:0.75rem; color:#475569; margin-top:0.3rem;">
                    Click below — activates across all intelligence views &amp; sidebar indicator.
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ Inject Into Global Analysis Engine", use_container_width=True, type="primary"):
            st.session_state.DATA_PATH         = ready_path
            st.session_state.era5_injected_path = ready_path   # → Triggers sidebar badge
            st.session_state.pop('era5_ready_path', None)       # Clear staging state
            st.rerun()

    # ─── LOGS / CONSOLE ──────────────────────────────────────────────────────
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    with st.expander("📝 Systematic Logs", expanded=False):
        st.code("""
[SYSTEM] Initializing Acquisition Module...
[AUTH]   Waiting for CDS Credentials...
[GEOS]   Area selection loaded.
[CDS]    Connecting to Copernicus server...
        """, language="bash")


def render_status_dot(active=True):
    color = "#10b981" if active else "#ef4444"
    return (f'<span style="display:inline-block; width:8px; height:8px; background:{color}; '
            f'border-radius:50%; margin-right:5px; box-shadow:0 0 5px {color};"></span>')
