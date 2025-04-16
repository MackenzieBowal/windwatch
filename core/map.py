import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon, Point
import pandas as pd


class Map:
    ''' Wrapper for a GeoDataFrame representing the search space '''

    ''' 
    attributes 
    - gdf: GeoDataFrame itself
    - coord_range: list of coordinates [lat_min, lat_max, lon_min, lon_max]
    - boundary: shapely polygon representing the outside edges/corners
    - grid_size: side length of each square in meters
    - bird_data_path: path to the bird data
    - output_path: path to store the output GeoDataFrame
    - folium: folium map object

    methods
    - __init__: constructor
    - __generate_map: generates the initial map from coordinates and data
    - update_resolution: regenerates the map with a new grid_size
    - update_coefficient: updates the cost function and the map's 'value' attribute
    - find_best_locations: does the PSO to find good locations for a wind farm
    - Plus getters
    '''

    def __init__(self, coord_range: list[float], grid_size: int, bird_data_path: str, output_path,  *args, **kwargs):
        # Generates a GeoDataFrame from boundary coordinates, grid size, data, and 
        self.coord_range = coord_range
        self.lat_min, self.lat_max, self.lon_min, self.lon_max = coord_range
        self.boundary = Polygon([
            (self.lon_max, self.lat_min),
            (self.lon_min, self.lat_min),
            (self.lon_max, self.lat_max),
            (self.lon_min, self.lat_max),
            (self.lon_min, self.lat_min)
        ])
        self.grid_size = grid_size
        self.bird_data_path = bird_data_path
        self.output_path = output_path
        self.folium_map = None

        # Set default coefficients
        self.bird_coefficient = 1

        self.gdf = self.__generate_map()

    def __generate_map(self):
        '''
        Generates a GeoDataFrame with the following structure:
        
        index | birdRisk | windSpeed | windDirection | terrainSlope | isProtectedArea | geometry
        
        Where the geometry is set to WGS84 coordinates.
        '''

        # wrap boundary in GeoDataFrame, with WGS84 coordinate reference system
        boundary_gdf = gpd.GeoDataFrame(geometry=[self.boundary], crs="EPSG:4326")
        
        # Project to UTM CRS
        utm_gdf = boundary_gdf.to_crs(boundary_gdf.estimate_utm_crs())
        xmin, ymin, xmax, ymax = utm_gdf.total_bounds

        # Generate grid cells
        grid_cells = []
        size = self.grid_size
        for x in np.arange(xmin, xmax, size):
            for y in np.arange(ymin, ymax, size):
                grid_cells.append(Polygon([
                    (x, y), (x+size, y),
                    (x+size, y+size), (x, y+size)
                ]))

    
        # Create final grid (in UTM)
        grid_gdf = gpd.GeoDataFrame(geometry=grid_cells, crs=utm_gdf.crs)
        
        # Add random values and return in WGS84
        grid_gdf['value'] = np.random.rand(len(grid_gdf))

        # Convert back to WGS84 for display
        final_gdf = grid_gdf.to_crs("EPSG:4326")  
        
        self.gdf = final_gdf
        self.folium_map = final_gdf.explore(
            column='value',
            cmap='viridis',
            legend=True,
            tooltip=True,
            name="Bird Sighting Map",
            style_kwds={'fillOpacity': 0.5}
        )
        
        # Save gdf to GeoJSON
        if self.output_path:
            final_gdf.to_file(self.output_path, driver="GeoJSON")

        return final_gdf
    
    def get_map(self):
        '''
        Returns the GeoDataFrame
        '''
        return self.folium



    
