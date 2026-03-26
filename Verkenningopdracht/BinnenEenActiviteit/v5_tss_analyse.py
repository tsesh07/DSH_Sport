import pandas as pd
import numpy as np
import os
import glob
from bikeride import BikeRide

script_map = os.path.dirname(os.path.abspath(__file__))
data_map = os.path.abspath(os.path.join(script_map, '..', '..', 'data_hackathon_mrt2026'))

fit_bestanden = glob.glob(os.path.join(data_map, 'StravaRobin', '**', '*.fit'), recursive=True)

df = None
gekozen_bestand = None

for bestand in fit_bestanden:
    try:
        ride = BikeRide(bestand)
        temp_df = pd.DataFrame(ride.records)
        
        # Zoeken naar power, tijd en snelheid
        if 'power' in temp_df.columns and 'timestamp' in temp_df.columns and 'enhanced_speed' in temp_df.columns:
            
            gem_snelheid = (temp_df['enhanced_speed'] * 3.6).mean()
            totale_afstand = temp_df['distance'].max() / 1000
            
            # FILTER: Snelheid > 20 km/u (Geen marathons!) EN Afstand > 30 km
            if gem_snelheid > 20.0 and totale_afstand > 30:
                df = temp_df.dropna(subset=['power', 'timestamp']).copy()
                gekozen_bestand = bestand
                break
            elif gem_snelheid <= 20.0 and totale_afstand > 30:
                print(f"Skippen: {os.path.basename(bestand)} (Te langzaam voor de fiets, waarschijnlijk hardlopen!)")
    except:
        continue

if df is None:
    print("Kon geen geschikte wielrenrit met vermogensmeter vinden.")
    exit()

print(f"Echte wielrenrit geladen: {os.path.basename(gekozen_bestand)}")


# 2. NORMALIZED POWER (NP) BEREKENEN
# Zorg dat de tijdlijn klopt voor de rolling window
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)
df.set_index('timestamp', inplace=True)

# rolling avg: 30-seconden vloeiend gemiddelde
rolling_30s = df['power'].rolling('30s').mean().dropna()

# Tot de macht 4, gemiddelde pakken, en dan de 4e-machtswortel
np_waarde = (rolling_30s ** 4).mean() ** 0.25

gemiddeld_vermogen = df['power'].mean()


# TRAINING STRESS SCORE (TSS) BEREKENEN
# FTP is een aanname op basis van eerdere testen. (Je kunt dit aanpassen!)
FTP = 250.0 

# Totale tijd in seconden
totale_tijd_sec = (df.index[-1] - df.index[0]).total_seconds()

# Intensity Factor (IF) = Hoe zwaar was de rit t.o.v. de maximale FTP?
intensity_factor = np_waarde / FTP

# Officiële TSS formule van TrainingPeaks
tss_score = (totale_tijd_sec * np_waarde * intensity_factor) / (FTP * 36)

# Printen van resultaat
print("\n" + "="*40)
print(f"INTENSITEIT RAPPORT")
print("="*40)
print(f"Totale Tijd:           {totale_tijd_sec / 3600:.1f} uur")
print(f"Gemiddeld Vermogen:    {gemiddeld_vermogen:.0f} Watt")
print(f"Normalized Power (NP): {np_waarde:.0f} Watt")
print("-" * 40)
print(f"FTP (Referentie):      {FTP} Watt")
print(f"Intensity Factor (IF): {intensity_factor:.2f} (1.00 is een uur lang maximaal)")
print(f"Training Stress Score: {tss_score:.0f} TSS")
print("="*40)

# Uitleg voor de TSS score
if tss_score < 150:
    print("\nConclusie: Een redelijk lichte/gemiddelde trainingsrit. (Herstel duurt 1 dag)")
elif tss_score < 300:
    print("\nConclusie: Een zware rit! De benen doen wel even pijn. (Herstel duurt 2 dagen)")
elif tss_score < 450:
    print("\nConclusie: Extreem zwaar. Waarschijnlijk een zware koers of bergrit. (Herstel duurt meerdere dagen)")
else:
    print("\nConclusie: Dit was een monster-etappe of een zware Gran Fondo.")