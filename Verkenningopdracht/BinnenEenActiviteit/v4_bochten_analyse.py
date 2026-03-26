import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from bikeride import BikeRide

# Data inladen
script_map = os.path.dirname(os.path.abspath(__file__))
data_map = os.path.abspath(os.path.join(script_map, '..', '..', 'data_hackathon_mrt2026'))

fit_bestanden = glob.glob(os.path.join(data_map, 'StravaRobin', '**', '*.fit'), recursive=True)

df = None
gekozen_bestand = None

# Zoek een bestand met genoeg data
for bestand in fit_bestanden:
    try:
        ride = BikeRide(bestand)
        temp_df = pd.DataFrame(ride.records)
        if 'lat' in temp_df.columns and 'enhanced_speed' in temp_df.columns:
            if len(temp_df) > 1000: # Rit moet niet te kort zijn
                df = temp_df.dropna(subset=['lat', 'lon', 'enhanced_speed']).copy()
                gekozen_bestand = bestand
                break
    except:
        continue

if df is None:
    print("Kon geen geschikte rit vinden.")
    exit()

print(f"Rit gevonden: {os.path.basename(gekozen_bestand)}")
df = df.reset_index(drop=True)


# Richting berekenen
def bereken_bearing(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = np.sin(dlon) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1) * np.cos(lat2) * np.cos(dlon))
    initial_bearing = np.arctan2(x, y)
    return (np.degrees(initial_bearing) + 360) % 360

# Kijken 3 seconden vooruit om de richting te bepalen
window = 3
df['bearing_in'] = bereken_bearing(df['lat'].shift(window), df['lon'].shift(window), df['lat'], df['lon'])
df['bearing_out'] = bereken_bearing(df['lat'], df['lon'], df['lat'].shift(-window), df['lon'].shift(-window))

verschil = abs(df['bearing_out'] - df['bearing_in'])
df['richting_verschil'] = np.where(verschil > 180, 360 - verschil, verschil)

# Snelheid in km/u
df['snelheid_kmu'] = df['enhanced_speed'] * 3.6

# Perfecte bocht zoeken
# Zoeken een bocht die scherp is (bijv > 70 graden) maar waarbij hij ook redelijk doortrapte
scherpe_bochten = df[(df['richting_verschil'] > 70) & (df['richting_verschil'] < 130)].copy()

if scherpe_bochten.empty:
    print("Geen mooie haakse bochten gevonden in deze rit, probeer de drempel aan te passen!")
    exit()

# Pak de allereerste goede bocht die we tegenkomen
index_bocht = scherpe_bochten.index[0]
hoek = df.loc[index_bocht, 'richting_verschil']

print(f"↩Bocht gevonden! Draai van {hoek:.1f} graden.")

# Knippen een 'snapshot' uit de data: 15 seconden VOOR de bocht tot 15 seconden ERNA
marge = 15
df_bocht = df.iloc[index_bocht - marge : index_bocht + marge + 1].copy()
df_bocht['tijd_relatief'] = range(-marge, marge + 1) # Tijdlijn van -15 tot +15 sec


# Data Plotten
plt.figure(figsize=(10, 6))

plt.plot(df_bocht['tijd_relatief'], df_bocht['snelheid_kmu'], color='crimson', linewidth=3, label='Snelheid (km/u)')

# Markeer de Apex (het midden van de bocht, tijd = 0)
plt.axvline(x=0, color='black', linestyle='--', alpha=0.5, label='Apex (Midden van de bocht)')

# Visuele zones toevoegen
plt.axvspan(-15, 0, color='red', alpha=0.1, label='Rem-zone (Entry)')
plt.axvspan(0, 15, color='green', alpha=0.1, label='Acceleratie-zone (Exit)')

plt.title(f'Bochten-Analyse: Remmen & Accelereren (Hoek: {hoek:.0f}°)', fontsize=14, fontweight='bold')
plt.xlabel('Seconden t.o.v. de bocht', fontsize=12)
plt.ylabel('Snelheid (km/u)', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim(-15, 15)

plot_bestand = os.path.join(script_map, "bocht_analyse_plot.png")
plt.savefig(plot_bestand)
print(f"Grafiek opgeslagen: {plot_bestand}")

plt.show()