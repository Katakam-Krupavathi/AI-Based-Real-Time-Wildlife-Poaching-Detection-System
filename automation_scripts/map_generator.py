# map_generator.py

import folium

def generate_map(lat, lon):

    lat = float(lat)
    lon = float(lon)

    m = folium.Map(location=[lat, lon], zoom_start=16)

    folium.Marker(
        [lat, lon],
        popup="Threat Location",
        icon=folium.Icon(color='red')
    ).add_to(m)

    m.save("latest_alert_map.html")