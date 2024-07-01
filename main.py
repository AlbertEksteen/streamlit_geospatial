#import configparser
import snowflake.connector
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import folium
import geohash

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



geohash_precision = st.slider("How precise do you want your Geohash to be?", 1, 8, 6)


# Create a cursor object
cursor = conn.cursor()
query = f'''
with raw_data as (
select  Start_Time as datetime, 
        Start_Lat as latitude, 
        Start_Lng as longitude,
        left(GeoHash,{geohash_precision}) as geohash
from	[spatial_data].[dbo].[Accidents_All]
where	County = 'Los Angeles'
)

, geohash_data as (
select  left(geohash,{geohash_precision}) as geohash,
        count(*) as qty
from	[spatial_data].[dbo].[Accidents_All]
where	County = 'Los Angeles'
group   by left(geohash,{geohash_precision})
having	count(*) > 1000
)
select  distinct
        a.geohash,
        b.qty
from	raw_data as a
join	geohash_data as b on b.geohash = a.geohash
'''
cursor.execute(query)
results = cursor.fetchall()

data = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
st.write('Data:')
st.write(data)


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
    edges = [upper_left, upper_right, lower_right, lower_left]
    #edges = [upper_left, lower_right]

    return edges

def geohash_mean(geohash_value):
    bbox_values = geohash.bbox(geohash_value)
    W = bbox_values["w"]
    E = bbox_values["e"]
    N = bbox_values["n"]
    S = bbox_values["s"]

    mean_latitude =  (N + S)
    mean_longitude = (E + W)
    edges = [mean_latitude, mean_longitude]

    return edges


def create_map(data):
    center_lat = 34.0212250625
    center_lon = -118.2293702375
    m = folium.Map(location=[center_lat, center_lon], tiles="OpenStreetMap", zoom_start=12)

    for index, row in data.iterrows():
        edges = geohash_bbox(row['GEOHASH'])
        qty = row['QTY']
        #folium.Marker([latitude, longitude], popup=geohash).add_to(m)
        #folium.Rectangle(bounds=edges, color="blue", fill_color="green", weight=2, popup=edges).add_to(m)
        folium.Polygon(locations=edges, color="blue", weight=3, fill_color="red", fill_opacity=0.3, fill=True, popup=row['GEOHASH'], tooltip=f"{qty} Accidents",).add_to(m)

    return m


st.write('Map:')
map_data = create_map(data)
folium_static(map_data)
