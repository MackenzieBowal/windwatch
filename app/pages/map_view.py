import streamlit as st
from windwatch.app.utilities import load_folium_map
from windwatch.app.components.map_display import display_folium_map
from windwatch.core.map import Map

if "map_subject" not in st.session_state:
    st.session_state.map_subject = "value"

if "map_header" not in st.session_state:
    st.session_state.map_header = "WFSS Value Map"

def show(map: Map = None):
    # print(map.gdf.head())
    st.header(st.session_state.map_header)

    map.change_map_subject(st.session_state.map_subject)
    data = map.folium_map
    display_folium_map(data)
    
    with st.sidebar:
        st.header("Controls")
        
        st.markdown("---")
                
        bird_slider = st.select_slider(
            "Bird Impact Risk",
            options=[1, 2, 3, 4, 5],
            value=3,
            key="bird_slider"
        )
        
        wind_slider = st.select_slider(
            "Wind Energy Potential",
            options=[1, 2, 3, 4, 5],
            value=3,
            key="wind_slider"
        )
        
        # Add some space
        st.markdown("##")
        
        # col1, col2, col3 = st.columns(3)
        
        # with col1:
        #     birdButton = st.button("Bird Layer", key="btn_bird")
        
        # with col2:
        #     windButton = st.button("Wind Layer", key="btn_wind")
        
        # with col3:
        #     valueButton = st.button("Value Layer", key="btn_value")

        selected_layer = st.selectbox(
            "Select map layer",
            ["Bird Sightings", "Wind Speed", "Best Sites"]
        )

        if selected_layer == "Bird Sightings":
            st.session_state.map_subject = "birdRisk"
            st.session_state.map_header = f"{map.comName} Sighting Map"

        elif selected_layer == "Wind Speed":
            st.session_state.map_subject = "windSpeed"
            st.session_state.map_header = "Wind Speed Map"

        elif selected_layer == "Best Sites":
            st.session_state.map_subject = "value"
            st.session_state.map_header = "WFSS Value Map"

        st.markdown("##")

        PSOButton = st.button("Find Best Sites", key="btn_PSO")

        
        # # Handle button clicks
        # if birdButton:
        #     st.session_state.map_subject = "birdRisk"
        #     st.session_state.map_header = f"{map.comName} Sighting Map"   
        #     st.rerun()
            
        # if windButton:
        #     st.session_state.map_subject = "windSpeed"
        #     st.session_state.map_header = "Wind Speed Map"
        #     st.rerun()
            
        # if valueButton:
        #     st.session_state.map_subject = "value"
        #     st.session_state.map_header = "WFSS Value Map"
        #     st.rerun()
