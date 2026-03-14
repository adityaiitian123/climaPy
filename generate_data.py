import xarray as xr
import numpy as np
import pandas as pd
import os

def generate_complex_climate_data(filename="data/sample_climate_data.nc"):
    print(f"Generating premium synthetic climate data: {filename}...")
    
    # Define dimensions (slightly higher resolution for premium feel but keep size manageable)
    lat = np.linspace(-90, 90, 90)  # 2 degree resolution
    lon = np.linspace(-180, 180, 180) # 2 degree resolution
    time = pd.date_range("2010-01-01", "2023-12-31", freq="YE") # Annual data for 14 years
    
    lat_rad = np.deg2rad(lat)
    
    # 1. Temperature: Realistic base + warming trend + El Nino anomaly simulation
    temp_base = 28 * np.cos(lat_rad)[:, np.newaxis] - 20 # Base temp based on latitude
    temp_data = np.zeros((len(time), len(lat), len(lon)))
    
    # 2. Precipitation
    precip_base = 15 * np.cos(lat_rad * 2)[:, np.newaxis] + 5
    precip_data = np.zeros((len(time), len(lat), len(lon)))
    
    # 3. Wind Speed
    wind_base = 20 * np.abs(np.sin(lat_rad * 3))[:, np.newaxis] + 2
    wind_data = np.zeros((len(time), len(lat), len(lon)))

    for i, t in enumerate(time):
        year = t.year
        # Global warming trend (0.02 C per year increase)
        trend = i * 0.04
        
        # Simulate an El Nino / La Nina cycle for specific years (e.g. 2015-2016 El Nino)
        enso_anomaly = 0
        if year in [2015, 2016]:
            # Positive anomaly in equatorial Pacific
            enso_anomaly = 2.5 * np.exp(-((lat[:, np.newaxis] - 0)**2 / 100) - ((lon - -120)**2 / 1000))
        elif year in [2010, 2011, 2021, 2022]:
            # La Nina
            enso_anomaly = -1.5 * np.exp(-((lat[:, np.newaxis] - 0)**2 / 100) - ((lon - -120)**2 / 1000))
            
        # Add random noise
        noise = np.random.normal(0, 1.5, (len(lat), len(lon)))
        temp_data[i] = temp_base + trend + enso_anomaly + noise
        
        # Precip depends heavily on temperature/enso
        precip_noise = np.random.exponential(4, (len(lat), len(lon)))
        precip_enso_effect = enso_anomaly * 2 # El Nino brings rain to some areas
        precip_data[i] = np.maximum(0, precip_base + precip_enso_effect + precip_noise)
        
        # Wind
        wind_noise = np.random.normal(0, 2, (len(lat), len(lon)))
        wind_data[i] = np.maximum(0, wind_base + wind_noise)

    # Calculate anomalies from the 2010-2020 baseline directly in the dataset
    baseline_temp = np.mean(temp_data[:11], axis=0) # Index 0 to 10 (2010-2020)
    temp_anomaly = temp_data - baseline_temp

    # Create Dataset
    ds = xr.Dataset(
        data_vars=dict(
            temperature=(["time", "lat", "lon"], temp_data, {"units": "degC", "long_name": "Surface Temperature"}),
            temperature_anomaly=(["time", "lat", "lon"], temp_anomaly, {"units": "degC", "long_name": "Temperature Anomaly (Base 2010-2020)"}),
            precipitation=(["time", "lat", "lon"], precip_data, {"units": "mm/day", "long_name": "Precipitation Rate"}),
            wind_speed=(["time", "lat", "lon"], wind_data, {"units": "m/s", "long_name": "Wind Speed at 10m"}),
        ),
        coords=dict(
            lon=(["lon"], lon, {"units": "degrees_east", "long_name": "Longitude"}),
            lat=(["lat"], lat, {"units": "degrees_north", "long_name": "Latitude"}),
            time=time,
        ),
        attrs=dict(
            title="Premium Synthetic Climate Dataset",
            description="Generated for PyClimaExplorer Hackathon. Features simulated warming trends and ENSO events.",
            source="PyClimaExplorer Data Generator",
            project="TECHNEX 26 Hackathon"
        )
    )
    
    # Save to NetCDF
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    ds.to_netcdf(filename)
    print("Premium synthetic data generation complete!")

if __name__ == "__main__":
    generate_complex_climate_data()
