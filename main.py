#import configparser
import snowflake.connector
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import folium
import geohash
from math import log10

c_sf_account = st.secrets["Snowflake"]["account"]
c_sf_username = st.secrets["Snowflake"]["username"]
c_sf_password = st.secrets["Snowflake"]["password"]
c_sf_database = st.secrets["Snowflake"]["database"]
c_sf_warehouse = st.secrets["Snowflake"]["warehouse"]


conn = snowflake.connector.connect(
    user=c_sf_username,
    password=c_sf_password,
    account=c_sf_account,
    warehouse=c_sf_warehouse,
    database=c_sf_database
)

# Create a cursor object
cursor = conn.cursor()
query = 'SELECT GEOHASH, LATITUDE, LONGITUDE FROM STREAMLIT.SPATIAL_DATA.GEOHASH_DATA'
cursor.execute(query)
results = cursor.fetchall()


data = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
st.write('Data:')
st.write(data)


print(geohash.bbox('9q8zp6z4mwvg'))



def geohash_bbox(geohash_value):
    bbox_values = geohash.bbox(geohash_value)
    W = bbox_values["w"]
    E = bbox_values["e"]
    N = bbox_values["n"]
    S = bbox_values["s"]

    upper_left = (N, W)
    upper_right = (N, E)
    lower_right = (S, E)
    lower_left = (S, W)
    #edges = [upper_left, upper_right, lower_right, lower_left]
    edges = [upper_left, lower_right]

    return edges

print(geohash_bbox('9q8zp6z4'))

def create_map(data, precision):
    mean_latitude = data[['LATITUDE']].mean()
    mean_longitude = data[['LONGITUDE']].mean()
    # Initialize the map centered at a location
    m = folium.Map(location=[mean_latitude, mean_longitude], zoom_start=10, tiles="OpenStreetMap")

    # Add markers for each data point
    for index, row in data.iterrows():
        latitude = row['LATITUDE']
        longitude = row['LONGITUDE']
        edges = geohash_bbox(row['GEOHASH'][:precision])
        #folium.Marker([latitude, longitude], popup=geohash).add_to(m)
        folium.Rectangle(bounds=edges, color="blue", fill_color="green", weight=1, popup=edges).add_to(m)
    
    return m


st.write('Map:')
map_data = create_map(data, 6)
folium_static(map_data)
