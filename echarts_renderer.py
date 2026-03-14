"""
echarts_renderer.py
Renders Apache ECharts charts inside Streamlit using st.components.v1.html.
No extra packages required — ECharts is loaded from the CDN.
"""
import json
import streamlit.components.v1 as components

ECHARTS_CDN = "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"
ECHARTS_WORLD_MAP = "https://cdn.jsdelivr.net/npm/echarts@4.9.0/map/js/world.js"
ECHARTS_GL_CDN = "https://cdn.jsdelivr.net/npm/echarts-gl@2.0.9/dist/echarts-gl.min.js"

import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def render_echarts(option: dict, height: int = 400, key: str = "chart", use_map: bool = False, use_gl: bool = False):
    """
    Renders an ECharts chart from a Python dict option spec.
    `option` must be JSON-serializable (no JS functions).
    Include `use_map=True` to load the world map projection data.
    Include `use_gl=True` to load ECharts-GL for 3D charts.
    """
    option_json = json.dumps(option, ensure_ascii=False, cls=NpEncoder)
    
    map_script = f'<script src="{ECHARTS_WORLD_MAP}"></script>' if use_map else ""
    gl_script = f'<script src="{ECHARTS_GL_CDN}"></script>' if use_gl else ""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8"/>
      <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ background: transparent; overflow: hidden; }}
        #chart {{ width: 100%; height: {height}px; }}
      </style>
    </head>
    <body>
      <div id="chart"></div>
      <script src="{ECHARTS_CDN}"></script>
      {map_script}
      {gl_script}
      <script>
        var chart = echarts.init(document.getElementById('chart'), null, {{
          renderer: 'canvas',
          useDirtyRect: false
        }});
        var option = {option_json};
        chart.setOption(option);
        window.addEventListener('resize', function() {{ chart.resize(); }});
      </script>
    </body>
    </html>
    """
    components.html(html, height=height + 10, scrolling=False)
