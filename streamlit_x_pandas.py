import streamlit as st
import pandas as pd
import plotly.express as px
import time  # To measure elapsed time

# Start timing the rendering process
start_time = time.time()

# Load the NYC taxi data into a pandas DataFrame
taxi_data_file_path = 'enriched_trips.csv'
trips = pd.read_csv(taxi_data_file_path)

# Ensure the pickup_datetime column is of datetime type
trips['pickup_datetime'] = pd.to_datetime(trips['pickup_datetime'])

# Create a sorted list of all unique boroughs from the trips data
# boroughs = sorted(trips['Borough'])

# Clean the 'Borough' column by replacing NaN with a default value and ensuring all entries are strings
trips.fillna({'Borough': 'Unknown'}, inplace=True)
trips['Borough'] = trips['Borough'].astype(str)

# Create a sorted list of unique boroughs from the trips data
boroughs = sorted(trips['Borough'].unique())

# Use the session state to retain multi-select values
selected_boroughs = st.multiselect("Select boroughs", boroughs, default=boroughs)

# Create a date range for the weeks between January 1st and January 31st
date_ranges = pd.date_range(start='2024-01-01', end='2024-01-31', freq='W-MON').normalize()

# Add a select box to choose a week
selected_week_str = st.selectbox('Select a week', [date.strftime('%Y-%m-%d') for date in date_ranges])

# Convert the selected week to pandas Timestamp
selected_week = pd.to_datetime(selected_week_str)

# Filter the trips DataFrame by selected week and selected boroughs
filtered_trips = trips[
    (trips['pickup_datetime'] >= selected_week) &
    (trips['pickup_datetime'] < selected_week + pd.Timedelta(weeks=1)) &
    (trips['Borough'].isin(selected_boroughs))
]

st.write('Caluclate the max and min fare amount for the selected week')

# Calculate the max and min fare amount for the selected week with pandas
max_fare_amount = filtered_trips['fare_amount'].max()
min_fare_amount = filtered_trips['fare_amount'].min()

# Display the max and min fare amount
st.write(f"Max fare amount: `{max_fare_amount:.2f}` Min fare amount: `{min_fare_amount:.2f}`")

# Display the contructed SQL query for reference (just for display, not executing in DuckDB)
query = f'''
    max_fare_amount = filtered_trips['fare_amount'].max()
    min_fare_amount = filtered_trips['fare_amount'].min()
'''
st.code(query)




# Extract day of the week (DOW) and hour from 'pickup_datetime'
filtered_trips['pickup_day'] = filtered_trips['pickup_datetime'].dt.dayofweek  # Monday=0, Sunday=6
filtered_trips['pickup_hour'] = filtered_trips['pickup_datetime'].dt.hour

# Group by 'pickup_day' and 'pickup_hour' and count occurrences
grouped_data = filtered_trips.groupby(['pickup_day', 'pickup_hour']).size().reset_index(name='number_of_trips')

# Map the numerical day to the day of the week
day_of_week_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
grouped_data['pickup_day'] = grouped_data['pickup_day'].map(day_of_week_map)

# Pivot the data for heatmap visualization
filtered_data = grouped_data.pivot(index='pickup_day', columns='pickup_hour', values='number_of_trips')

# Reorder the days of the week to ensure correct order
filtered_data = filtered_data.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

# Create a heatmap to visualize the number of trips by hour and day of the week
fig = px.imshow(filtered_data, labels={'pickup_hour': 'Hour', 'pickup_day': 'Day of the week', 'value': 'Number of trips'}, title='Number of trips by hour and day of the week')

# Display heatmap in Streamlit
st.write('Create a heatmap of the number of trips by hour and day of the week')
st.plotly_chart(fig)

# Display the contructed SQL query for reference (just for display, not executing in DuckDB)
query = f'''
    filtered_trips['pickup_day'] = filtered_trips['pickup_datetime'].dt.dayofweek  # Monday=0, Sunday=6
    filtered_trips['pickup_hour'] = filtered_trips['pickup_datetime'].dt.hour

    grouped_data = filtered_trips.groupby(['pickup_day', 'pickup_hour']).size().reset_index(name='number_of_trips')

    day_of_week_map = {{0: 'Monday', 
                        1: 'Tuesday', 
                        2: 'Wednesday', 
                        3: 'Thursday', 
                        4: 'Friday', 
                        5: 'Saturday', 
                        6: 'Sunday'}}
                        
    grouped_data['pickup_day'] = grouped_data['pickup_day'].map(day_of_week_map)
    
'''    

st.code(query)


# Calculate the time elapsed since the start of rendering
elapsed_time = time.time() - start_time

# Display the elapsed time in seconds
st.write(f"Time elapsed: {elapsed_time:.2f} seconds")
