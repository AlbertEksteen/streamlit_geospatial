#import configparser
import snowflake.connector
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import folium


#config = configparser.ConfigParser()
#config.read('config.ini')



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


query = "SELECT * FROM STREAMLIT.SPATIAL_DATA.GEOHASH_DATA"

# Execute query
cursor.execute(query)

# Fetch results
results = cursor.fetchall()

data = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])

st.write(data)




# we need to draw the map


# lat, long = geohash.decode(‘qqu57’) # get the center of the geohash

#latitude_index = int(data.columns.get_loc('LATITUDE'))
#longitude_index = int(data.columns.get_loc('LONGITUDE'))

mean_latitude = data[['LATITUDE']].mean()
mean_longitude = data[['LONGITUDE']].mean()

st.write(mean_latitude)
st.write(mean_longitude)

# create a map canvas
m = folium.Map(
    location=[mean_latitude, mean_longitude], 
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
