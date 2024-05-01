import configparser
import snowflake.connector
import pandas as pd
import streamlit as st


config = configparser.ConfigParser()
config.read('config.ini')

# value = config['SectionName']['VariableName'] 
c_sf_account = config.get('Snowflake', 'account')
c_sf_username = config.get('Snowflake', 'username')
c_sf_password = config.get('Snowflake', 'password')
c_sf_database = config.get('Snowflake', 'database')
c_sf_warehouse = config.get('Snowflake', 'warehouse')


conn = snowflake.connector.connect(
    user=c_sf_username,
    password=c_sf_password,
    account=c_sf_account,
    warehouse=c_sf_warehouse,
    database=c_sf_database
)

# Create a cursor object
cursor = conn.cursor()


query = "SELECT * FROM STREAMLIT.SPATIAL_DATA.GEOHASH_DATA"

# Execute query
cursor.execute(query)

# Fetch results
results = cursor.fetchall()

df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])

st.write(df)
