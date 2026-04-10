import streamlit as st
import pickle
import numpy as np
import requests
from geopy.geocoders import Nominatim
import json
import os


st.title(" Fare Predictor")
st.markdown("Enter your pickup and drop location and get estimated fare and route map")


st.markdown(
    """
    <style>
    body {
        background-color: #0f111a;
        color: #f5f5f5;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-size: 16px;
        height: 3em;
        width: 100%;
    }
    .stTextInput>div>div>input {
        background-color: #1c1c28;
        color: white;
    }
    .stNumberInput>div>div>input {
        background-color: #1c1c28;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


model = pickle.load(open("model.pkl", 'rb'))
geo = Nominatim(user_agent='fare_app')


st.sidebar.header("Enter Trip Details: Check the right spelling of the place")
pickup_place = st.sidebar.text_input("Pickup Location")
drop_place = st.sidebar.text_input("Drop Location")
passengers = st.sidebar.number_input("Passengers", min_value=1, max_value=4, value=1)
vehicle_type = st.sidebar.selectbox("Vehicle Type", ['Bike', 'Auto', 'Car'])
calculate_btn = st.sidebar.button("Calculate Price")


if calculate_btn:
    loc1 = geo.geocode(pickup_place)
    loc2 = geo.geocode(drop_place)

    if loc1 is None or loc2 is None:
        st.error("Please enter valid locations")
    else:
        lat1, lon1 = loc1.latitude, loc1.longitude
        lat2, lon2 = loc2.latitude, loc2.longitude

        
        url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
        res = requests.get(url).json()
        distance = res['routes'][0]['distance'] / 1000  # in km
        
        
        distance = distance * 0.85

       

        
        input_data = np.array([[distance]])
        fare = model.predict(input_data)[0]

        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("Price Estimated")
            
            st.success(f"{fare[0]:.2f}")

            st.markdown("Distance")
            st.info(f"{distance:.2f} km")

            st.markdown("Vehicle Type")
            st.info(vehicle_type)

            st.markdown("Passengers")
            st.info(passengers)

        
        with col2:
            
            route_coords = res['routes'][0]['geometry']['coordinates']  
            route_latlng = [[coord[1], coord[0]] for coord in route_coords]  
            
            
            center_lat = (lat1 + lat2) / 2
            center_lon = (lon1 + lon2) / 2
            
            
            map_data = {
                "lat1": lat1,
                "lon1": lon1,
                "lat2": lat2,
                "lon2": lon2,
                "center_lat": center_lat,
                "center_lon": center_lon,
                "pickup_place": pickup_place,
                "drop_place": drop_place,
                "distance": distance,
                "route": route_latlng
            }
            
            
            with open("map.html", "r") as f:
                html_content = f.read()
            
            
            html_with_data = f"""
            {html_content}
            <script>
                window.mapData = {json.dumps(map_data)};
                initializeMap(window.mapData);
            </script>
            """
            
            
            st.components.v1.html(html_with_data, height=500)