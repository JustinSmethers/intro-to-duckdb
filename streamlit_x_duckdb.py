import duckdb
import streamlit as st
import pandas as pd
import plotly.express as px
import time  # To measure elapsed time


# Start timing the rendering process
start_time = time.time()

# Load the NYC taxi data into DuckDB
con = duckdb.connect(database=':memory:')
taxi_data_file_path = 'enriched_trips.csv'
con.execute(f"CREATE TABLE trips AS SELECT * FROM read_csv_auto('{taxi_data_file_path}')")

# Create a list of all unique boroughs from the trips data
boroughs = con.execute("SELECT DISTINCT borough FROM trips").fetchdf()['Borough'].sort_values().tolist()

# Use the session state to retain multi-select values
selected_boroughs = st.multiselect("Select boroughs", boroughs, default=boroughs)

# Create date range for the weeks between January 1st and January 31st
date_ranges = pd.date_range(start='2024-01-01', end='2024-01-31', freq='W-MON').date

# Add a select box to the app
selected_week = st.selectbox('Select a week', date_ranges)


# Create or replace a filtered trips table in the DuckDB database
query = f'''
    CREATE OR REPLACE VIEW filtered_trips AS
    SELECT *
    FROM trips
    WHERE
        pickup_datetime >= \'{selected_week}\'
        AND pickup_datetime < \'{selected_week + pd.Timedelta(weeks=1)}\'
        AND borough IN ({', '.join([f"'{borough}'" for borough in selected_boroughs])})
    '''
con.execute(query)


st.write('Caluclate the max and min fare amount for the selected week')

# Calculate the max and min fare amount for the selected week with DuckDB
query = f'''
    SELECT
        MAX(fare_amount) AS max_fare_amount,
        MIN(fare_amount) AS min_fare_amount
    FROM filtered_trips
    '''
result = con.execute(query).fetchdf()

# Show the result
st.write("Max fare amount:", result['max_fare_amount'][0], "Min fare amount:", result['min_fare_amount'][0])

# Show the query
st.write('Query:')
st.code(query)


st.write('Create a heatmap of the number of trips by hour and day of the week')
# Show a heatmap of the number of trips by hour and day of the week with DuckDB
query = f'''
    SELECT
        pickup_day,
        pickup_hour,
        COUNT(*) AS number_of_trips
    FROM
        (
            SELECT
                pickup_datetime,
                EXTRACT(DOW FROM pickup_datetime) AS pickup_day,
                EXTRACT(HOUR FROM pickup_datetime) AS pickup_hour
            FROM
                filtered_trips
        )
    GROUP BY
        pickup_day,
        pickup_hour
    ORDER BY
        pickup_day,
        pickup_hour
    '''

# Execute the query and convert the result to a DataFrame
filtered_data = con.execute(query).df()

# Convert pickup_day to a string to display the day of the week
filtered_data['pickup_day'] = filtered_data['pickup_day'].map({0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'})

# Reshape the data to create a heatmap
filtered_data = filtered_data.pivot(index='pickup_day', columns='pickup_hour', values='number_of_trips')

# Order the days of the week
filtered_data = filtered_data.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

# Create a heatmap to see the number of trips by hour and day of the week
fig = px.imshow(filtered_data, labels={'pickup_hour': 'Hour', 'pickup_day': 'Day of the week', 'value': 'Number of trips'}, title='Number of trips by hour and day of the week')

# Show the heatmap
st.plotly_chart(fig)

# Show the query
st.write('Query:')
st.code(query)

# Calculate the time elapsed since the start of rendering
elapsed_time = time.time() - start_time

# Display the elapsed time in seconds
st.write(f"Time elapsed: {elapsed_time:.2f} seconds")