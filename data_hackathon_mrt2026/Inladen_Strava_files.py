from bikeride import BikeRide
import pandas as pd
from bikeride import get_weather
import numpy as np

ride = BikeRide('Passo_Duran_Duran_.fit')
ride.summary

records = pd.DataFrame(ride.records)[['timestamp', 'lat', 'lon', 'enhanced_altitude', 'power', 'cadence', 'temperature']]
sgms = pd.DataFrame(ride.segments)[['timestamp_start', 'timestamp_end', 'lat_start', 'lon_start', 'lat_end', 'lon_end', 'temp_recorded_start']]


