import pandas as pd
import duckdb

weather_stations = pd.DataFrame({
    'station_id': [1, 2],
    'station_name': ['Rampo', 'Tire']
    })

measurements = pd.DataFrame({
    'station_id': [1, 2],
    'measurement': [64.6, -43.1],
    })

# Query the DataFrame with DuckDB
query = '''
    SELECT 
        ws.station_name,
        m.measurement,

    FROM weather_stations ws 
    
    JOIN measurements m 
        ON ws.station_id = m.station_id 

    '''

result = duckdb.sql(query)
print(result)