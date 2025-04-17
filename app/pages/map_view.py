import streamlit as st
from windwatch.app.utilities import load_folium_map
from windwatch.app.components.map_display import display_folium_map
from windwatch.core.map import Map

def show(map: Map = None):
    print(map.gdf.head())
    # st.header(f"{map.comName} Sighting Map")
    st.header(f"Wind Speed Map")
    
    # Get data (cached)
    data = load_folium_map(map=map)
    
    # Display map
    display_folium_map(data)
    
    # Add filters if needed
    with st.sidebar:
        st.header("Filters")
        # Add your filters here