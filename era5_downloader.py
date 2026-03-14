import cdsapi
import os
from typing import Dict, List, Optional

# New CDS API v3 endpoint (ECMWF migrated in 2024)
CDS_URL = 'https://cds.climate.copernicus.eu/api'

class ERA5Downloader:
    """Interface for retrieving ERA5 reanalysis data from Copernicus Climate Data Store (CDS)."""

    def __init__(self, api_key: Optional[str] = None, url: Optional[str] = None):
        """
        Initializes the CDS client using the new API v3 format (key-only, no UID needed).
        
        Args:
            api_key: Personal API Key from your CDS profile.
            url: CDS API endpoint. Defaults to the v3 endpoint.
        """
        self.url = url or os.environ.get('CDS_URL', CDS_URL)
        self.api_key = api_key or os.environ.get('CDS_API_KEY')

        if self.api_key:
            self.client = cdsapi.Client(url=self.url, key=self.api_key, quiet=True)
        else:
            # Fallback to local .cdsapirc
            try:
                self.client = cdsapi.Client(quiet=True)
            except Exception:
                self.client = None


    def download_request(self, dataset: str, request: Dict, output_path: str) -> str:
        """
        Submits a download request to CDS.
        
        Args:
            dataset: The dataset identifier (e.g., 'reanalysis-era5-single-levels')
            request: Dictionary of parameters (variables, dates, area, etc.)
            output_path: Path where the resulting .nc file will be saved.
            
        Returns:
            The path to the downloaded file.
        """
        if not self.client:
            raise RuntimeError("CDS Client not initialized. API credentials required.")

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if os.path.exists(output_path):
            return output_path

        self.client.retrieve(dataset, request, output_path)
        return output_path

    @staticmethod
    def create_request_dict(
        variable: List[str],
        years: List[str],
        months: List[str],
        days: List[str],
        times: List[str],
        area: Optional[List[float]] = None,
        product_format: str = 'netcdf'
    ) -> dict:
        """
        Helper to construct the request dictionary for CDS.
        
        Args:
            variable: List of variable names (e.g., ['2m_temperature'])
            years: List of years as strings
            months: List of months ('01' to '12')
            days: List of days ('01' to '31')
            times: List of times ('00:00' to '23:00')
            area: [North, West, South, East] in degrees.
            product_format: 'netcdf' or 'grib'
        """
        req: dict = {
            'product_type': 'reanalysis',
            'format': product_format,
            'variable': variable,
            'year': years,
            'month': months,
            'day': days,
            'time': times,
        }
        
        if area:
            req['area'] = area  # [North, West, South, East]
            
        return req
