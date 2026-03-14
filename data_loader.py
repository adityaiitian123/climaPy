import xarray as xr
import pandas as pd
import os
import streamlit as st

class ClimateDataLoader:
    """Handles parsing and ingestion of NetCDF climate data."""
    
    @staticmethod
    @st.cache_resource(show_spinner=False)
    def load_dataset(filepath: str) -> xr.Dataset:
        """Loads a NetCDF file optimally, using dask caching for large models (CESM/ERA5)."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset not found at {filepath}")
        
        try:
            # For real-world CESM/ERA5 data, files can be massive.
            # We use chunks='auto' to enable out-of-core computation via dask.
            # We also enable use_cftime to handle non-standard calendars (e.g., noleap).
            ds = xr.open_dataset(filepath, chunks='auto', decode_times=True, use_cftime=True)
            
            # Normalize coordinate names (a common issue with scientific data)
            ds = ClimateDataLoader._normalize_coordinates(ds)
            return ds
        except Exception as e:
            raise RuntimeError(f"Failed to parse NetCDF file: {e}")

    @staticmethod
    def _normalize_coordinates(ds: xr.Dataset) -> xr.Dataset:
        """Ensures standard naming for lat, lon, and time."""
        rename_dict = {}
        for coord in ds.coords:
            coord_lower = str(coord).lower()
            if coord_lower in ['latitude', 'lat', 'y'] and str(coord) != 'lat':
                rename_dict[str(coord)] = 'lat'
            elif coord_lower in ['longitude', 'lon', 'x'] and str(coord) != 'lon':
                rename_dict[str(coord)] = 'lon'
            elif coord_lower in ['time', 'date', 't'] and str(coord) != 'time':
                rename_dict[str(coord)] = 'time'
        
        if rename_dict:
            ds = ds.rename(rename_dict)
        return ds

    @staticmethod
    def get_metadata_summary(ds: xr.Dataset) -> dict:
        """Extracts key metadata to power the Dataset Inspector UI."""
        variables = list(ds.data_vars)
        
        info = {
            "title": ds.attrs.get("title", ds.attrs.get("description", "Unknown Dataset")),
            "dimensions": dict(ds.sizes),
            "spatial_coverage": "",
            "time_coverage": "",
            "variables": variables,
            "var_info": {}
        }
        
        if 'lat' in ds.coords and 'lon' in ds.coords:
            info["spatial_coverage"] = f"Lat: {float(ds.lat.min()):.1f}° to {float(ds.lat.max()):.1f}°, Lon: {float(ds.lon.min()):.1f}° to {float(ds.lon.max()):.1f}°"
            
        if 'time' in ds.coords:
            times = ds.time
            if len(times) > 0:
                try:
                    formatted = times.dt.strftime('%Y-%m').values
                except (AttributeError, TypeError):
                    formatted = [f"{t.year}-{t.month:02d}" for t in times.values]
                info["time_coverage"] = f"{formatted[0]} to {formatted[-1]}"
                
        for v in variables:
            long_name = ds[v].attrs.get("long_name", v)
            units = ds[v].attrs.get("units", "unknown units")
            info["var_info"][v] = {"long_name": long_name, "units": units}
            
        return info
