import xarray as xr
import os

filepath = 'data/sample_climate_data.nc'
if os.path.exists(filepath):
    print(f"Loading {filepath}...")
    try:
        ds = xr.open_dataset(filepath, chunks='auto', use_cftime=True)
        print(f"Time dtype: {ds.time.dtype}")
        print(f"Time example: {ds.time.values[0]}")
        try:
            print(f"Accessing .dt: {ds.time.dt}")
            print(f"Year from .dt: {ds.time.dt.year.values[0]}")
        except Exception as dt_err:
            print(f"ERROR accessing .dt: {dt_err}")
    except Exception as e:
        print(f"ERROR loading: {e}")
else:
    print("File not found.")
