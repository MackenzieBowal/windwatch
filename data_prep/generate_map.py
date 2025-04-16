import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon, Point
import pandas as pd


def generate_map(bird_data_path: str,
                    map_output_path: str, 
                    coord_range: list[float] = [49.0000, 52.833333, -114.0000, -110.0000],
                    grid_size: int = 1000):
    
    '''
    grid_size: size of each square in meters

    Generates a GeoDataFrame with the following structure:
    
    index | birdRisk | windSpeed | windDirection | terrainSlope | isProtectedArea | x | y | geometry
    
    Where the geometry is set to WGS84 coordinates.
    '''

    
    lat_min, lat_max, lon_min, lon_max = coord_range

    # Create a boundary polygon from input coordinates (WGS84)
    boundary = Polygon([
        (lon_min, lat_min),
        (lon_max, lat_min),
        (lon_max, lat_max),
        (lon_min, lat_max),
        (lon_min, lat_min)
    ])
    
    # wrap boundary in GeoDataFrame, with WGS84 coordinate reference system
    boundary_gdf = gpd.GeoDataFrame(geometry=[boundary], crs="EPSG:4326")
    
    # Project to UTM CRS
    print(boundary_gdf.estimate_utm_crs())
    utm_gdf = boundary_gdf.to_crs(boundary_gdf.estimate_utm_crs())
    print(utm_gdf.head())

    xmin, ymin, xmax, ymax = utm_gdf.total_bounds

    # Generate grid cells
    grid_cells = []
    for x in np.arange(xmin, xmax, grid_size):
        for y in np.arange(ymin, ymax, grid_size):
            grid_cells.append(Polygon([
                (x, y), (x+grid_size, y),
                (x+grid_size, y+grid_size), (x, y+grid_size)
            ]))
    
    # Create final grid (in UTM)
    grid_gdf = gpd.GeoDataFrame(geometry=grid_cells, crs=utm_gdf.crs)
    
    # Add random values and return in WGS84
    grid_gdf['value'] = np.random.rand(len(grid_gdf))

    # Convert back to WGS84 for display
    final_gdf = grid_gdf.to_crs("EPSG:4326")  
    
    final_gdf.to_file(map_output_path, driver="GeoJSON")

    return final_gdf



    # # extra validation
    # if gdf.crs != "EPSG:4326":
    #     gdf = gdf.to_crs(epsg=4326)

    # # Use GeoDataFrame.explore() to create a Folium map
    # # The 'column' parameter ensures that polygons are color-mapped based on the "Value" attribute.
    # # You can adjust style_kwds as needed.
    # folium_map = gdf.explore(
    #     column="value",
    #     cmap="YlOrRd",
    #     showLegend=True,
    #     k=10,
    #     tiles="CartoDB positron"
    # )

    # print(folium_map)

    # folium.TileLayer("CartoDB positron", show=False).add_to(folium_map)  # use folium to add alternative tiles
    # folium.LayerControl().add_to(folium_map)

    # # Embed the Folium map within Streamlit using streamlit-folium
    # st_folium(folium_map, width=700, height=500)

    ''''''

    # raw_path=DATA_DIR+"raw_bird_sighting_data.jsonl"
    # proc_path=DATA_DIR+"proc_bird_sighting_data.jsonl"
    # map_path=DATA_DIR+"gdf.shp"

    # # get_bird_sighting_data(output_path=raw_path)
    # # process_bird_sighting_data(input_path=raw_path, proc_output_path=proc_path)
    # gdf = generate_map(bird_data_path=proc_path, map_output_path=map_path)
