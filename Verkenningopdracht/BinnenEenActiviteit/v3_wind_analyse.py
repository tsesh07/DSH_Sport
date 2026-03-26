import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from bikeride import BikeRide

script_map = os.path.dirname(os.path.abspath(__file__))
data_map = os.path.abspath(os.path.join(script_map, '..', '..', 'data_hackathon_mrt2026'))

fit_bestanden = glob.glob(os.path.join(data_map, 'StravaRobin', '**', '*.fit'), recursive=True)

df = None
gekozen_bestand = None

# Zoek een bestand dat GPS (lat/lon), snelheid, hoogte én power heeft
for bestand in fit_bestanden:
    try:
        ride = BikeRide(bestand)
        temp_df = pd.DataFrame(ride.records)
        
        required_cols = ['lat', 'lon', 'enhanced_speed', 'enhanced_altitude', 'power']
        if all(col in temp_df.columns for col in required_cols):
            # Een redelijke rit (minimaal 20 km) om alle richtingen te hebben
            if (temp_df['distance'].max() / 1000) > 20:
                df = temp_df.dropna(subset=required_cols).copy()
                gekozen_bestand = bestand
                break
    except:
        continue

if df is None:
    print("Kon geen geschikte rit vinden met de juiste sensoren.")
    exit()

print(f"Rit gevonden: {os.path.basename(gekozen_bestand)}")


# Feature Engineering: Data
# Snelheid naar km/u
df['snelheid_kmu'] = df['enhanced_speed'] * 3.6

# Heuvels eruit filteren
df['hoogte_verschil'] = df['enhanced_altitude'].diff().fillna(0)
df_vlak = df[abs(df['hoogte_verschil']) < 0.3].copy() # Max 30cm stijging/daling per seconde

# Alleen de momenten met een "gemiddelde" inspanning (150 tot 250 Watt)
df_constant = df_vlak[(df_vlak['power'] >= 150) & (df_vlak['power'] <= 250)].copy()

print(f"   Overgebleven vlakke GPS-punten met constant vermogen: {len(df_constant)}")


# Kompas richtingen
def bereken_bearing(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = np.sin(dlon) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1) * np.cos(lat2) * np.cos(dlon))
    initial_bearing = np.arctan2(x, y)
    return (np.degrees(initial_bearing) + 360) % 360

df_constant['lat_next'] = df_constant['lat'].shift(-1)
df_constant['lon_next'] = df_constant['lon'].shift(-1)
df_constant = df_constant.dropna(subset=['lat_next'])

df_constant['richting'] = bereken_bearing(df_constant['lat'], df_constant['lon'], df_constant['lat_next'], df_constant['lon_next'])

# Verdeel de 360 graden in 8 windrichtingen (N, NE, O, ZO, Z, ZW, W, NW)
bins = [0, 45, 90, 135, 180, 225, 270, 315, 360]
labels = ['N', 'NO', 'O', 'ZO', 'Z', 'ZW', 'W', 'NW']

df_constant['richting_bin'] = pd.cut((df_constant['richting'] + 22.5) % 360, bins=bins, labels=labels, right=False)


# Resultaten berekenen en plotten
# Bereken de gemiddelde snelheid per windrichting bij ~200 Watt
snelheid_per_richting = df_constant.groupby('richting_bin', observed=False)['snelheid_kmu'].mean()

print("\n📊 Snelheid per kompasrichting (bij ~200 Watt):")
print(snelheid_per_richting.round(1).to_string())

# Zoek wind mee en wind tegen
wind_mee_richting = snelheid_per_richting.idxmax()
wind_tegen_richting = snelheid_per_richting.idxmin()

print("\n" + "="*40)
print(f"CONCLUSIE WIND-ANALYSE")
print("="*40)
print(f"Wind Mee (Snelst):    Richting {wind_mee_richting} ({snelheid_per_richting[wind_mee_richting]:.1f} km/u)")
print(f"Wind Tegen (Traagst): Richting {wind_tegen_richting} ({snelheid_per_richting[wind_tegen_richting]:.1f} km/u)")
print("De wind waaide deze dag dus hoogstwaarschijnlijk vanuit het " + wind_tegen_richting + "!")
print("="*40)

# Radar chart
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
snelheden = snelheid_per_richting.fillna(0).tolist() # Vul lege richtingen met 0

# Circulair grafiek
snelheden += snelheden[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
ax.set_theta_direction(-1) # Met de klok mee
ax.set_theta_offset(np.pi / 2.0) # Noord bovenaan

ax.plot(angles, snelheden, color='blue', linewidth=2, linestyle='solid')
ax.fill(angles, snelheden, color='blue', alpha=0.25)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=12, fontweight='bold')
ax.set_title(f"Windroos (Snelheid bij 150-250 Watt)\nBestand: {os.path.basename(gekozen_bestand)}", size=14, pad=20)

plot_bestand = os.path.join(script_map, "wind_analyse_plot.png")
plt.savefig(plot_bestand)
print(f"\nWindroos grafiek opgeslagen: 👉 {plot_bestand}")
plt.show()