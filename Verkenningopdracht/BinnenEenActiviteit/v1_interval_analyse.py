import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import os

# Data 'stravapieter - interval 12x_200m.gpx inladen

script_map = os.path.dirname(os.path.abspath(__file__))
# Let op: de opdracht zegt dat hij in StravaPieter staat!
file_path = os.path.join(script_map, '..', '..', 'data_hackathon_mrt2026', 'StravaPieter', 'interval_12x_200m.gpx')
file_path = os.path.abspath(file_path)

# Doorzoek de namespaces
data = []
try:
    tree = ET.parse(file_path)
    root = tree.getroot()
    for trkpt in root.iter():
        if trkpt.tag.endswith('trkpt'):
            lat = float(trkpt.attrib['lat'])
            lon = float(trkpt.attrib['lon'])
            tijd = None
            for child in trkpt:
                if child.tag.endswith('time'):
                    tijd = child.text
            if tijd:
                data.append({'timestamp': tijd, 'lat': lat, 'lon': lon})
except Exception as e:
    print(f"Fout bij inladen GPX: {e}")
    exit()

df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

# Afstand & snelheid (Haversine) berekenen

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 # Aardstraal in meters
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1-a))

# Verschil berekenen met vorige punt
df['lat_vorige'] = df['lat'].shift(1)
df['lon_vorige'] = df['lon'].shift(1)
df['tijd_vorige'] = df['timestamp'].shift(1)

# Afstand in meters per punt
df['delta_meters'] = haversine(df['lat'], df['lon'], df['lat_vorige'], df['lon_vorige'])

# Tijd in seconden per punt
df['delta_seconden'] = (df['timestamp'] - df['tijd_vorige']).dt.total_seconds()

# Snelheid (km/u) = (meters / seconden) * 3.6
df['snelheid_kmu'] = (df['delta_meters'] / df['delta_seconden']) * 3.6

# Lijn vloeiender maken met een rolling average van 10 sec
df['snelheid_vloeiend'] = df['snelheid_kmu'].rolling(window=10, center=True).mean()

# Visualisatie van de intervallen
plt.figure(figsize=(14, 6))

# Plot de vloeiende snelheid
plt.plot(df['timestamp'], df['snelheid_vloeiend'], color='royalblue', linewidth=2, label='Snelheid (km/u)')

# de gemiddelde snelheid als referentie
gemiddelde = df['snelheid_vloeiend'].mean()
plt.axhline(y=gemiddelde, color='red', linestyle='--', alpha=0.5, label=f'Gemiddelde ({gemiddelde:.1f} km/u)')

plt.title('Snelheidsprofiel: Zoek de Intervallen.', fontsize=14, fontweight='bold')
plt.xlabel('Tijd', fontsize=12)
plt.ylabel('Snelheid (km/u)', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plot_bestand = os.path.join(script_map, "interval_plot.png")
plt.savefig(plot_bestand)
print(f"Grafiek opgeslagen: {plot_bestand}")
plt.show()

# Automatisch herkennen van het interval schema
print("\n🔍 Automatische patroonherkenning starten...")

# Drempelwaarde bepalen: 13km/u
drempel_kmu = 13.0
df['is_sprint'] = df['snelheid_vloeiend'] > drempel_kmu

# Telkens als 'is_sprint' wisselt van True naar False, gaat het groep-ID +1
df['interval_id'] = (df['is_sprint'] != df['is_sprint'].shift()).cumsum()

# Filter alleen de sprint-blokken eruit
alleen_sprints = df[df['is_sprint'] == True]

gedetecteerde_intervallen = []

# Reken per blokje de afstand uit
for blok_id, data in alleen_sprints.groupby('interval_id'):
    totale_afstand = data['delta_meters'].sum()
    
    # Ruis filteren
    if totale_afstand > 50: 
        gedetecteerde_intervallen.append(totale_afstand)

# Conclusie
aantal_herhalingen = len(gedetecteerde_intervallen)
gemiddelde_afstand = np.mean(gedetecteerde_intervallen)

# afronden van getallen
afgeronde_afstand = round(gemiddelde_afstand / 100) * 100

print("="*50)
print(f"ALGORITME CONCLUSIE:")
print(f"Aantal sprints gedetecteerd: {aantal_herhalingen}")
print(f"Gemiddelde afstand per sprint: {gemiddelde_afstand:.1f} meter")
print(f"\n Herkend Schema: {aantal_herhalingen}x {afgeronde_afstand}m")
print("="*50)