import os
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import folium
from folium import plugins

file_path = os.path.join('..', 'data_hackathon_mrt2026', 'StravaPieter', 'Alle activiteiten', '1910046353.gpx')

print(f"GPX bestand inlezen: {file_path}")

tree = ET.parse(file_path)
root = tree.getroot()
ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

data = []
for trkpt in root.findall('.//gpx:trkpt', ns):
    lat = float(trkpt.get('lat'))
    lon = float(trkpt.get('lon'))
    time_str = trkpt.find('gpx:time', ns).text
    
    ele_tag = trkpt.find('gpx:ele', ns)
    ele = float(ele_tag.text) if ele_tag is not None else 0.0
    
    data.append({'timestamp': time_str, 'lat': lat, 'lon': lon, 'elevation': ele})

df = pd.DataFrame(data)

df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

def haversine_vector(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    R = 6371000 # Straal van de aarde in meters
    return R * c

# Verschuif rijen voor vorige coördinaten/tijd
df['lat_prev'] = df['lat'].shift(1)
df['lon_prev'] = df['lon'].shift(1)
df['time_prev'] = df['timestamp'].shift(1)

# Berekeningen
df['delta_afstand_m'] = haversine_vector(df['lat_prev'], df['lon_prev'], df['lat'], df['lon']).fillna(0)
df['delta_tijd_sec'] = (df['timestamp'] - df['time_prev']).dt.total_seconds().fillna(0)

# Snelheid voorkomen delen door nul
df['snelheid_m_s'] = np.where(df['delta_tijd_sec'] > 0, df['delta_afstand_m'] / df['delta_tijd_sec'], 0)
df['snelheid_km_h'] = df['snelheid_m_s'] * 3.6

# Tijdelijke kolommen opruimen
df = df.drop(columns=['lat_prev', 'lon_prev', 'time_prev'])

df['timestamp'] = df['timestamp'].dt.tz_convert('Europe/Amsterdam')

max_snelheid_kmh = 25.0 
aantal_voor = len(df)

df_clean = df[df['snelheid_km_h'] <= max_snelheid_kmh].copy()
df_clean = df_clean.reset_index(drop=True)

aantal_na = len(df_clean)

print(f"\n Data succesvol opgeschoond!")
print(f"   Verwijderde GPS-fouten (outliers): {aantal_voor - aantal_na} rijen")
print(f"   Bruikbare datapunten over: {aantal_na}\n")


print("🗺️ Kaart genereren...")

coordinaten = list(zip(df_clean['lat'], df_clean['lon']))

start_lat, start_lon = coordinaten[0]
route_kaart = folium.Map(location=[start_lat, start_lon], zoom_start=15)

plugins.AntPath(
    locations=coordinaten,
    color="blue",
    weight=5,
    tooltip="Gevolgde Route"
).add_to(route_kaart)

folium.Marker(coordinaten[0], tooltip="Start", icon=folium.Icon(color="green", icon="play")).add_to(route_kaart)
folium.Marker(coordinaten[-1], tooltip="Finish", icon=folium.Icon(color="red", icon="stop")).add_to(route_kaart)

script_map = os.path.dirname(os.path.abspath(__file__))
html_bestand = os.path.join(script_map, "route_kaart.html")
route_kaart.save(html_bestand)
print(f"Succes! De kaart is opgeslagen op deze locatie:\n   👉 {html_bestand}")