import streamlit as st
from windwatch.app.utilities import load_folium_map
from windwatch.app.components.map_display import display_folium_map

def show():
    st.header("Bird Sighting Map")
    
    # Get data (cached)
    data = load_folium_map()
    
    # Display map
    display_folium_map(data)
    
    # Add filters if needed
    with st.sidebar:
        st.header("Filters")
        # Add your filters here