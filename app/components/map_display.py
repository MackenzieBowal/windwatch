import streamlit as st
from streamlit_folium import st_folium, folium_static
from windwatch.config import DATA_DIR


def display_folium_map(map):
    """Display a folium map with the provided GeoDataFrame"""
    if map is not None:
        # Use your existing map generation function
        folium_static(map, width=700, height=500)
    else:
        st.warning("No data available to display")

