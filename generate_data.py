import xarray as xr
import numpy as np
import pandas as pd
import cftime
import os

def generate_climate_data(filename="climate_data.nc"):
    print(f"Generating synthetic climate data: {filename}...")
    
    # Define dimensions
    lat = np.linspace(-90, 90, 73)  # 2.5 degree resolution
    lon = np.linspace(-180, 180, 144) # 2.5 degree resolution
    
    # Use cftime noleap calendar to simulate CESM output
    time = xr.cftime_range(start="2020-01-01", periods=48, freq="MS", calendar="noleap")
    
    # Create realistic-looking data with seasonal variations and trends
    # Temperature: warmer at equator, colder at poles, seasonal cycle
    lat_rad = np.deg2rad(lat)
    temp_base = 30 * np.cos(lat_rad)[:, np.newaxis] - 10 # Base temp based on latitude
    
    # Pre-allocate arrays
    temp_data = np.zeros((len(time), len(lat), len(lon)))
    precip_data = np.zeros((len(time), len(lat), len(lon)))
    wind_data = np.zeros((len(time), len(lat), len(lon)))
    
    for i, t in enumerate(time):
        month = t.month
        # Seasonal temp variation (Northern Hemisphere summer is warmer)
        season_mod = 15 * np.sin(np.pi * (month - 4) / 6) * np.sin(lat_rad)[:, np.newaxis]
        # Global warming trend (slight increase over time)
        trend = i * 0.05
        # Noise
        noise = np.random.normal(0, 2, (len(lat), len(lon)))
        temp_data[i] = temp_base + season_mod + trend + noise
        
        # Precipitation: higher near equator and mid-latitudes, seasonal
        precip_base = 10 * np.cos(lat_rad * 2)[:, np.newaxis] + 5
        precip_noise = np.random.exponential(5, (len(lat), len(lon)))
        precip_data[i] = np.maximum(0, precip_base + precip_noise)
        
        # Wind Speed: higher at mid-latitudes
        wind_base = 15 * np.abs(np.sin(lat_rad * 2))[:, np.newaxis] + 2
        wind_noise = np.random.normal(0, 3, (len(lat), len(lon)))
        wind_data[i] = np.maximum(0, wind_base + wind_noise)

    # Create Dataset
    ds = xr.Dataset(
        data_vars=dict(
            temperature=(["time", "lat", "lon"], temp_data, {"units": "Celsius", "long_name": "Surface Temperature"}),
            precipitation=(["time", "lat", "lon"], precip_data, {"units": "mm/month", "long_name": "Total Precipitation"}),
            wind_speed=(["time", "lat", "lon"], wind_data, {"units": "m/s", "long_name": "Wind Speed at 10m"}),
        ),
        coords=dict(
            lon=(["lon"], lon, {"units": "degrees_east", "long_name": "Longitude"}),
            lat=(["lat"], lat, {"units": "degrees_north", "long_name": "Latitude"}),
            time=time,
        ),
        attrs=dict(description="Synthetic Climate Dataset for PyClimaExplorer Hackathon", source="Generated")
    )
    
    # Save to NetCDF
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    ds.to_netcdf(filename)
    print("Generation complete!")

if __name__ == "__main__":
    generate_climate_data("data/sample_climate_data.nc")
