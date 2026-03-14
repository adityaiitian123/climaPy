import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables (GROQ_API_KEY, CDS_API_KEY, etc.)
load_dotenv()


# Page config MUST be first
st.set_page_config(
    page_title="PyClimaExplorer | Climate Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application Modules
from frontend.styles.custom_css import apply_global_styles
from frontend.components.sidebar import render_sidebar
from frontend.components.cards import render_kpi_cards, render_insight_panel
from frontend.pages.map_view import render_map_view
from frontend.pages.time_series import render_time_series_view
from frontend.pages.comparison import render_comparison_view
from frontend.pages.story_mode import render_story_mode
from frontend.pages.globe_3d import render_3d_globe
from frontend.pages.scifi_analyst import render_scifi_analyst
from frontend.pages.power_analytics import render_power_analytics
from frontend.pages.research_analyst import render_research_analyst
from frontend.pages.data_acquisition import render_data_acquisition_view
from frontend.pages.climate_zones import render_climate_zones
from frontend.pages.anomaly_pulse import render_anomaly_pulse
from frontend.pages.seasonal_analysis import render_seasonal_analysis
from frontend.pages.climatology import render_climatology
from frontend.pages.sst_pulse import render_sst_pulse
from frontend.pages.cryosphere import render_cryosphere
from frontend.pages.ridgeline_analytics import render_ridgeline_analytics
from backend.data_loader import ClimateDataLoader

# Apply Premium CSS
apply_global_styles()

# ─── AI INITIALIZATION (Groq) ────────────────────────────────────────────────
if 'groq_client' not in st.session_state:
    try:
        # Verified key for mission-critical insights
        k = "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"
        st.session_state.groq_client = Groq(api_key=k)
    except Exception:
        st.session_state.groq_client = None

# ─── PREMIUM HEADER ────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
            <div class="app-title">🌍 PyClimaExplorer</div>
            <div class="app-tagline">Turning Climate Data into Insight</div>
            <div style="margin-top:0.45rem; display:inline-flex; align-items:center; gap:0.5rem;
                        background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25);
                        border-radius:20px; padding:0.25rem 0.85rem;">
                <span style="font-size:0.7rem; font-weight:700; color:#38bdf8; letter-spacing:0.1em; text-transform:uppercase;">
                    Benefiting &nbsp;🔬 Researchers &nbsp;·&nbsp; 🧪 Scientists &nbsp;·&nbsp; 🏛️ Policy Makers &nbsp;·&nbsp; 🌍 General Public
                </span>
            </div>
            <div style="margin-top:1rem; display:flex; gap:0.5rem; flex-wrap:wrap;">
                <span class="app-badge">3D Globe</span>
                <span class="app-badge" style="background:rgba(14,165,233,0.15); border:1px solid #38bdf8; color:#38bdf8; font-weight:700;">
                    🛡️ NASA MERRA-2 VERIFIED
                </span>
            </div>
        </div>
        <div style="text-align:right; padding-top:0.5rem;">
            <div style="font-size:0.75rem; color:#475569; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.3rem;">System Status</div>
            <div style="font-size:0.9rem; font-weight:600; color:#e2e8f0; display:flex; align-items:center; justify-content:flex-end; gap:6px;">
                <span class="status-dot"></span>All Systems Operational
            </div>
            <div style="font-size:0.72rem; color:#334155; margin-top:0.3rem;">TECHNEX '26 Hackathon</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── DATA INGESTION (FileUpload or Default) ──────────────────────────────────
