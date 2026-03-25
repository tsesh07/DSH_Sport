import pandas as pd
import matplotlib.pyplot as plt
import os
from bikeride import BikeRide


print('Data is aan het inladen...')
script_map = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(script_map, '..', '..', 'data_hackathon_mrt2026', 'StravaRobin', 'Passo_Duran_Duran_.fit')
file_path = os.path.abspath(file_path)

try:
    ride = BikeRide(file_path)
    df_records = pd.DataFrame(ride.records)
    print("Beschikbare kolommen in deze FIT file:", df_records.columns.tolist())
except Exception as e:
    print(f"Fout bij inladen: {e}. Check of het pad klopt!")
    exit()
    
desired_cols = ['timestamp', 'enhanced_altitude', 'heart_rate', 'hr']
available_cols = [col for col in desired_cols if col in df_records.columns]

df = df_records[available_cols].copy()

df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

print(f'Data is succesvol ingeladen, aantal beschikbare rijen: {len(df)}')

# start en einde van de klim vinden
index_top = df['enhanced_altitude'].idxmax()
tijd_top = df.loc[index_top, 'timestamp']
hoogte_top = df.loc[index_top, 'enhanced_altitude']

# begin van de klim (laagste punt)
df_voor_top = df.iloc[:index_top]
index_start_klim = df_voor_top['enhanced_altitude'].idxmin()
tijd_start = df.loc[index_start_klim, 'timestamp']
hoogte_start = df.loc[index_start_klim, 'enhanced_altitude']

print(f'\n Passo Duran Dataset geladen')
print(f"Start van de klim: rond {tijd_start.strftime('%H:%M:%S')} (Hoogte: {hoogte_start:.1f}m)")
print(f"Top bereikt om:    {tijd_top.strftime('%H:%M:%S')} (Hoogte: {hoogte_top:.1f}m)")

# Grafiek plotten
marge = pd.Timedelta(minutes=5)
df_klim = df[(df['timestamp'] >= (tijd_start - marge)) & (df['timestamp'] <= (tijd_top + marge))]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Hoogteprofiel
ax1.plot(df_klim['timestamp'], df_klim['enhanced_altitude'], color='gray', linewidth=2)
ax1.axvline(x=tijd_start, color='green', linestyle='--', label='Start Klim')
ax1.axvline(x=tijd_top, color='red', linestyle='--', label='Top Bereikt')
ax1.set_title('Hoogteprofiel Passo Duran', fontsize=14)
ax1.set_ylabel('Hoogte (meters)', fontsize=12)
ax1.legend()
ax1.grid(True, alpha=0.3)

# Hartslag
ax2.plot(df_klim['timestamp'], df_klim['heart_rate'], color='crimson', linewidth=1.5, alpha=0.8)
ax2.axvline(x=tijd_start, color='green', linestyle='--')
ax2.axvline(x=tijd_top, color='red', linestyle='--')
ax2.set_title('heart_rate tijdens de beklimming', fontsize=14)
ax2.set_ylabel('heart_rate (BPM)', fontsize=12)
ax2.set_xlabel('Tijd', fontsize=12)
ax2.grid(True, alpha=0.3)

plt.tight_layout()

# Sla op in de huidige map
plot_bestand = os.path.join(script_map, "passo_duran_analyse.png")
plt.savefig(plot_bestand)

print(f"\n Grafiek succesvol opgeslagen op:\n   👉 {plot_bestand}")
plt.show()
