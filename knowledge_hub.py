import streamlit as st

class KnowledgeHub:
    """Educational companion for public-friendly climate data exploration."""
    
    GLOSSARY = {
        "Temperature": {
            "expert": "2-meter air temperature (K/C)",
            "public": "Surface Temperature: How hot or cold it feels where people live."
        },
        "Anomalies": {
            "expert": "Departure from long-term climatological mean.",
            "public": "Anomalies: How much today's weather differs from the 'normal' average of the last 30 years."
        },
        "Zonal Mean": {
            "expert": "Averaging across longitudinal circles per latitude line.",
            "public": "East-West Average: The average temperature across the whole world at a specific latitude (like the Equator)."
        },
        "NetCDF": {
            "expert": "Network Common Data Form for array-oriented scientific data.",
            "public": "Data File: A professional scientific file containing thousands of weather measurements."
        },
        "MERRA-2": {
            "expert": "Modern-Era Retrospective analysis for Research and Applications, Version 2.",
            "public": "Satellite Record: A high-quality record of Earth's weather captured by NASA satellites since 1980."
        }
    }

    @staticmethod
    def render_infotip(term: str):
        """Renders a simplified tooltip if Public Mode is active."""
        mode = st.session_state.get("ui_mode", "public")
        info = KnowledgeHub.GLOSSARY.get(term, {})
        
        if mode == "public":
            st.markdown(f"""
            <div style='background:rgba(56,189,248,0.05); padding:0.5rem; border-radius:8px; border-left:3px solid #38bdf8; margin:0.5rem 0;'>
                <span style='font-size:0.75rem; color:#38bdf8; font-weight:700;'>💡 KNOWLEDGE BYTE</span><br>
                <span style='font-size:0.85rem; color:#e2e8f0;'>{info.get("public", "Insight active.")}</span>
            </div>
            """, unsafe_allow_html=True)

    @staticmethod
    def get_public_analogy(metric_name: str) -> str:
        """Returns a friendly analogy for complex metrics."""
        analogies = {
            "precip": "Like a bucket filling up across the whole city.",
            "temp": "Think of this as the Earth's basic temperature, like a body's fever check.",
            "pressure": "Like the weight of the air pressing down on us."
        }
        return analogies.get(metric_name.lower()[:5], "Nature's signal.")
