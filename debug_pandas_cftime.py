import xarray as xr
import pandas as pd
import os

filepath = 'data/sample_climate_data.nc'
if os.path.exists(filepath):
    ds = xr.open_dataset(filepath, use_cftime=True)
    df = ds['temperature'].isel(lat=0, lon=0).to_dataframe().reset_index()
    time_vals = df['time']
    print(f"Pandas Series dtype: {time_vals.dtype}")
    print(f"Type of first element: {type(time_vals.iloc[0])}")
    
    try:
        # This is what I have in my code
        if hasattr(time_vals.dt, 'strftime'):
            print("time_vals.dt has strftime")
            try:
                print(f"Applying strftime: {time_vals.dt.strftime('%Y').iloc[0]}")
            except Exception as e:
                print(f"ERROR applying strftime: {e}")
    except Exception as e:
        print(f"ERROR checking dt: {e}")
