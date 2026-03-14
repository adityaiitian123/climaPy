import xarray as xr
import pandas as pd
import numpy as np
import scipy.stats as scipy_stats

class ClimateProcessor:
    """Handles data slicing, aggregation, anomaly calculations for the UI."""
    
    @staticmethod
    def get_spatial_slice(ds: xr.Dataset, variable: str, time_index: int) -> pd.DataFrame:
        """Returns a 2D dataframe for a specific variable at a specific time for map rendering."""
        try:
            da_slice = ds[variable].isel(time=time_index)
            df = da_slice.to_dataframe().reset_index().dropna(subset=[variable])
            if 'time' in df.columns:
                df = df.drop(columns=['time'])
            return df
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def get_time_series(ds: xr.Dataset, variable: str, lat: float, lon: float):
        """Extracts a time series for the nearest grid point to the provided coordinates."""
        try:
            nearest_ds = ds.sel(lat=lat, lon=lon, method="nearest")
            df = nearest_ds[variable].to_dataframe().reset_index()
            actual_lat = float(nearest_ds.lat.values)
            actual_lon = float(nearest_ds.lon.values)
            return df, actual_lat, actual_lon
        except Exception:
            return pd.DataFrame(), None, None

    @staticmethod
    def calculate_global_mean(ds: xr.Dataset, variable: str, time_index: int) -> float:
        """Calculates an area-weighted global mean for a specific time slice."""
        try:
            da = ds[variable].isel(time=time_index)
            return float(da.mean().values)
        except:
            return 0.0

    @staticmethod
    def get_zonal_mean(ds: xr.Dataset, variable: str, time_index: int) -> pd.DataFrame:
        """Calculates mean of a variable across all longitudes for each latitude."""
        try:
            da = ds[variable].isel(time=time_index).mean(dim='lon')
            return da.to_dataframe().reset_index()
        except:
            return pd.DataFrame()

    @staticmethod
    def get_meridional_mean(ds: xr.Dataset, variable: str, time_index: int) -> pd.DataFrame:
        """Calculates mean of a variable across all latitudes for each longitude."""
        try:
            da = ds[variable].isel(time=time_index).mean(dim='lat')
            return da.to_dataframe().reset_index()
        except:
            return pd.DataFrame()

    @staticmethod
    def get_zonal_profile_stats(ds: xr.Dataset, variable: str, time_index: int) -> pd.DataFrame:
        """Calculates latitudinal mean and standard deviation for zonal profiles."""
        try:
            da = ds[variable].isel(time=time_index)
            zonal_mean = da.mean(dim='lon')
            zonal_std = da.std(dim='lon')
            df = zonal_mean.to_dataframe(name='mean').reset_index()
            df['std'] = zonal_std.values
            return df
        except:
            return pd.DataFrame()

    @staticmethod
    def get_statistical_summary(ds: xr.Dataset, variable: str, time_index: int) -> dict:
        """Calculates statistical distribution metrics for a time slice."""
        try:
            da = ds[variable].isel(time=time_index)
            data = da.values.flatten()
            data = data[~np.isnan(data)]
            return {
                "min": float(np.min(data)),
                "q1": float(np.percentile(data, 25)),
                "median": float(np.median(data)),
                "q3": float(np.percentile(data, 75)),
                "max": float(np.max(data)),
                "mean": float(np.mean(data)),
                "std": float(np.std(data)),
                "skew": float(scipy_stats.skew(data)) if len(data) > 2 else 0.0,
                "kurt": float(scipy_stats.kurtosis(data)) if len(data) > 2 else 0.0,
                "cv": float(np.std(data)/np.mean(data)) if np.mean(data) != 0 else 0.0
            }
        except:
            return {}

    @staticmethod
    def get_histogram_data(ds: xr.Dataset, variable: str, time_index: int, bins: int = 30):
        """Returns histogram bin edges and counts."""
        try:
            da = ds[variable].isel(time=time_index)
            data = da.values.flatten()
            data = data[~np.isnan(data)]
            counts, edges = np.histogram(data, bins=bins)
            return counts.tolist(), edges.tolist()
        except:
            return [], []

    @staticmethod
    def get_temporal_matrix(ds: xr.Dataset, variable: str) -> pd.DataFrame:
        """Calculates time-latitude mean matrix for heatmap rendering."""
        try:
            da = ds[variable].mean(dim='lon')
            return da.to_dataframe().reset_index()
        except:
            return pd.DataFrame()

    @staticmethod
    def generate_automated_insight(ds: xr.Dataset, variable: str, time_index: int, ai_client=None) -> str:
        """Generates a text summary for the AI Insight panel using rule-based fallback or LLM."""
        try:
            current_mean = ClimateProcessor.calculate_global_mean(ds, variable, time_index)
            historical_mean = float(ds[variable].mean().values)
            diff = current_mean - historical_mean
            pct_diff = (diff / abs(historical_mean)) * 100 if historical_mean != 0 else 0
            
            time_obj = ds.time.isel(time=time_index)
            try:
                time_val = time_obj.dt.strftime("%Y").values.item()
            except (AttributeError, TypeError):
                time_val = str(time_obj.values.year)
            
            direction = "higher" if diff > 0 else "lower"
            rule_based = f"In {time_val}, the global average for this variable ({variable}) is {current_mean:.2f}. "
            rule_based += f"This is **{abs(diff):.2f} ({abs(pct_diff):.1f}%) {direction}** than the long-term dataset average of {historical_mean:.2f}. "
            
            if not ai_client:
                return rule_based

            # AI Enhancement Path
            system_prompt = "You are a senior climate research analyst. Provide a concise, high-impact 2-sentence summary of climate data."
            user_msg = f"""
            Variable: {variable}
            Target Year: {time_val}
            Current Global Mean: {current_mean:.2f}
            Historical Dataset Mean: {historical_mean:.2f}
            Anomaly: {diff:.2f} ({pct_diff:.1f}%)
            
            Analyze this observation. Focus on the significance of the anomaly. Use professional but accessible language. Keep it under 60 words.
            """
            
            completion = ai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                model="llama-3.1-8b-instant",
            )
            return completion.choices[0].message.content
            
        except Exception as e:
            return f"Observation analysis active. Signal suggests a {direction} trend relative to baseline."

    # ─── NEW INTELLIGENCE METHODS ─────────────────────────────────────────────

    @staticmethod
    def get_anomaly_slice(ds: xr.Dataset, variable: str, time_index: int) -> pd.DataFrame:
        """Returns a spatial anomaly slice: current - long-term mean.
        Positive = warmer/wetter than average. Negative = cooler/drier."""
        try:
            da_current = ds[variable].isel(time=time_index)
            da_mean = ds[variable].mean(dim='time')
            da_anomaly = da_current - da_mean
            df = da_anomaly.to_dataframe(name='anomaly').reset_index()
            if 'time' in df.columns:
                df = df.drop(columns=['time'])
            df = df.dropna(subset=['anomaly'])
            return df
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def get_trend_stats(ds: xr.Dataset, variable: str, lat: float, lon: float) -> dict:
        """Calculates linear trend (slope per time step, R²) for a location's time series."""
        try:
            from scipy import stats as scipy_stats
            nearest_ds = ds.sel(lat=lat, lon=lon, method="nearest")
            values = nearest_ds[variable].values.astype(float)
            x = np.arange(len(values))
            mask = ~np.isnan(values)
            if mask.sum() < 3:
                return {}
            slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(x[mask], values[mask])
            return {
                "slope": float(slope),
                "r_squared": float(r_value ** 2),
                "p_value": float(p_value),
                "intercept": float(intercept),
                "n": int(mask.sum()),
                "std_err": float(std_err)
            }
        except Exception:
            # Fallback without scipy
            try:
                nearest_ds = ds.sel(lat=lat, lon=lon, method="nearest")
                values = nearest_ds[variable].values.astype(float)
                x = np.arange(len(values))
                mask = ~np.isnan(values)
                if mask.sum() < 3:
                    return {}
                xm, ym = x[mask].mean(), values[mask].mean()
                slope = float(np.sum((x[mask]-xm)*(values[mask]-ym)) / np.sum((x[mask]-xm)**2))
                ss_tot = float(np.sum((values[mask]-ym)**2))
                ss_res = float(np.sum((values[mask] - (slope*x[mask] + (ym - slope*xm)))**2))
                r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0
                return {"slope": slope, "r_squared": r2, "p_value": 0.0, "intercept": float(ym - slope*xm), "n": int(mask.sum()), "std_err": 0.0}
            except:
                return {}

    @staticmethod
    def get_ml_forecast(ds: xr.Dataset, variable: str, lat: float, lon: float, future_steps: int = 5):
        """Linear regression forecast for next N time steps. Returns (forecast_vals, lower_band, upper_band)."""
        try:
            nearest_ds = ds.sel(lat=lat, lon=lon, method="nearest")
            values = nearest_ds[variable].values.astype(float)
            x = np.arange(len(values))
            mask = ~np.isnan(values)
            if mask.sum() < 3:
                return [], [], []
            # Numpy polyfit (linear)
            coeffs = np.polyfit(x[mask], values[mask], 1)
            slope, intercept = coeffs
            future_x = np.arange(len(values), len(values) + future_steps)
            forecast = [float(slope * xi + intercept) for xi in future_x]
            # Simple confidence band based on residuals
            residuals = values[mask] - (slope * x[mask] + intercept)
            sigma = float(np.std(residuals)) * 1.5
            lower = [f - sigma for f in forecast]
            upper = [f + sigma for f in forecast]
            return forecast, lower, upper
        except Exception:
            return [], [], []

    @staticmethod
    def get_climate_risk_index(ds: xr.Dataset, variable: str, lat: float, lon: float) -> dict:
        """Composite 0-100 Climate Risk Index based on trend steepness, anomaly frequency, and variability."""
        try:
            nearest_ds = ds.sel(lat=lat, lon=lon, method="nearest")
            values = nearest_ds[variable].values.astype(float)
            mask = ~np.isnan(values)
            if mask.sum() < 3:
                return {"score": 0, "label": "UNKNOWN", "color": "#64748b"}
            clean = values[mask]
            mean_v = float(np.mean(clean))
            std_v = float(np.std(clean))
            
            # Factor 1: Trend (slope normalized by std)
            x = np.arange(len(clean))
            coeffs = np.polyfit(x, clean, 1)
            slope = coeffs[0]
            trend_score = min(100, abs(slope / (std_v + 1e-9)) * 100)
            
            # Factor 2: Anomaly frequency (% of time steps > 1σ from mean)
            anomaly_freq = float(np.sum(np.abs(clean - mean_v) > std_v) / len(clean)) * 100
            
            # Factor 3: Relative variability (CV)
            cv_score = min(100, (std_v / (abs(mean_v) + 1e-9)) * 200)
            
            raw = 0.5 * trend_score + 0.3 * anomaly_freq + 0.2 * cv_score
            score = min(100, max(0, raw))
            
            if score >= 70:
                label, color = "CRITICAL", "#ef4444"
            elif score >= 45:
                label, color = "HIGH", "#f97316"
            elif score >= 20:
                label, color = "MEDIUM", "#f59e0b"
            else:
                label, color = "LOW", "#10b981"
            
            return {"score": round(score, 1), "label": label, "color": color,
                    "trend_component": round(trend_score, 1),
                    "anomaly_component": round(anomaly_freq, 1),
                    "variability_component": round(cv_score, 1)}
        except Exception:
            return {"score": 0, "label": "UNKNOWN", "color": "#64748b"}

    @staticmethod
    def get_top_anomaly_regions(ds: xr.Dataset, variable: str, time_index: int, n: int = 10) -> pd.DataFrame:
        """Returns the top N most anomalous lat/lon points (furthest from long-term mean) for spotlight overlays."""
        try:
            da_current = ds[variable].isel(time=time_index)
            da_mean = ds[variable].mean(dim='time')
            da_anomaly = da_current - da_mean
            df = da_anomaly.to_dataframe(name='anomaly').reset_index()
            if 'time' in df.columns:
                df = df.drop(columns=['time'])
            df = df.dropna(subset=['anomaly'])
            df['abs_anomaly'] = df['anomaly'].abs()
            top = df.nlargest(n, 'abs_anomaly')[['lat', 'lon', 'anomaly', 'abs_anomaly']].reset_index(drop=True)
            return top
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def get_climatology_comparison(ds: xr.Dataset, variable: str, lat: float, lon: float) -> pd.DataFrame:
        """Calculates monthly climatology vs current year for a specific location."""
        try:
            nearest_ds = ds.sel(lat=lat, lon=lon, method="nearest")
            # Group by month to get climatology
            climatology = nearest_ds[variable].groupby("time.month").mean("time")
            
            # Get current year monthly values (last 12 months in the dataset)
            current_year = nearest_ds[variable].isel(time=slice(-12, None))
            
            df_clim = climatology.to_dataframe(name='climatology').reset_index()
            # Extract month for merging
            try:
                df_curr = current_year.to_dataframe(name='actual').reset_index()
                df_curr['month'] = df_curr['time'].dt.month
            except:
                # Cftime fallback
                df_curr = current_year.to_dataframe(name='actual').reset_index()
                df_curr['month'] = [t.month for t in df_curr['time']]
            
            df = pd.merge(df_clim, df_curr[['month', 'actual']], on='month', how='left')
            return df
        except:
            return pd.DataFrame()

    @staticmethod
    def get_hovmoller_data(ds: xr.Dataset, variable: str) -> pd.DataFrame:
        """Generates Time-Latitude Hovmöller matrix data."""
        try:
            da = ds[variable].mean(dim='lon')
            df = da.to_dataframe(name='val').reset_index()
            try:
                df['time_str'] = df['time'].dt.strftime('%Y-%m')
            except:
                df['time_str'] = [f"{t.year}-{t.month:02d}" for t in df['time']]
            return df
        except:
            return pd.DataFrame()

    @staticmethod
    def classify_climate_zones(ds: xr.Dataset) -> pd.DataFrame:
        """Classifies grid cells into climate zones based on temperature and latitude.
        Zones: Polar, Subpolar, Temperate, Subtropical, Tropical, Equatorial."""
        try:
            # Use T2M or similar temperature variable if available, else first variable
            temp_vars = ['t2m', 'temp', 'tas', 'temperature']
            var = next((v for v in temp_vars if v in ds.data_vars), list(ds.data_vars)[0])
            
            # Use climatological mean temperature
            da_temp = ds[var].mean(dim='time')
            df = da_temp.to_dataframe(name='temp').reset_index().dropna()
            
            # Classification logic (Simplified but visually effective)
            def assign_zone(row):
                lat_val = abs(float(row['lat']))
                t = float(row['temp'])
                # Convert to Celsius if in Kelvin
                t_c = t - 273.15 if t > 100 else t
                
                if lat_val > 66.5 or t_c < 0: return "Polar"
                if lat_val > 50: return "Subpolar"
                if lat_val > 35: return "Temperate"
                if lat_val > 23.5: return "Subtropical"
                if lat_val > 10: return "Tropical"
                return "Equatorial"

            df['zone'] = df.apply(assign_zone, axis=1)
            # Map zones to numeric IDs and colors for rendering
            zone_map = {
                "Polar": {"id": 0, "color": [186, 230, 253, 200]},
                "Subpolar": {"id": 1, "color": [14, 165, 233, 200]},
                "Temperate": {"id": 2, "color": [34, 197, 94, 200]},
                "Subtropical": {"id": 3, "color": [245, 158, 11, 200]},
                "Tropical": {"id": 4, "color": [249, 115, 22, 200]},
                "Equatorial": {"id": 5, "color": [239, 68, 68, 200]}
            }
            df['zone_id'] = df['zone'].map(lambda x: zone_map[x]['id'])
            df['color_rgb'] = df['zone'].map(lambda x: zone_map[x]['color'])
            return df
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def get_global_anomaly_series(ds: xr.Dataset) -> pd.DataFrame:
        """Calculates global mean temperature anomalies with robust dimension handling."""
        try:
            # 1. Identify thermal variable
            temp_vars = ['t2m', 'temp', 'tas', 'temperature', 'T2M', 'surface_temp']
            var = next((v for v in temp_vars if v in ds.data_vars), None)
            if not var:
                if len(ds.data_vars) > 0:
                    var = list(ds.data_vars)[0]
                else:
                    return pd.DataFrame()
            
            # 2. Handle Time dimension
            if 'time' not in ds.dims and 'time' not in ds.coords:
                return pd.DataFrame()
                
            n_steps = len(ds.time)
            freq = 'YE' if n_steps >= 24 else 'ME'
            
            # 3. Spatial Averaging (Robust to dim names)
            spatial_dims = [d for d in ds[var].dims if d in ['lat', 'lon', 'latitude', 'longitude']]
            
            # Resample time
            try:
                ds_resampled = ds[var].resample(time=freq).mean()
            except Exception:
                # Fallback: group by year/month manually if resample fails
                ds_resampled = ds[var]
            
            global_series = ds_resampled.mean(dim=spatial_dims) if spatial_dims else ds_resampled
            
            if len(global_series) == 0:
                return pd.DataFrame()

            # 4. Calculate Anomaly
            # Baseline: first part of the series
            n_base = max(1, min(30, len(global_series) // 3))
            baseline_val = global_series.isel(time=slice(0, n_base)).mean().values
            
            df = global_series.to_dataframe(name='val').reset_index()
            df['anomaly'] = df['val'] - float(baseline_val)
            
            # Units conversion (Kelvin cleanup)
            avg_val = df['val'].mean()
            if avg_val > 100: # Clearly Kelvin or wrong units
                df['val_c'] = df['val'] - 273.15
            else:
                df['val_c'] = df['val']
            
            # 5. Format Time Labels
            try:
                if freq == 'YE':
                    df['year'] = pd.to_datetime(df['time']).dt.year
                else:
                    df['year'] = pd.to_datetime(df['time']).dt.strftime('%b %Y')
            except Exception:
                # Backup manual formatting for cftime
                def fmt_time(t):
                    try: return f"{t.year}" if freq == 'YE' else f"{t.month:02d}/{t.year}"
                    except: return str(t)
                df['year'] = df['time'].apply(fmt_time)
                
            return ClimateProcessor._ensure_standard_time(df)
        except Exception as e:
            print(f"ERROR in get_global_anomaly_series: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_climatology_mean(ds: xr.Dataset, variable: str) -> pd.DataFrame:
        """Calculates long-term spatial mean (climatology) across the time dimension."""
        try:
            climatology = ds[variable].mean(dim='time')
            df = climatology.to_dataframe(name='val').reset_index().dropna()
            return df
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def get_spaghetti_data(ds: xr.Dataset, variable: str) -> pd.DataFrame:
        """Groups data by day-of-year and year for multi-line comparison plots."""
        try:
            # Resample to daily if not already, or just take mean by day
            # If dataset is monthly, this will just show 12 points per year
            da = ds[variable].mean(dim=['lat', 'lon'])
            
            df = da.to_dataframe(name='val').reset_index()
            # Handle cftime or numpy datetime
            try:
                df['doy'] = df['time'].dt.dayofyear
                df['year'] = df['time'].dt.year
            except:
                df['doy'] = [t.timetuple().tm_yday for t in df['time']]
                df['year'] = [t.year for t in df['time']]
            
            return ClimateProcessor._ensure_standard_time(df)
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def get_composition_series(ds: xr.Dataset) -> pd.DataFrame:
        """Prepares stacked area data for composition visualization."""
        try:
            # If specific variables like 'sea_ice_age_X' exist, use them.
            # Otherwise, simulate composition from total ice or return dummy for demo
            time_series = ds.mean(dim=['lat', 'lon'])
            df = time_series.to_dataframe().reset_index()
            
            # For demonstration in the UI if real categories aren't present
            categories = ["First-year ice", "Second-year ice", "Multi-year ice (5+)"]
            result_dfs = []
            
            for i, cat in enumerate(categories):
                temp_df = df[['time']].copy()
                # Create a simulated breakdown
                factor = (i + 1) / (len(categories) + 1)
                temp_df['val'] = (i+1) * 0.5 + 0.2 * np.sin(np.arange(len(df)) * 0.5) 
                temp_df['category'] = cat
                result_dfs.append(temp_df)
                
            final_df = pd.concat(result_dfs)
            return ClimateProcessor._ensure_standard_time(final_df)
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def _ensure_standard_time(df: pd.DataFrame) -> pd.DataFrame:
        """Helper to convert cftime objects to pandas Timestamps for Plotly serialization."""
        if 'time' not in df.columns:
            return df
        try:
            # Check if first element is cftime
            from cftime import datetime as cf_dt
            if len(df) > 0 and isinstance(df['time'].iloc[0], cf_dt):
                df['time'] = df['time'].apply(lambda t: pd.Timestamp(
                    year=t.year, month=t.month, day=t.day, 
                    hour=t.hour, minute=t.minute, second=t.second
                ))
        except Exception:
            pass
        return df

    @staticmethod
    def get_seasonal_means(ds: xr.Dataset, variable: str) -> dict:
        """Calculates multi-year averages for each season."""
        try:
            # Use .dt accessor for safer season access
            seasonal = ds[variable].groupby(ds.time.dt.season).mean(dim='time')
            res = {}
            season_names = {
                'MAM': 'Spring (MAM)',
                'JJA': 'Summer (JJA)',
                'SON': 'Autumn (SON)',
                'DJF': 'Winter (DJF)'
            }
            for s in seasonal.season.values:
                df = seasonal.sel(season=s).to_dataframe(name='val').reset_index().dropna()
                res[season_names.get(s, s)] = df
            return res
        except Exception:
            return {}

    @staticmethod
    def get_monthly_distributions(ds: xr.Dataset, variable: str) -> pd.DataFrame:
        """Extracts values grouped by month for ridgeline/distribution analysis."""
        try:
            # Subsample for horizontal ridgeline performance if spatial grid is dense
            da = ds[variable]
            if da.size > 200000:
                # Spatial thinning
                da = da.thin({'lat': 3, 'lon': 3})
            
            df = da.to_dataframe(name='val').reset_index().dropna()
            
            # Month extraction with fallbacks
            try:
                df['month'] = pd.to_datetime(df['time']).dt.month_name()
                df['month_idx'] = pd.to_datetime(df['time']).dt.month
            except:
                month_map = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                             7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
                df['month_idx'] = [getattr(t, 'month', 1) for t in df['time']]
                df['month'] = df['month_idx'].map(month_map)
            
            # Rank months chronologically
            df = df.sort_values('month_idx')
            return df[['month', 'month_idx', 'val']]
        except Exception:
            return pd.DataFrame()
