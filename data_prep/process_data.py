import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
import json
import rasterio
from rasterio.mask import mask
from shapely.geometry import box, mapping
import numpy as np

from rasterio.transform import xy



from rasterio.io import MemoryFile



def process_bird_sighting_data(input_path: str, 
                               proc_output_path: str, 
                               coord_range: list[float] = [49.0000, 52.833333, -114.0000, -110.0000]
                               ) -> pd.DataFrame:
    """
    Expects input .jsonl file, processes the data, saves it and returns the final dataframe.
    """

    # Load raw data
    try:
        df = pd.read_json(input_path, lines=True)
    except:
        print("Error loading file")
        return
    
    # Fill Nans with 0
    df["noCount"] = df["noCount"].fillna(0).astype(int)

    # Keep only necessary attributes
    required_attrs = {"speciesCode", "comName", "sciName", "obsDt", "howMany", "noCount", "lat", "lng"}

    for idx, row in df.iterrows():
        assert required_attrs.issubset(row.keys()), f"Missing keys in row {idx}: {row.to_dict()}"

    proc_df = df[list(required_attrs)]

    # Rename "lng" to "lon" for compatibility with streamlit
    proc_df = proc_df.rename(columns={"lng": "lon"})

    # optional TODO: Separate obsDt into date and time (will mostly use date)

    # Filter for area used by Wellicome
    # Coordinate boundaries:
    # NW: 52.833333, -114.000000
    # SW: 49.0000, -114.0000
    # NE: 52.833333, -110.0000
    # SE: 49.0000, -110.0000

    lat_min, lat_max, lon_min, lon_max = coord_range

    proc_df = proc_df[
        (proc_df["lat"] >= lat_min) & (proc_df["lat"] <= lat_max) &
        (proc_df["lon"] >= lon_min) & (proc_df["lon"] <= lon_max)
    ]
    
    # Save processed dataframe to file
    proc_df.to_json(proc_output_path, orient="records", lines=True)

    return proc_df


def process_wind_speed_data(input_path: str,
                            proc_output_path: str = None,
                            coord_range: list[float] = [49.0000, 52.833333, -114.0000, -110.0000]
                            ) -> pd.DataFrame:
    
    ''' Expects input .tif file, processes the data, saves it and returns the final dataframe. '''

    # # Load raw data
    # raw_dataset = rasterio.open(input_path)

    # # print(f"{dataset.crs=}")
    # # print(f"{dataset.bounds=}")
    # # print(f"{dataset.width=}")
    # # print(f"{dataset.height=}")
    # # band1 = dataset.read(1)
    # # print(f"{band1=}")
    # # print(f"num nans: {np.count_nonzero(np.isnan(band1))}") # About a third are nan (ocean)


    # # Create a new dataset masking for relevant area
    # lat_min, lat_max, lon_min, lon_max = coord_range

    

    # bbox = box(lon_min, lat_min, lon_max, lat_max)
    # geo = [mapping(bbox)]

    # out_image, out_transform = mask(raw_dataset, geo, crop=True)
    # out_meta = raw_dataset.meta.copy()

    # out_meta.update({
    #     "driver": "GTiff",
    #     "height": out_image.shape[1],
    #     "width": out_image.shape[2],
    #     "transform": out_transform
    # })

    # raw_dataset.close()

    # with rasterio.open(proc_output_path, 'w', **out_meta) as dest:
    #     dest.write(out_image)


    cropped_dataset = rasterio.open(proc_output_path)

    # print(f"{cropped_dataset.crs=}")
    # print(f"{cropped_dataset.bounds=}")
    # print(f"{cropped_dataset.width=}")
    # print(f"{cropped_dataset.height=}")
    band = cropped_dataset.read(1)
    print(f"{band=}")
    print(f"num nans: {np.count_nonzero(np.isnan(band))}")

    x, y = xy(cropped_dataset.transform, 1, 0)
    print(f"{x=}, {y=}")

    x_res, y_res = cropped_dataset.res
    print(f"{x_res=}, {y_res=}")



    return




