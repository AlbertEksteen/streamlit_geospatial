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

geohash_precision = st.slider(
    label = "How precise do you want your Geohash to be?", 
    min_value = 1, 
    max_value = 8, 
    value = 6,
    step = 1
    )

geohash_top_n_rows = st.slider(
    label = "How many clusters do you want to see?", 
    min_value = 1, 
    max_value = 50, 
    value = 10,
    step = 5
    )


cursor = conn.cursor()
query = f'''
with geohash_data as (
select  top {geohash_top_n_rows}
		left(geohash,{geohash_precision}) as geohash,
        count(*) as qty
from    streamlit.spatial_data.geohash_data
group   by left(geohash,{geohash_precision})
order   by qty desc
)
select  distinct
        b.geohash,
        b.qty
from    geohash_data as b
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
    m = folium.Map(location=[center_lat, center_lon], tiles="OpenStreetMap", zoom_start=11)

    # Add markers for each data point
    for index, row in data.iterrows():
        edges = geohash_bbox(row['GEOHASH'])
        qty = row['QTY']
        folium.Polygon(locations=edges, color="blue", weight=3, fill_color="red", fill_opacity=0.3, fill=True, popup=row['GEOHASH'], tooltip=f"{qty} Accidents",).add_to(m)

    return m


st.write('Map:')
map_data = create_map(data)
folium_static(map_data)
