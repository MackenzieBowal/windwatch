import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
import json
import rasterio
from rasterio.mask import mask
from shapely.geometry import box, mapping, Polygon, Point

import numpy as np

from rasterio.transform import xy
from rasterio.enums import Resampling
from rasterio.transform import from_origin



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
    
    ''' Expects input .tif file, processes the data, saves it and returns the final dataframe. 
    The final dataframe will contain (lat, lon, wind_speed) in the given coord_range, with 1km resolution.
    '''


    # Determine UTM zone from avg longitude/latitude
    lat_min, lat_max, lon_min, lon_max = coord_range


    # Don't need this anymore :'(

    # utm_zone = int(((lon_max + lon_min)/2 + 180) / 6) + 1
    # print(f"{utm_zone=}")

    # if (lat_max + lat_min) / 2 >= 0:
    #     utm_crs = f"EPSG:326{utm_zone}" # Northern hemisphere
    # else:
    #     utm_crs = f"EPSG:327{utm_zone}" # Southern hemisphere

    # print(f"{utm_crs=}")


    # Load raw data
    raw_dataset = rasterio.open(input_path)

    # print(f"{dataset.crs=}")
    # print(f"{dataset.bounds=}")
    # print(f"{dataset.width=}")
    # print(f"{dataset.height=}")
    # band1 = dataset.read(1)
    # print(f"{band1=}")
    # print(f"num nans: {np.count_nonzero(np.isnan(band1))}") # About a third are nan (ocean)

    bbox = box(lon_min, lat_min, lon_max, lat_max)
    geo = [mapping(bbox)]

    out_image, out_transform = mask(raw_dataset, geo, crop=True)
    out_meta = raw_dataset.meta.copy()

    out_meta.update({
        "driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform
    })

    raw_dataset.close()

    with rasterio.open("temp.tif", 'w', **out_meta) as dest:
        dest.write(out_image)


    cropped_dataset = rasterio.open("temp.tif", "r+")

    band = cropped_dataset.read(1)

    # replace nans with 0
    band[np.isnan(band)] = 0
    cropped_dataset.write(band, 1)
    

    desired_res = 0.01 # Hardcoded 0.01 degree resolution, approx 1km

    # Calculate new dimensions

    width = int((cropped_dataset.bounds.right - cropped_dataset.bounds.left) / desired_res)
    height = int((cropped_dataset.bounds.top - cropped_dataset.bounds.bottom) / desired_res)

    transform = from_origin(cropped_dataset.bounds.left, cropped_dataset.bounds.top, desired_res, desired_res)

    # Resample data
    data = cropped_dataset.read(
        out_shape=(cropped_dataset.count, height, width),
        resampling=Resampling.nearest
    )

    # Update metadata
    profile = cropped_dataset.profile
    profile.update({
        'transform': transform,
        'width': width,
        'height': height
    })

    # Now we have the final raster dataset. Save lat, lon, and windSpeed values to a jsonl file (consistent with bird data)
    # Also save the processed raster data to a new file
    with rasterio.open(proc_output_path, 'r+', **profile) as final_dataset:
        final_dataset.write(data)

        transform = final_dataset.transform

        print(f"Data shape: {data.shape}")

        # Create geojson from processed raster data

        rows, cols = data.shape
        row_indices, col_indices = np.meshgrid(np.arange(rows), np.arange(cols), indexing='ij')
        flat_rows = row_indices.flatten()
        flat_cols = col_indices.flatten()

        xs, ys = rasterio.transform.xy(transform, flat_rows, flat_cols)

        flat_data = data.flatten()

        df = pd.DataFrame({
            'lat': ys,
            'lon': xs,
            'windSpeed': flat_data
        })

        df.to_json(f"{proc_output_path.split(".")[0]}.jsonl", orient='records', lines=True)






    # x, y = xy(cropped_dataset.transform, 1, 0)
    # print(f"{x=}, {y=}")

    # x_res, y_res = cropped_dataset.res
    # print(f"{x_res=}, {y_res=}")



    return




