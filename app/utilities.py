import streamlit as st
import geopandas as gpd
import folium

from windwatch.config import DATA_DIR

@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_base_gdf(gdf_path: str = DATA_DIR+"gdf.geojson") -> gpd.GeoDataFrame:
    """Load processed bird data once, then cache it"""
    gdf = gpd.read_file(gdf_path)
    return gdf

@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_folium_map(gdf_path: str = DATA_DIR+"gdf.geojson") -> folium.Map:
    gdf = load_base_gdf(gdf_path)
    m = gdf.explore(
        column="value",
        cmap="YlOrRd",
        showLegend=True,
        k=10,
        tiles="CartoDB positron"
    )
    return m


