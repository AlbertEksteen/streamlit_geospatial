#import configparser
import snowflake.connector
import pandas as pd
import streamlit as st


#config = configparser.ConfigParser()
#config.read('config.ini')

c_sf_account = st.secrets.db_credentials.account
c_sf_username = st.secrets.db_credentials.username
c_sf_password = st.secrets.db_credentials.password
c_sf_database = st.secrets.db_credentials.database
c_sf_warehouse = st.secrets.db_credentials.warehouse


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
