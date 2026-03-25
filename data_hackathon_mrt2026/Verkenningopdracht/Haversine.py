import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import os


base_dir = os.path.join('data_hackathon_mrt2026', 'StravaPieter', 'Alle activiteiten')
file_name = '1910046353.gpx'
file_path = os.path.join('StravaPieter', 'Alle activiteiten', '1910046353.gpx')

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

# afstand, tijd en snelheid berekenen
# verschuif rijen om de vorige coodinaten en tijd te krijgen
df['lat_prev'] = df['lat'].shift(1)
df['lon_prev'] = df['lon'].shift(1)
df['time_prev'] = df['timestamp'].shift(1)

# afstand berekenen in meters
df['delta_afstand_m'] = haversine_vector(df['lat_prev'], df['lon_prev'], df['lat'], df['lon'])
df['delta_afstand_m'] = df['delta_afstand_m'].fillna(0)

# tijd berekenen in sec
df['delta_tijd_sec'] = (df['timestamp'] - df['time_prev']).dt.total_seconds()
df['delta_tijd_sec'] = df['delta_tijd_sec'].fillna(0)

df['snelheid_m_s'] = np.where(df['delta_tijd_sec'] > 0, 
                              df['delta_afstand_m'] / df['delta_tijd_sec'], 
                              0)
df['snelheid_km_h'] = df['snelheid_m_s'] * 3.6

# tijdelijke columns verwijderen
df = df.drop(columns=['lat_prev', 'lon_prev', 'time_prev'])

# eerste 15 resultaten
print(df[['timestamp', 'delta_afstand_m', 'delta_tijd_sec', 'snelheid_km_h']].head(15))