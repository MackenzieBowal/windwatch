import pandas as pd
import json


def process_bird_sighting_data(file_path, file_type, data_type=None):
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

    try:
        # Load the data based on file type
        if file_type == 'csv':
            data = pd.read_csv(file_path)
        elif file_type == 'json':
            with open(file_path, 'r') as f:
                json_data = json.load(f)
            data = pd.DataFrame(json_data)
        else:
            raise ValueError("Unsupported file type. Use 'csv' or 'json'.")


    except Exception as e:
        print(f"Error processing data: {e}")
        return None
    
    # Filter data:
    # - Only keep observations with Lat, Long, Date, and Count attributes
    # - Lat and Long should be within area used by Wellicome

    
    

    return data
