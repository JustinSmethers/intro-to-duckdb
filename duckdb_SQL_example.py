import duckdb

# Connect to an in-memory database
con = duckdb.connect(database=':memory:')

# Alternatively, connect to a database file
# con = duckdb.connect(database='my_database.db')

# Create a table and insert some data
con.execute("CREATE TABLE students (name VARCHAR, grade FLOAT);")
con.execute("INSERT INTO students VALUES ('Alice', 9.0);")

# Query the table
result = con.execute("SELECT * FROM students").fetchall()
print(result)

# Export the table to a CSV file
con.execute("COPY students TO 'students.csv' (HEADER, DELIMITER ',');")

# Query the csv file
result = con.execute("SELECT * FROM read_csv_auto('students.csv')").fetchall()
print(result)


