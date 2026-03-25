from bikeride import BikeRide
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Load the data
script_dir = Path(__file__).parent
file_path = script_dir / 'StravaRobin' / 'Passo_Duran_Duran_.fit'
ride = BikeRide(str(file_path))

df_records = pd.DataFrame(ride.records)

desired_cols = ['timestamp', 'lat', 'lon', 'enhanced_altitude', 'power', 'cadence', 'temperature']

available_cols = [col for col in desired_cols if col in df_records.columns]

records = df_records[available_cols]

print(f"Successfully loaded {len(records)} rows!")
print(f"Columns found: {available_cols}")


plot_data = records.dropna(subset=['lat', 'lon', 'enhanced_altitude']).copy()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

ax1.plot(plot_data['lon'], plot_data['lat'], color='#2980b9', linewidth=2)
ax1.set_title('Course Route: Passo Duran', fontsize=14, fontweight='bold')
ax1.set_xlabel('Longitude', fontsize=12)
ax1.set_ylabel('Latitude', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.5)

ax1.set_aspect('equal', adjustable='datalim')


ax2.plot(plot_data.index, plot_data['enhanced_altitude'], color='#27ae60', linewidth=2)
ax2.fill_between(plot_data.index, plot_data['enhanced_altitude'], color='#27ae60', alpha=0.2)

ax2.set_title('Elevation Profile', fontsize=14, fontweight='bold')
ax2.set_xlabel('Data Points (Sequence)', fontsize=12)
ax2.set_ylabel('Elevation (Meters)', fontsize=12)
ax2.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()