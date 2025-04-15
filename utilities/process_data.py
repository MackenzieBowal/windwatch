import pandas as pd
import json
from pyproj import Proj, Transformer
import geopandas as gpd


def proc_bird_sighting_data(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Reads a CSV or JSON file, processes the data, and returns a cleaned DataFrame.
    """

    # Load raw data (should be unfiltered, unchanged from eBird API)

    def print_data(data: list[dict[str]]) -> None:
        for d in data:
            print(f"{d['comName']}\n"
                    f"\tScientific Name: {d['sciName']}\n"
                    f"\tLat: {d['lat']}, Long: {d['lng']}\n"
                    f"\tDate: {d['obsDt']}\n"
                    f"\tCount: {d['howMany']}",
                    "\n")

    # Load data
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

    # TODO: Separate obsDt into date and time (will mostly use date)

    # Filter for area used by Wellicome
    # Coordinate boundaries:
    # NW: 52.833333, -114.000000
    # SW: 49.0000, -114.0000
    # NE: 52.833333, -110.0000
    # SE: 49.0000, -110.0000

    lat_min = 49.0000
    lat_max = 52.833333
    lon_min = -114.0000
    lon_max = -110.0000

    proc_df = proc_df[
        (proc_df["lat"] >= lat_min) & (proc_df["lat"] <= lat_max) &
        (proc_df["lon"] >= lon_min) & (proc_df["lon"] <= lon_max)
    ]
    
    # Save to file
    proc_df.to_json(output_path, orient="records", lines=True)

    return proc_df




