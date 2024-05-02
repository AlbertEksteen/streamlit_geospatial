#import configparser
import snowflake.connector
import pandas as pd
import streamlit as st
# from streamlit_folium import folium_static
import folium


#config = configparser.ConfigParser()
#config.read('config.ini')

c_sf_account = st.secrets.Snowflake.account
c_sf_username = st.secrets.Snowflake.username
c_sf_password = st.secrets.Snowflake.password
c_sf_database = st.secrets.Snowflake.database
c_sf_warehouse = st.secrets.Snowflake.warehouse


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

data = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])

st.write(data)

# encode geohash from lat long 
# geohash.encode(lat7itude = , longitude = , precision = 8)
# returns 'qqguguga'

# decode geohash to centerpoint lat long
# geohash.decode('qqguguga')
# returns (latitude, longitude)

# bounding box of the geohash
# geohash.bbox('qqu57zr2v') 
# returns {'s': , 'w': , 'n': , 'e': , }


# Upper_left_point = (N, W)
# Upper_right_point = (N, E)
# Lower_right_point = (S, E)
# Lower_left_point = (S, W)


# we need to draw the map


# lat, long = geohash.decode(‘qqu57’) # get the center of the geohash

m = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=5)

# create a map canvas
m = folium.Map(
    location=[data['latitude'].mean(),data['longitude'].mean()], # set the center location of the map
    zoom_start=9.5,
    tiles="CartoDB Positron"
)

# show the map
m 



#def create_map(data):
#    # Initialize the map centered at a location
#    m = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=10)
#
#    # Add markers for each data point
#    for row in data:
#        latitude = row[1]
#        longitude = row[2]
#        geohash = row[0]
#        folium.Marker([latitude, longitude], popup=geohash).add_to(m)
#        #print(f"latitude = {latitude}, longitude = {longitude}, geohash = {geohash}")
#    
#    return m



#st.write('Map:')
#map_data = create_map(data)
#st.write(map_data)

#map_data = create_map(data)
#folium_static(map_data)
