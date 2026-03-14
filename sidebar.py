import streamlit as st
import pandas as pd

def render_sidebar(ds, metadata):
    """Renders the premium control sidebar and returns user selections."""
    controls = {}
    
    # === NASA Verification Shield ===
    if "NASA MERRA-2" in metadata.get("title", ""):
        st.sidebar.markdown(f"""
        <div style="background:linear-gradient(135deg, rgba(14,165,233,0.1) 0%, rgba(56,189,248,0.05) 100%);
                    border:1px solid rgba(56,189,248,0.3); border-radius:12px; padding:1rem; margin-bottom:1.5rem;
                    position:relative; overflow:hidden;">
            <div style="position:absolute; top:-10px; right:-10px; opacity:0.1; font-size:4rem;">🛡️</div>
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.7rem;">
                <div style="background:#0ea5e9; color:white; border-radius:50%; width:20px; height:20px; 
                            display:flex; align-items:center; justify-content:center; font-size:0.7rem;">✓</div>
                <div style="font-size:0.7rem; font-weight:700; color:#e2e8f0; text-transform:uppercase; letter-spacing:0.1em;">
                    Authenticity Certified
                </div>
            </div>
            <div style="font-size:0.8rem; color:#cbd5e1; line-height:1.4;">
                This system is currently utilizing the <b>NASA MERRA-2</b> Global Diagnostics dataset.
            </div>
            <div style="margin-top:0.8rem; border-top:1px solid rgba(255,255,255,0.06); padding-top:0.6rem;">
                <a href="https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich785.pdf" target="_blank" 
                   style="font-size:0.65rem; color:#38bdf8; text-decoration:none; display:flex; align-items:center; gap:5px;">
                   🔗 View NASA Documentation
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # === Brand Mark ===
    st.sidebar.markdown("""
    <div style="padding: 0.5rem 0 0.8rem; text-align: center;">
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:700;
                    background:linear-gradient(100deg,#38bdf8,#818cf8); -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent; letter-spacing:-0.02em;">
            🌍 PyClimaExplorer
        </div>
        <div style="font-size:0.65rem; color:#334155; text-transform:uppercase;
                    letter-spacing:0.1em; margin-top:0.2rem;">
            Intelligence Platform
        </div>
    </div>
    <div style="height:1px; background:linear-gradient(90deg,transparent,rgba(56,189,248,0.3),transparent); margin-bottom:1.2rem;"></div>
    """, unsafe_allow_html=True)

    # === Variable Selector ===
    st.sidebar.markdown('<div class="sidebar-section-header">🎛 Observation Metric</div>', unsafe_allow_html=True)
    variables = metadata.get("variables", [])
    
    if not variables:
        st.sidebar.error("❌ No data variables found in dataset.")
        st.sidebar.info("Please ensure your NetCDF file contains observational data.")
        controls["variable"] = None
        controls["units"] = "N/A"
        return controls

    var_info = metadata.get("var_info", {})
    # Use .get() and fallbacks to prevent KeyError
    friendly_names = {v: var_info.get(v, {}).get("long_name", v) for v in variables}
    
    selected_var = st.sidebar.selectbox(
        "Select Metric", 
        variables, 
        index=0,
        format_func=lambda x: friendly_names.get(x, x), 
        label_visibility="collapsed"
    )
    
    controls["variable"] = selected_var
    # FIXED: Robust unit access using .get()
    controls["units"]    = var_info.get(selected_var, {}).get("units", "units")

    st.sidebar.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    # === Time Slider ===
    if "time" in ds.coords:
        times = ds.time
        try:
            time_labels = times.dt.strftime('%Y-%m-%d').values.tolist()
        except (AttributeError, TypeError):
            time_labels = [f"{t.year}-{t.month:02d}-{t.day:02d}" for t in times.values]
            
        st.sidebar.markdown('<div class="sidebar-section-header">📅 Temporal Axis</div>', unsafe_allow_html=True)
        selected_time_index = st.sidebar.slider("", 0, len(times) - 1, 0, format="%d", label_visibility="collapsed")
        controls["time_index"] = selected_time_index
        controls["time_value"] = time_labels[selected_time_index]
        
        st.sidebar.markdown(f"""
        <div style="background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.2);
                    border-radius:8px;padding:0.6rem 0.9rem;margin-top:0.5rem;font-size:0.85rem;
                    color:#38bdf8;font-weight:600;text-align:center;">
            📍 {time_labels[selected_time_index]}
        </div>
        """, unsafe_allow_html=True)
    else:
        controls["time_index"] = 0
        controls["time_value"] = "Static"

    st.sidebar.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.sidebar.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.07),transparent);margin-bottom:1rem;"></div>', unsafe_allow_html=True)

    # === Dataset Inspector ===
    with st.sidebar.expander("🔍 Dataset Inspector", expanded=False):
        st.markdown(f"**{metadata.get('title', 'Climate Dataset')}**", unsafe_allow_html=True)
        items = [
            ("Coverage", metadata.get('spatial_coverage', 'Global')),
            ("Period", metadata.get('time_coverage', 'N/A')),
        ]
        for label, val in items:
            st.markdown(f"<div style='font-size:0.78rem;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;margin-top:0.5rem'>{label}</div><div style='color:#cbd5e1;font-size:0.9rem'>{val}</div>", unsafe_allow_html=True)
        
        dimensions = metadata.get('dimensions', {})
        if dimensions:
            st.markdown("<div style='margin-top:0.8rem;font-size:0.78rem;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;'>Dimensions</div>", unsafe_allow_html=True)
            for dim, size in dimensions.items():
                st.markdown(f"<code style='color:#38bdf8;background:rgba(56,189,248,0.08);padding:2px 8px;border-radius:4px;font-size:0.82rem;'>{dim}: {size}</code> ", unsafe_allow_html=True)

    st.sidebar.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # === Variable Info ===
    with st.sidebar.expander("📊 Variable Details", expanded=False):
        for v in variables:
            info = var_info.get(v, {})
            selected_style = "background:rgba(56,189,248,0.1);border-color:rgba(56,189,248,0.3);" if v == selected_var else ""
            st.markdown(f"""
            <div style="border:1px solid rgba(255,255,255,0.06);border-radius:8px;
                        padding:0.6rem 0.8rem;margin-bottom:0.4rem;{selected_style}">
                <div style="font-weight:600;color:#e2e8f0;font-size:0.85rem;">{info.get('long_name', v)}</div>
                <div style="color:#475569;font-size:0.75rem;">Units: <code style="color:#94a3b8">{info.get('units', 'N/A')}</code></div>
            </div>
            """, unsafe_allow_html=True)

    return controls
