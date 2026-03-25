import pandas as pd
import os
from bikeride import BikeRide

file_path = os.path.join('..', '..', 'data_hackathon_mrt2026', 'StravaRobin', 'Van_Luik_naar_Bastenaken_en_weer_terug_naar_Luik_.fit')

print(f"Data inladen van de data...")
print("Een moment geduld...")

try:
    ride = BikeRide(file_path)
    df = pd.DataFrame(ride.records)
except Exception as e:
    print(f"Fout bij inladen: {e}")
    exit()

# Filter alleen de kolommen die nodig zijn en gooi lege rijen weg
if 'enhanced_altitude' not in df.columns:
    print("Fout: Kolom 'enhanced_altitude' niet gevonden in dit bestand.")
    exit()

df = df[['timestamp', 'enhanced_altitude']].dropna().copy()
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

print(f"Data ingeladen! ({len(df)} datapunten)")

df['hoogte_verschil'] = df['enhanced_altitude'].diff()
stijgingen = df[df['hoogte_verschil'] > 0]['hoogte_verschil']
totale_hoogtemeters = stijgingen.sum()


print("\n" + "="*40)
print(f"Resultaat Luik-Bastenaken-Luik")
print("="*40)
print(f"Totale stijging (hoogtemeters): {totale_hoogtemeters:.1f} meter")
print("="*40 + "\n")