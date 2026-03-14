import xarray as xr
import sys

try:
    ds = xr.open_dataset('c:/Users/ASUS/OneDrive/Desktop/Py-Climax/data/nasa_merra2_proof_new.nc')
    print(f"Dataset Title: {ds.attrs.get('title', 'No Title')}")
    print(f"Time dim: {ds.time.size}")
    print(f"Data vars: {list(ds.data_vars)}")
    if 'time' in ds.coords:
        print(f"Time Range: {ds.time.values[0]} to {ds.time.values[-1]}")
    ds.close()
except Exception as e:
    print(f"Error: {e}")
