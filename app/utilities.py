import streamlit as st
import geopandas as gpd
import folium

from windwatch.config import DATA_DIR

@st.cache_data(ttl=21600)  # Cache for 6 hours
def load_base_gdf(gdf_path: str = DATA_DIR+"gdf.geojson") -> gpd.GeoDataFrame:
    """Load processed bird data once, then cache it"""
    gdf = gpd.read_file(gdf_path)
    return gdf


# The map itself can't be cached (pickling is weird apparently)
def load_folium_map(gdf: gpd.GeoDataFrame = None, gdf_path: str = DATA_DIR+"gdf.geojson") -> folium.Map:
    if gdf is None:
        gdf = load_base_gdf(gdf_path)

    m = gdf.explore(
        column="value",
        cmap="YlOrRd",
        showLegend=True,
        k=10,
        tiles="CartoDB positron"
    )
    return m


