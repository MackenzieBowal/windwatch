import streamlit as st
from windwatch.app.utilities import load_folium_map
from windwatch.app.components.map_display import display_folium_map
from windwatch.core.map import Map
import numpy as np



def show(map: Map = None):

    # Set up state
    if "prev_bird_slider" not in st.session_state:
        st.session_state.prev_bird_slider = 50

    if "prev_wind_slider" not in st.session_state:
        st.session_state.prev_wind_slider = 50

    if "map_subject" not in st.session_state:
        st.session_state.map_subject = "value"

    if "map_header" not in st.session_state:
        st.session_state.map_header = "Site Value Map"


    st.header(st.session_state.map_header)

    map.update_folium_map(st.session_state.map_subject)
    data = map.folium_map
    display_folium_map(data)
    
    with st.sidebar:
        st.header("Controls")
        
        st.markdown("---")
                
        bird_slider = st.select_slider(
            "Bird Impact Risk",
            options=np.arange(1, 101, 1),
            value=50,
            key="bird_slider"
        )
        
        wind_slider = st.select_slider(
            "Wind Energy Potential",
            options=np.arange(1, 101, 1),
            value=50,
            key="wind_slider"
        )

        if bird_slider != st.session_state.prev_bird_slider:
            st.session_state.prev_bird_slider = bird_slider
            map.calculate_cost_value(new_coefficients={"birdRisk": int(bird_slider)})

        if wind_slider != st.session_state.prev_wind_slider:  
            st.session_state.prev_wind_slider = wind_slider
            map.calculate_cost_value(new_coefficients={"windSpeed": int(wind_slider)})
        
        # Add some space
        st.markdown("##")
        

        selected_layer = st.selectbox(
            "Select map layer",
            ["Site Value", "Bird Risk", "Wind Potential"]
        )

        if selected_layer == "Bird Risk":
            st.session_state.map_subject = "birdRisk"
            st.session_state.map_header = f"{map.comName} Sighting Map"

        elif selected_layer == "Wind Speed":
            st.session_state.map_subject = "windSpeed"
            st.session_state.map_header = "Wind Speed Map"

        elif selected_layer == "Site Value":
            st.session_state.map_subject = "value"
            st.session_state.map_header = "Site Value Map"

        st.markdown("##")

        PSOButton = st.button("Find Best Sites", key="btn_PSO")

        if PSOButton:
            # TODO
            # call function to find PSO
            # update map with new folium map (1's and 0's)
            pass

        
