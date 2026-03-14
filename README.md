# 🌍 PyClimaExplorer

**Scientific Intelligence Platform for Rapid Climate Data Visualization**

PyClimaExplorer is a premium, interactive web application designed for researchers and the general public to explore complex climate datasets (CESM, ERA5, CMIP6) with ease. Built for the **TECHNEX '26 Hackathon**.

## 🚀 Key Features

- **Scientific Command Center**: 9 dynamic ECharts providing multi-dimensional insights (Zonal, Meridional, Statistical, Radar, Heatmap).
- **NetCDF File Port**: Upload and analyze your own `.nc` files in real-time.
- **3D Topographical Globe**: Visualize climate intensity mapped to Earth's elevation.
- **Story Mode**: Interactive narrative walkthroughs of global climate anomalies.
- **Orbital Data Acquisition**: Direct integration with ECMWF ERA5 via the Copernicus CDS API.
- **Real-World Engine**: Robust support for Dask (large files) and `cftime` (non-standard climate calendars).


## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Py-Climax
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Sample Data:**
   ```bash
   python generate_data.py
   ```

## 🖥️ Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

- **Sidebar**: Toggle metrics (Temperature, Precipitation, etc.) and drag the temporal axis.
- **Upload**: Drop your own `.nc` files into the sidebar uploader for instant analysis.
- **Tabs**: Switch between Spatial Heatmaps, Time Series, 3D Globe, and Story Mode.

## 📄 Documentation

- [Walkthrough](.gemini/antigravity/brain/1e0028f5-d702-4d8d-a85f-cda729901da7/walkthrough.md): Detailed explanation of features and implementation.
- [Implementation Plan](.gemini/antigravity/brain/1e0028f5-d702-4d8d-a85f-cda729901da7/implementation_plan.md): Technical roadmap and architecture details.

---
*Built with ❤️ for TECHNEX '26*
