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
    - bird_risk_gdf: contains the circles around bird observations (only updated if radius changes)
    - wind_speed_gdf: contains the wind speed observation points (shouldn't have to be updated)
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
        self.output_path = output_path
        self.folium_map = None
        self.comName = ""
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.bird_radius = 30000  #3385 # according to Watson 2020

        # Set default coefficients
        self.bird_risk_coefficient = 50 # 1-100
        self.wind_speed_coefficient = 50

        self.__initialize_map(bird_data_path, wind_speed_data_path)

    def calculate_cost_value(self, new_coefficients: dict = {}):
        ''' Calculates the cost value of each grid cell based on the coefficients '''

        for factor in new_coefficients.keys():
            if factor == 'birdRisk':
                self.bird_risk_coefficient = new_coefficients[factor]
            elif factor == 'windSpeed':
                self.wind_speed_coefficient = new_coefficients[factor]

        print(f"bird risk coefficient: {self.bird_risk_coefficient}")
        print(f"wind speed coefficient: {self.wind_speed_coefficient}")

        self.gdf['value'] = (
            self.gdf['windSpeed'] * 1 -
            self.gdf['birdRisk'] * 100
        )

        # Normalize the value column to [0,1]
        self.gdf['value'] = self.scaler.fit_transform(self.gdf['value'].values.reshape(-1, 1)).flatten()
    
        return None
    

    def update_folium_map(self, new_subject: str):
        ''' Changes the folium map subject '''

        # colormap = cm.LinearColormap(
        #     colors=['white', 'yellow', 'red'],
        #     vmin=0,
        #     vmax=1,
        # )

        
        self.folium_map = self.gdf.explore(
            column=new_subject,
            cmap='YlOrRd', 
            legend=True,
            tooltip=True,
            style_kwds={'fillOpacity': 0.5, 'weight': 0, 'color': None},
        )

        return
        
    


    def __update_bird_risk(self):
        ''' Adds a birdRisk column to the Map's gdf based on bird observations '''

        observations = self.bird_risk_gdf
        self.gdf = self.gdf.drop(columns=['birdRisk'])


        # Now we can do a spatial join on observations and self.gdf
        observations_joined = gpd.sjoin(
            observations,
            self.gdf[['geometry']],
            how="inner",
            predicate="intersects"
        )

        sum_bird_risk = (
            observations_joined
            .groupby('index_right')['howMany']
            .sum()
            .rename('birdRisk')
        )

        # Add the sum of bird counts to the self.gdf
        self.gdf = self.gdf.join(sum_bird_risk, how="left")

        self.gdf = self.gdf.fillna({'birdRisk': 0})

        # normalize the column to [0,1]
        self.gdf['birdRisk'] = self.scaler.fit_transform(self.gdf['birdRisk'].values.reshape(-1, 1)).flatten()

        return
    
    def __update_wind_speed(self):
        ''' Adds a windSpeed column to the Map's gdf based on wind speeds '''

        observations = self.wind_speed_gdf
        self.gdf = self.gdf.drop(columns=['windSpeed'])

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
            .groupby('index_right')['windSpeedValue']
            .mean()
            .rename('windSpeed')
        )

        # Add the average wind speeds to the self.gdf
        self.gdf = self.gdf.join(avg_wind_speed, how="left")

        # There might be null values if some cells are a bit outside the region
        # Since they're on the borders, they should have a low wind energy potential value anyway (no one wants to build a wind farm there)
        # Still not the best solution admittedly
        self.gdf['windSpeed'] = self.gdf['windSpeed'].fillna(self.gdf['windSpeed'].min())


        self.gdf['windSpeed'] = self.scaler.fit_transform(self.gdf['windSpeed'].values.reshape(-1, 1)).flatten()

        return


    def __update_resolution(self, new_grid_size: int):
        ''' Updates the grid size of the map '''
        # TODO - implement this
        pass


    def __initialize_map(self, bird_data_path: str, wind_speed_data_path: str):
        '''
        Generates a GeoDataFrame with the following structure:
        
        index | birdRisk | windSpeed | value | pso | geometry
        
        Where the geometry is set to WGS84 coordinates of the grid cell corners (shapely Polygons).
        birdRis, windSpeed, and value are all normalized [1,0].
        pso is 1 for yes, include and 0 for no, exclude.
        '''


        ''' Initialize bird dataframe '''
        data = pd.read_json(bird_data_path, lines=True)
        self.comName = data["comName"][0]

        geometry = [Point(lon, lat) for lon, lat in zip(data['lon'], data['lat'])]
        observations = gpd.GeoDataFrame(
            data[['howMany']],  # Keep the attribute column
            geometry=geometry,
            crs="EPSG:4326"  # WGS84 coordinate reference system
        )

        # Project to UTM CRS
        observations = observations.to_crs(observations.estimate_utm_crs())

        # Set new geometry to circles around each observation instead of points
        observations['geometry'] = observations.buffer(self.bird_radius)

        observations = observations.to_crs("EPSG:4326")  # Project back to WGS84

        self.bird_risk_gdf = observations


        ''' Initialize wind speed dataframe '''
        data = pd.read_json(wind_speed_data_path, lines=True)

        geometry = [Point(lon, lat) for lon, lat in zip(data['lon'], data['lat'])]
        observations = gpd.GeoDataFrame(
            data[['windSpeed']],  # Keep the attribute column
            geometry=geometry,
            crs="EPSG:4326"  # WGS84 coordinate reference system
        )
        observations = observations.rename(columns={'windSpeed': 'windSpeedValue'})

        self.wind_speed_gdf = observations


        ''' Now set up the grid (main dataframe) '''
        # wrap boundary in GeoDataFrame, with WGS84 coordinate reference system
        boundary_gdf = gpd.GeoDataFrame(geometry=[self.boundary], crs="EPSG:4326")
        
        # Project to UTM to generate meters-based grid cells
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

        # Create final grid (in UTM)
        grid_gdf = gpd.GeoDataFrame(geometry=grid_cells, crs=utm_gdf.crs)
        # Convert back to WGS84
        grid_gdf = grid_gdf.to_crs("EPSG:4326")  

        self.gdf = grid_gdf
        self.gdf['birdRisk'] = [0] * len(grid_gdf)
        self.gdf['windSpeed'] = [0] * len(grid_gdf)
        self.gdf['value'] = [0] * len(grid_gdf)

        
        ''' Join all the dataframes together '''
        # update bird risk updates the bird risk column based on the current self.gdf
        self.__update_bird_risk()

        self.__update_wind_speed()

        self.calculate_cost_value()

        
        # Initialize folium map
        self.update_folium_map('value')
        
        # Save gdf to GeoJSON
        if self.output_path:
            self.gdf.to_file(self.output_path, driver="GeoJSON")

        return None
    


    
