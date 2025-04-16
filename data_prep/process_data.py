import pandas as pd
import json


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







