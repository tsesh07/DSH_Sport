import pandas as pd
import numpy as np
import os
import glob
from bikeride import BikeRide

script_map = os.path.dirname(os.path.abspath(__file__))
data_map = os.path.abspath(os.path.join(script_map, '..', '..', 'data_hackathon_mrt2026'))

fit_bestanden = glob.glob(os.path.join(data_map, 'StravaPieter', '**', '*.fit'), recursive=True)

gekozen_bestand = None
df = None

# Zoeken automatisch naar een hardlooprit (onder 16 km/u) die langer is dan 10 kilometer
for bestand in fit_bestanden:
    try:
        ride = BikeRide(bestand)
        temp_df = pd.DataFrame(ride.records)
        
        if 'enhanced_speed' not in temp_df.columns or 'distance' not in temp_df.columns:
            continue
            
        gem_snelheid = (temp_df['enhanced_speed'] * 3.6).mean()
        totale_afstand = temp_df['distance'].max()
        
        # Hardlopen EN meer dan 10.000 meter
        if gem_snelheid < 16.0 and totale_afstand > 10000:
            gekozen_bestand = bestand
            df = temp_df.dropna(subset=['distance', 'timestamp']).copy()
            break # Bam, we hebben een goede run!
    except:
        pass

if df is None:
    print("Kon geen geschikte hardlooprit vinden. Misschien moet je in Jan's map zoeken!")
    exit()

print(f"Grote hardlooprit gevonden: {os.path.basename(gekozen_bestand)}")
print(f"   Totale afstand: {df['distance'].max() / 1000:.2f} km")

# Tijd vanaf de start in seconden
df['cum_tijd'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()
df['cum_afstand'] = df['distance'] 

max_afstand = df['cum_afstand'].max()
grid_afstand = np.arange(0, max_afstand, 10)

grid_tijd = np.interp(grid_afstand, df['cum_afstand'], df['cum_tijd'])

df_perfect = pd.DataFrame({'afstand_m': grid_afstand, 'tijd_sec': grid_tijd})

# Bereken de snelste tijd
def format_tijd(seconden):
    minuten = int(seconden // 60)
    secs = int(seconden % 60)
    return f"{minuten:02d}:{secs:02d}"

print("\nRESULTATEN (Snelste Segmenten):")
print("="*40)

# Aantal stappen van 10 meter die nodig zijn voor de afstand
afstanden = {'1 km': 100, '5 km': 500, '10 km': 1000}

for naam, stappen in afstanden.items():
    if len(df_perfect) > stappen:
        # De tijd die het kostte om deze afstand af te leggen = Tijd NU min Tijd X stappen geleden
        verschil = df_perfect['tijd_sec'] - df_perfect['tijd_sec'].shift(stappen)
        
        snelste_seconden = verschil.min()
        gem_kmu = (int(naam.split()[0]) / (snelste_seconden / 3600))
        
        print(f"Snelste {naam:5}: {format_tijd(snelste_seconden)}  ({gem_kmu:.2f} km/u)")

print("="*40)


# Logica: is dit een wedstrijd?
print("\nWedstrijd Analyse:")
afstand_km = max_afstand / 1000
if (9.9 < afstand_km < 10.3) or (21.0 < afstand_km < 21.4):
    print("VERMOEDELIJK EEN WEDSTRIJD! De totale afstand stopt héél dicht op een officieel wedstrijd-getal (10k of Halve Marathon). Recreanten rennen vaak net even een willekeurig rondje van 11.2 km of 9.4 km.")
else:
    print("Waarschijnlijk een reguliere training (Afstand is niet exact een wedstrijd-standaard).")