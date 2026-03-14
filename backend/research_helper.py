import xarray as xr
import pandas as pd
import numpy as np
import streamlit as st
from backend.climate_processor import ClimateProcessor

class ResearchHelper:
    """Advanced pattern recognition engine for climate data analysis."""

    @staticmethod
    def identify_spatial_clusters(ds: xr.Dataset, variable: str, time_index: int) -> list:
        """Identifies hotspots or clusters of high/low anomalies with dynamic coordinate awareness."""
        try:
            da = ds[variable].isel(time=time_index)
            # Find coordinate names dynamically
            lat_dim = next((d for d in da.dims if 'lat' in d.lower()), 'lat')
            lon_dim = next((d for d in da.dims if 'lon' in d.lower()), 'lon')
            
            std_v = float(da.std())
            mean_v = float(da.mean())
            
            if std_v < 1e-7: return []

            # 1. Detect Warming Hotspots (Top Anomalies)
            hot_threshold = mean_v + 1.1 * std_v 
            hot_pts = da.where(da > hot_threshold, drop=True)
            if hot_pts.size == 0:
                hot_pts = da.where(da > (mean_v + 0.6 * std_v), drop=True)

            hotspots = []
            if hot_pts.size > 0:
                # dropna() is CRITICAL to keep only the points that matched the condition
                df_hot = hot_pts.to_dataframe(name='val').reset_index().dropna(subset=['val']).sort_values('val', ascending=False).head(3)
                for _, row in df_hot.iterrows():
                    hotspots.append({
                        "lat": round(float(row[lat_dim]), 2),
                        "lon": round(float(row[lon_dim]), 2),
                        "intensity": round(float(row['val']), 2),
                        "type": "WARMING"
                    })

            # 2. Detect Cooling Zones (Bottom Anomalies)
            cold_threshold = mean_v - 1.1 * std_v
            cold_pts = da.where(da < cold_threshold, drop=True)
            if cold_pts.size == 0:
                cold_pts = da.where(da < (mean_v - 0.6 * std_v), drop=True)
            
            if cold_pts.size > 0:
                df_cold = cold_pts.to_dataframe(name='val').reset_index().dropna(subset=['val']).sort_values('val', ascending=True).head(4 - len(hotspots))
                for _, row in df_cold.iterrows():
                    hotspots.append({
                        "lat": round(float(row[lat_dim]), 2),
                        "lon": round(float(row[lon_dim]), 2),
                        "intensity": round(float(row['val']), 2),
                        "type": "COOLING"
                    })
            return hotspots
        except Exception:
            return []

    @staticmethod
    def detect_oscillations(ds: xr.Dataset, variable: str) -> dict:
        """Detects periodic patterns or seasonality with adaptive windowing for short data."""
        try:
            # Global mean time series
            ts = ds[variable].mean(dim=['lat', 'lon']).to_series()
            
            if len(ts) < 3:
                return {"cycle_frequency": "Static", "instability_index": 0.0, "peak_count": 0, "is_volatile": False}

            # Adaptive window: for 12 months, use 3 months to see seasonality
            window = 3 if len(ts) <= 24 else 12
            rolling = ts.rolling(window=window, center=True).mean()
            residuals = ts - rolling
            
            # Calculate standard deviation of residuals as 'instability'
            valid_residuals = residuals.dropna()
            if valid_residuals.empty:
                # If window still too large, fall back to simple mean subtraction
                valid_residuals = ts - ts.mean()
            
            inst_val = float(valid_residuals.std())
            instability = inst_val if not np.isnan(inst_val) else 0.0
            
            # Find max/min peaks
            threshold = valid_residuals.std() if not np.isnan(valid_residuals.std()) else 1.0
            peaks = len(valid_residuals[valid_residuals > threshold])
            
            return {
                "cycle_frequency": "Sub-seasonal" if len(ts) < 24 else "Multi-annual",
                "instability_index": round(float(instability), 4),
                "peak_count": peaks,
                "is_volatile": bool(instability > (ts.std() * 0.3)) if not np.isnan(ts.std()) else False
            }
        except Exception:
            return {"cycle_frequency": "Unknown", "instability_index": 0.0, "peak_count": 0, "is_volatile": False}

    @staticmethod
    def generate_aadhya_report(ds: xr.Dataset, variable: str, t_idx: int, ai_client=None) -> dict:
        """Generates a structured scientific report for Dr. Aadhya with strong data-source consciousness."""
        clusters = ResearchHelper.identify_spatial_clusters(ds, variable, t_idx)
        cycles = ResearchHelper.detect_oscillations(ds, variable)
        stats = ClimateProcessor.get_statistical_summary(ds, variable, t_idx)
        
        # 1. Background Awareness: Check for NASA METADATA
        source_is_nasa = False
        attrs_str = str(ds.attrs).upper()
        if any(term in attrs_str for term in ["NASA", "MERRA", "GMAO"]):
            source_is_nasa = True

        # 2. Determine "Hidden Pattern" score
        raw_score = (len(clusters) * 15) + (int(cycles['is_volatile']) * 20) + (abs(stats.get('skew', 0)) * 10)
        pattern_score = round(float(min(100, raw_score)), 1)
        
        # 3. AI DIALOGUE GENERATION
        ui_mode = st.session_state.get("ui_mode", "public")
        
        if ai_client:
            try:
                if ui_mode == "public":
                    system_prompt = "You are Dr. Aadhya, a friendly AI Climate Guide. Use simple analogies, avoid jargon, and be encouraging."
                else:
                    system_prompt = "You are Dr. Aadhya, a senior AI Climate Research Scientist. Use high-level scientific terminology and mention NASA if they are the source."
                
                context = f"Analyzing {variable}. Pattern Score: {pattern_score}%. "
                if source_is_nasa:
                    context += "CRITICAL: This is NASA MERRA-2 Verified Data. Mention NASA."
                
                user_msg = f"""
                Profile: Skew={stats.get('skew', 0):.2f}, Kurtosis={stats.get('kurt', 0):.2f}, Instability={cycles['instability_index']}.
                {context}
                Provide a short analytical quote as Dr. Aadhya.
                """
                
                completion = ai_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg}
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.7
                )
                mood = completion.choices[0].message.content.replace('"', '')
            except Exception:
                mood = f"Analyzing planetary telemetry. Signal suggests significant {variable} variance."
        else:
            mood = "Dr. Aadhya here. Pattern coherence identified in planetary telemetry flux."
        
        return {
            "dialogue": mood,
            "clusters": clusters,
            "cycles": cycles,
            "stats": stats,
            "pattern_score": pattern_score,
            "is_nasa": source_is_nasa,
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_id": f"RA-{variable[:3].upper()}-{t_idx:03d}"
        }
