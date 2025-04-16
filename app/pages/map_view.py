import streamlit as st
from windwatch.app.utilities import load_folium_map
from windwatch.app.components.map_display import display_folium_map
from windwatch.core.map import Map

def show(map: Map = None):
    st.header("Bird Sighting Map")
    
    # Get data (cached)
    data = load_folium_map(map=map)

    print(f"Data loaded: {data}")
    
    # Display map
    display_folium_map(data)
    
    # Add filters if needed
    with st.sidebar:
        st.header("Filters")
        # Add your filters here