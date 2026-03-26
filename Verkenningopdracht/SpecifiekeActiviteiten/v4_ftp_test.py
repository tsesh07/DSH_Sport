import pandas as pd
import xml.etree.ElementTree as ET
import os
import matplotlib.pyplot as plt

script_map = os.path.dirname(os.path.abspath(__file__))
base_data_map = os.path.join(script_map, '..', '..', 'data_hackathon_mrt2026')
bestandsnaam = 'Wattbike_The_20_Minute_Test.tcx'

pad_robin = os.path.join(base_data_map, 'StravaRobin', bestandsnaam)
pad_pieter = os.path.join(base_data_map, 'StravaPieter', bestandsnaam)

file_path = pad_robin if os.path.exists(pad_robin) else pad_pieter

print("⚡ Wattbike TCX inladen, momentje...")

data = []
tree = ET.parse(file_path)
root = tree.getroot()

for trkpt in root.iter():
    if trkpt.tag.endswith('Trackpoint'):
        tijd = None
        watts = 0.0
        for child in trkpt.iter():
            if child.tag.endswith('Time'):
                tijd = child.text
            elif child.tag.endswith('Watts'):
                watts = float(child.text)
        
        if tijd:
            data.append({'timestamp': tijd, 'power': watts})

df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

print(f"Data geladen! ({len(df)} seconden aan data)")


# FTP BEREKENEN (20 Min Rolling Average)
print("\n20-minuten piekvermogen zoeken...")

df.set_index('timestamp', inplace=True)

# Bereken het gemiddelde vermogen over een 'raam' van 20 minuten dat steeds doorschuift
# Min_periods=1200 zorgt ervoor dat hij alleen kijkt naar volle blokken van 20 minuten (1200 sec)
df['20min_gemiddelde'] = df['power'].rolling('20min', min_periods=1100).mean()

# Zoek het absolute piekmoment van die 20 minuten
max_20min_power = df['20min_gemiddelde'].max()
eindtijd_piek = df['20min_gemiddelde'].idxmax()

# De FTP is 95% van deze 20-minuten waarde!
ftp_waarde = max_20min_power * 0.95

print("="*40)
print(f"🏆 FTP TEST RESULTATEN")
print("="*40)
print(f"Hoogste 20-min gemiddelde: {max_20min_power:.1f} Watt")
print(f"Berekende FTP (95%):       {ftp_waarde:.1f} Watt")
print("="*40 + "\n")

# Vermogensgrafiek
print("Grafiek genereren...")

plt.figure(figsize=(12, 6))

# Plot de ruwe power data in lichtblauw
plt.plot(df.index, df['power'], color='lightblue', alpha=0.6, label='Ruwe Vermogen (Watts)')

# Plot de vloeiende 20-minuten lijn in donkerblauw
plt.plot(df.index, df['20min_gemiddelde'], color='darkblue', linewidth=2, label='20-min Gemiddelde')

# Markeer het piekmoment
plt.axvline(x=eindtijd_piek, color='red', linestyle='--', label='Einde van beste 20 minuten')

plt.title(f'Wattbike Test - FTP: {ftp_waarde:.0f}W', fontsize=14, fontweight='bold')
plt.xlabel('Tijd', fontsize=12)
plt.ylabel('Vermogen (Watt)', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

# Opslaan
plot_bestand = os.path.join(script_map, "ftp_test_grafiek.png")
plt.savefig(plot_bestand)
print(f"Grafiek opgeslagen op:\n   👉 {plot_bestand}")

plt.show()