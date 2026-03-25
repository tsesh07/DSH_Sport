import os
import glob
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

# --- 1. Vind alle GPX bestanden ---
# Let op de '..' aan het begin: we gaan vanuit Verkenningopdracht één map omhoog
folder_path = os.path.join('..', 'data_hackathon_mrt2026', 'StravaPieter', 'Alle activiteiten', '*.gpx')
gpx_bestanden = glob.glob(folder_path)

print(f" Bezig met inladen van de {len(gpx_bestanden)} GPX bestanden...")

activiteiten_summary = []

# --- 2. Loop door alle bestanden heen ---
for file_path in gpx_bestanden:
    try:
        # Parse XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
        
        data = []
        for trkpt in root.findall('.//gpx:trkpt', ns):
            lat = float(trkpt.get('lat'))
            lon = float(trkpt.get('lon'))
            time_tag = trkpt.find('gpx:time', ns)
            if time_tag is not None:
                data.append({'timestamp': time_tag.text, 'lat': lat, 'lon': lon})
        
        # Sla bestanden met te weinig datapunten over
        if len(data) < 2:
            continue 
            
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Snelle gevectoriseerde Haversine berekening
        lat1, lon1 = np.radians(df['lat'].shift(1)), np.radians(df['lon'].shift(1))
        lat2, lon2 = np.radians(df['lat']), np.radians(df['lon'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
        afstand_m = 6371000 * (2 * np.arcsin(np.sqrt(a)))
        afstand_m = afstand_m.fillna(0)
        
        # Tijdsverschil in seconden
        tijd_sec = (df['timestamp'] - df['timestamp'].shift(1)).dt.total_seconds().fillna(0)
        
        # Totalen berekenen (Stap 3 voor elke activiteit)
        totale_afstand_km = afstand_m.sum() / 1000
        totale_tijd_uur = tijd_sec.sum() / 3600
        
        if totale_tijd_uur > 0:
            gem_snelheid = totale_afstand_km / totale_tijd_uur
            
            # Filter corrupte bestanden met onmogelijke gemiddelden eruit
            if 1 < gem_snelheid < 60:
                activiteiten_summary.append({
                    'bestand': os.path.basename(file_path),
                    'afstand_km': totale_afstand_km,
                    'tijd_uur': totale_tijd_uur,
                    'gem_snelheid_kmh': gem_snelheid
                })
                
    except Exception as e:
        # Foutafhandeling voor als 1 gpx bestandje toevallig corrupt is
        pass

# Maak een overzichtstabel (DataFrame)
df_summary = pd.DataFrame(activiteiten_summary)
print(f"✅ Klaar! {len(df_summary)} activiteiten succesvol geanalyseerd.\n")

# --- 3. Activiteiten classificeren (Onderdeel van Stap 5) ---
def bepaal_sport(snelheid):
    if snelheid < 7.5:
        return 'Wandelen'
    elif snelheid < 18.0:
        return 'Hardlopen'
    else:
        return 'Wielrennen'

# Maak een nieuwe kolom aan met de voorspelde sport
df_summary['sport_type'] = df_summary['gem_snelheid_kmh'].apply(bepaal_sport)

# Print even een korte samenvatting in de terminal
print(df_summary['sport_type'].value_counts())
print("\n👉 Er opent nu een pop-up venster met het histogram. Sluit dat venster om het script te beëindigen.")

# --- 4. Het Histogram Plotten (Stap 5) ---
plt.figure(figsize=(10, 6))

# Kleuren voor de verschillende sporten
kleuren = {'Wandelen': 'green', 'Hardlopen': 'orange', 'Wielrennen': 'blue'}

# Plot een staafjesgrafiek (histogram) per sport, zodat we mooi de groepen (bulten) zien
for sport in kleuren.keys():
    subset = df_summary[df_summary['sport_type'] == sport]
    plt.hist(subset['gem_snelheid_kmh'], bins=15, alpha=0.7, label=sport, color=kleuren[sport], edgecolor='black')

# Opmaak van de grafiek
plt.title('Groepeer de Activiteiten: Histogram van Gemiddelde Snelheden', fontsize=14)
plt.xlabel('Gemiddelde Snelheid (km/u)', fontsize=12)
plt.ylabel('Aantal Activiteiten', fontsize=12)
plt.legend()
plt.grid(axis='y', alpha=0.75)

# Toon de grafiek in een pop-up venster!
plt.show()