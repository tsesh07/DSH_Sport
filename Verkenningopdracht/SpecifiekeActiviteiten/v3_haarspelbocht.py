import pandas as pd
import numpy as np
import os
import folium
from bikeride import BikeRide


# DATA INLADEN 

script_map = os.path.dirname(os.path.abspath(__file__))
base_data_map = os.path.join(script_map, '..', '..', 'data_hackathon_mrt2026')
bestandsnaam = 'DTS_Amsterdamse_Bos_triatlon_2_3_.fit'

pad_robin = os.path.join(base_data_map, 'StravaRobin', bestandsnaam)
pad_pieter = os.path.join(base_data_map, 'StravaPieter', bestandsnaam)

if os.path.exists(pad_robin):
    file_path = pad_robin
elif os.path.exists(pad_pieter):
    file_path = pad_pieter
else:
    print(f"❌ Kan {bestandsnaam} niet vinden in de data mappen!")
    exit()

print(f"🚴‍♂️ Triatlon inladen vanuit:\n   {os.path.abspath(file_path)}...")

try:
    ride = BikeRide(os.path.abspath(file_path))
    df = pd.DataFrame(ride.records)[['timestamp', 'lat', 'lon']].dropna().reset_index(drop=True)
    print(f"✅ Route geladen met {len(df)} datapunten!")
except Exception as e:
    print(f"❌ Fout bij inladen: {e}")
    exit()

def bereken_bearing(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = np.sin(dlon) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1) * np.cos(lat2) * np.cos(dlon))
    initial_bearing = np.arctan2(x, y)
    return (np.degrees(initial_bearing) + 360) % 360

window = 15

# Richting IN en OUT
df['bearing_in'] = bereken_bearing(df['lat'].shift(window), df['lon'].shift(window), df['lat'], df['lon'])
df['bearing_out'] = bereken_bearing(df['lat'], df['lon'], df['lat'].shift(-window), df['lon'].shift(-window))

# Bereken het verschil
verschil = abs(df['bearing_out'] - df['bearing_in'])
df['richting_verschil'] = np.where(verschil > 180, 360 - verschil, verschil)

# DE BOCHT VINDEN & DEBUGGEN
max_gemeten_hoek = df['richting_verschil'].max()
print(f"🔍 Debug Info: De aller-scherpste hoek in deze dataset is {max_gemeten_hoek:.1f} graden.")

haarspeld_punten = df[df['richting_verschil'] > 130].copy()

print(f"Er zijn {len(haarspeld_punten)} GPS-punten gedetecteerd die in de haarspeldbocht liggen.")

# OP DE KAART PLOTTEN
print("Kaart genereren...")

start_lat, start_lon = df['lat'].iloc[0], df['lon'].iloc[0]
route_kaart = folium.Map(location=[start_lat, start_lon], zoom_start=14)

coordinaten = list(zip(df['lat'], df['lon']))
folium.PolyLine(coordinaten, color="blue", weight=3, opacity=0.7).add_to(route_kaart)

for index, row in haarspeld_punten.iterrows():
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=5,
        color="red",
        fill=True,
        fill_color="red",
        tooltip=f"Haarspeldbocht!"
    ).add_to(route_kaart)

html_bestand = os.path.join(script_map, "haarspeldbocht_kaart.html")
route_kaart.save(html_bestand)

print(f"Klaar! Open deze in je browser:\n   👉 {html_bestand}")