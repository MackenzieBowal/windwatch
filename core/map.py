import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon, Point
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import branca.colormap as cm



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
    TODO - update_resolution: regenerates the map with a new grid_size
    TODO - update_coefficient: updates the cost function and the map's 'value' attribute
    TODO - find_best_locations: does the PSO to find good locations for a wind farm
    TODO - get gdf index from coordinate
    TODO - The gdfs of each data source should be stored for recalculation with tuning
    - Plus getters
    '''

    def __init__(self, coord_range: list[float], 
                 grid_size: int, 
                 bird_data_path: str, 
                 wind_speed_data_path: str, 
                 output_path = None,  
                 *args, **kwargs):
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
        self.wind_speed_data_path = wind_speed_data_path
        self.output_path = output_path
        self.folium_map = None
        self.comName = ""
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.bird_radius = 3385 # according to Watson 2020

        # Set default coefficients
        self.bird_coefficient = 1

        self.__generate_map()


    def __add_bird_risk(self):
        ''' Adds a birdRisk column to the Map's gdf based on bird observations '''
        # Load bird data
        data = pd.read_json(self.bird_data_path, lines=True)
        self.comName = data["comName"][0]

        geometry = [Point(lon, lat) for lon, lat in zip(data['lon'], data['lat'])]
        observations = gpd.GeoDataFrame(
            data[['howMany']],  # Keep the attribute column
            geometry=geometry,
            crs="EPSG:4326"  # WGS84 coordinate reference system
        )

        # Project to UTM CRS
        observations = observations.to_crs(observations.estimate_utm_crs())


        # TODO: optimize this instead of brute force it hurts
        for i, obs in observations.iterrows():
            point = obs['geometry']
            # Use a circular buffer for better distribution
            circle = point.buffer(self.bird_radius)
            for i, row in self.gdf.iterrows():
                if circle.intersects(row['geometry']):
                    self.gdf.at[i, 'birdRisk'] += obs['howMany']

        print(f"gdf: {self.gdf['birdRisk'].head()}")

        # TODO normalize the column [0,1]

        self.gdf['birdRisk'] = self.scaler.fit_transform(self.gdf['birdRisk'].values.reshape(-1, 1)).flatten()

        return
    
    def __add_wind_speed(self):
        ''' Adds a windSpeed column to the Map's gdf based on wind speeds '''

        data = pd.read_json(self.wind_speed_data_path, lines=True)

        geometry = [Point(lon, lat) for lon, lat in zip(data['lon'], data['lat'])]
        observations = gpd.GeoDataFrame(
            data[['windSpeed']],  # Keep the attribute column
            geometry=geometry,
            crs="EPSG:4326"  # WGS84 coordinate reference system
        )

        # Spatial join to attach each observation to it's grid cell
        observations_joined = gpd.sjoin(
            observations,
            self.gdf[['geometry']],
            how="inner",
            predicate="within"
        )
        
        # Series of average wind speeds, indexed the same as self.gdf
        avg_wind_speed = (
            observations_joined
            .groupby('index_right')['windSpeed']
            .mean()
            .rename('windSpeed')
        )

        # Add the average wind speeds to the ' self.gdf
        self.gdf = self.gdf.join(avg_wind_speed, how="left")

        # There might be null values if some cells are a bit outside the region
        # Since they're on the borders, they should have a low wind energy potential value anyway (no one wants to build a wind farm there)
        # Still not the best solution admittedly
        self.gdf['windSpeed'] = self.gdf['windSpeed'].fillna(self.gdf['windSpeed'].min())

        return





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
        for y in np.arange(ymin, ymax, size):
            for x in np.arange(xmin, xmax, size):
                grid_cells.append(Polygon([
                    (x, y), (x+size, y),
                    (x+size, y+size), (x, y+size)
                ]))

    
        print(f"y-range: {len(np.arange(ymin, ymax, size))}")
        print(f"x-range: {len(np.arange(xmin, xmax, size))}")

        # Create final grid (in UTM)
        grid_gdf = gpd.GeoDataFrame(geometry=grid_cells, crs=utm_gdf.crs)

        self.gdf = grid_gdf
        
        # Set up birdRisk gdf from observations

        grid_gdf['birdRisk'] = [0] * len(grid_gdf)

        # Then update bird risk will update the bird risk column based on the current self.gdf
        # self.__add_bird_risk()

        # Convert back to WGS84
        self.gdf = self.gdf.to_crs("EPSG:4326")  

        # Set up windSpeed gdf from observations
        self.__add_wind_speed() # wind speed is in WGS84


        # Total cost function value for each grid cell
        self.gdf['value'] = [0] * len(grid_gdf)

        colormap = cm.LinearColormap(
            colors=['white', 'yellow', 'red', 'black'],
            index=[0.0, 0.5, 8.7, 10.0],
            vmin=0,
            vmax=10,
            caption='Custom Colormap (0 to 1)'
        )

                
        self.folium_map = self.gdf.explore(
            column='windSpeed',
            cmap='YlOrBr',
            legend=True,
            tooltip=True,
            style_kwds={'fillOpacity': 0.5, 'weight': 0, 'color': None},
        )
        
        # Save gdf to GeoJSON
        if self.output_path:
            self.gdf.to_file(self.output_path, driver="GeoJSON")

        return None
    


    