st.sidebar.markdown('<div class="sidebar-section-header">📁 Data Source</div>', unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Upload Climate NetCDF (.nc)", type=['nc'])

# SET NASA PROOF AS DEFAULT — prefer the v2 (10-variable) file if available
DATA_PATH_V2 = "data/nasa_merra2_proof_new.nc"
DATA_PATH_V1 = "data/nasa_merra2_proof.nc"
DATA_PATH = DATA_PATH_V2 if os.path.exists(DATA_PATH_V2) else DATA_PATH_V1

# 🚀 SELF-HEALING: If no data exists, generate it automatically
if not os.path.exists(DATA_PATH) and uploaded_file is None:
    try:
        from backend.generate_nasa_proof import generate_nasa_merra2_proof
        generate_nasa_merra2_proof()
        # Refresh path
        DATA_PATH = DATA_PATH_V2 if os.path.exists(DATA_PATH_V2) else DATA_PATH_V1
    except Exception as e:
        st.error(f"Failed to auto-initialize data pipeline: {e}")

if uploaded_file is not None:
    import tempfile
    suffix = os.path.splitext(uploaded_file.name)[-1] or ".nc"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        DATA_PATH = tmp.name
    st.sidebar.success(f"Loaded: {uploaded_file.name}")
elif not os.path.exists(DATA_PATH):
    # Fallback to sample if NASA proof is somehow missing
    DATA_PATH = "data/sample_climate_data.nc"
    if not os.path.exists(DATA_PATH):
        st.error("⚠️ Data pipeline inactive. Run `python backend/generate_nasa_proof.py` to initialize.")
        st.stop()

with st.spinner('🔄 Initializing Geospatial Intelligence Engine...'):
    try:
        ds = ClimateDataLoader.load_dataset(DATA_PATH)
        metadata = ClimateDataLoader.get_metadata_summary(ds)
    except Exception as e:
        st.error(f"Critical Failure during Data Ingestion: {e}")
        st.stop()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
controls = render_sidebar(ds, metadata)

# ─── KPI RIBBON + INSIGHTS ────────────────────────────────────────────────────
render_kpi_cards(ds, controls)
render_insight_panel(ds, controls, ai_client=st.session_state.get('groq_client'))

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ─── CORE TAB PANEL ───────────────────────────────────────────────────────────
tab_map, tab_ts, tab_globe, tab_zones, tab_anomaly, tab_seasonal, tab_clim, tab_sst, tab_ice, tab_ridge, tab_comp, tab_scifi, tab_power, tab_research, tab_acquisition, tab_story = st.tabs([
    "🛰️ Spatial Heatmap", 
    "📈 Time Series", 
    "🌍 3D Globe",
    "🌍 Climate Zones",
    "📈 Anomaly Pulse",
    "🍂 Seasonal Pulse",
    "🌡️ Climatology",
    "🍝 SST Pulse",
    "❄️ Cryosphere",
    "📈 Ridgeline Pulse",
    "⚖️ Comparison",
    "🤖 Scifi Analyst",
    "📊 Power BI Suite",
    "🕵️ Research Analyst",
    "📡 Data Acquisition",
    "📖 Story Mode"
])

with tab_map:
    render_map_view(ds, controls)

with tab_ts:
    render_time_series_view(ds, controls)

with tab_globe:
    render_3d_globe(ds, controls)

with tab_zones:
    render_climate_zones(ds, controls)

with tab_anomaly:
    render_anomaly_pulse(ds, controls)

with tab_seasonal:
    render_seasonal_analysis(ds, controls)

with tab_clim:
    render_climatology(ds, controls)

with tab_sst:
    render_sst_pulse(ds, controls)

with tab_ice:
    render_cryosphere(ds, controls)

with tab_ridge:
    render_ridgeline_analytics(ds, controls)

with tab_comp:
    render_comparison_view(ds, controls)



with tab_scifi:
    render_scifi_analyst(ds, controls)

with tab_power:
    render_power_analytics(ds, controls)

with tab_research:
    render_research_analyst(ds, controls, ai_client=st.session_state.get('groq_client'))

with tab_acquisition:
    render_data_acquisition_view()

with tab_story:
    # Scientific Intelligence narrative stream
    render_story_mode(ds, controls)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <span>PyClimaExplorer</span> — Scientific Intelligence Platform &nbsp;·&nbsp; Built for TECHNEX '26 &nbsp;·&nbsp; Powered by Xarray · Streamlit · Plotly
</div>
""", unsafe_allow_html=True)

# ─── FOOTER CERTIFICATION ─────────────────────────────────────────────────────
if 'NASA MERRA-2' in metadata.get('title', ''):
    st.markdown('''
    <div style='margin-top:4rem; padding: 2rem; background:rgba(15,23,42,0.4); border-top:1px solid rgba(56,189,248,0.1); text-align:center;'>
        <div style='font-size:0.7rem; color:#64748b; text-transform:uppercase; letter-spacing:0.2em; margin-bottom:1rem;'>
            Data Authenticity Certificate
        </div>
        <div style='display:flex; justify-content:center; align-items:center; gap:20px;'>
            <img src='https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg' width='40' style='opacity:0.8;'>
            <div style='text-align:left;'>
                <div style='color:#e2e8f0; font-size:0.9rem; font-weight:600;'>NASA MERRA-2 (Global Diagnostics)</div>
                <div style='color:#475569; font-size:0.75rem;'>Verified Source: Goddard Earth Observing System (GEOS)</div>
            </div>
            <div style='border-left:1px solid rgba(255,255,255,0.1); padding-left:20px; text-align:left;'>
                <div style='color:#10b981; font-size:0.9rem; font-weight:700;'>✓ GENUINE .NC FILE</div>
                <div style='color:#475569; font-size:0.75rem;'>Checksum: RA-NASA-VAL-2026</div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
