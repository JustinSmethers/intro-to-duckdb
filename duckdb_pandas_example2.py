import pandas as pd
import duckdb

weather_stations = pd.DataFrame({
    'station_name': ['Rampo', 'Tire'],
    'measurement': [64.6, -43.1]
    })

# Query the DataFrame with DuckDB
query = f"""
    select
        station_name,
        min(measurement) as Min,
        max(measurement) as Max,
        avg(measurement) as Mean
    
    from weather_stations
           
    group by station_name
    order by station_name
    """    

result = duckdb.sql(query)
print(result)