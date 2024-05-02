import duckdb
import requests
from dotenv import load_dotenv
import os


# Load the environment variables
load_dotenv()

# The link to download the parquet file
url = os.getenv('PARQUET_URL')

# The name of the parquet file
file_name = 'yellow_tripdata_2024-01.parquet'

# Download the parquet file
response = requests.get(url)
response.raise_for_status() # Raise an exception for bad status codes

# Save the parquet file
with open(file_name, 'wb') as f:
    f.write(response.content)

# Download the zone lookup file
zone_lookup_url = os.getenv('ZONE_LOOKUP_URL')
zone_lookup_file = 'taxi_zone_lookup.csv'
response = requests.get(zone_lookup_url)
response.raise_for_status()

# Save the zone lookup file
with open(zone_lookup_file, 'wb') as f:
    f.write(response.content)

# Connect to an in-memory database
con = duckdb.connect(database=':memory:')

# Create a table from the parquet file
con.execute(f"CREATE TABLE trips AS SELECT * FROM parquet_scan('{file_name}')")

# Rename the datetime fields
con.execute("ALTER TABLE trips RENAME COLUMN tpep_pickup_datetime TO pickup_datetime")
con.execute("ALTER TABLE trips RENAME COLUMN tpep_dropoff_datetime TO dropoff_datetime")

# Create a table from the zone lookup file
con.execute(f"CREATE TABLE zone_lookup AS SELECT * FROM read_csv_auto('{zone_lookup_file}')")

# Export the trips table to a CSV file
con.execute("COPY trips TO 'trips.csv' (HEADER, DELIMITER ',')")

# Join the trips table with the zone lookup table
con.execute("CREATE TABLE enriched_trips AS SELECT * FROM trips JOIN zone_lookup ON trips.PULocationID = zone_lookup.LocationID")

# Export the joined table to a CSV file
con.execute("COPY enriched_trips TO 'enriched_trips.csv' (HEADER, DELIMITER ',')")