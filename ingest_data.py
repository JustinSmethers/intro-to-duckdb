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

# Connect to an in-memory database
con = duckdb.connect(database=':memory:')

# Create a table from the parquet file
con.execute(f"CREATE TABLE trips AS SELECT * FROM parquet_scan('{file_name}')")

# Rename the datetime fields
con.execute("ALTER TABLE trips RENAME COLUMN tpep_pickup_datetime TO pickup_datetime")
con.execute("ALTER TABLE trips RENAME COLUMN tpep_dropoff_datetime TO dropoff_datetime")

# Export the table to a CSV file
con.execute("COPY trips TO 'trips.csv' (HEADER, DELIMITER ',')")
