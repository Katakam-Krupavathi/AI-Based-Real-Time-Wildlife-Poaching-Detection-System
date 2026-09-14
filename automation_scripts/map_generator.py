# map_generator.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config

def generate_map(lat, lon, output_path=None):
    """
    Generates a Folium interactive map centered on the threat coordinates.
    """
    if output_path is None:
        output_path = os.path.join(config.PROJECT_ROOT, "latest_alert_map.html")

    try:
        import folium
        lat = float(lat)
        lon = float(lon)

        m = folium.Map(location=[lat, lon], zoom_start=16)
        folium.Marker(
            [lat, lon],
            popup=f"Poaching Threat Detected ({lat:.4f}, {lon:.4f})",
            icon=folium.Icon(color='red', icon='warning', prefix='fa')
        ).add_to(m)

        m.save(output_path)
        return output_path
    except Exception as e:
        print(f"Warning: Map generation skipped: {e}")
        return None