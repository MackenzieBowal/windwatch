from ebird.api import get_historic_observations
import os
from dotenv import load_dotenv
from datetime import date, timedelta
import json
import requests
import rasterio

#################################
''' API calls to data sources '''
#################################


def get_bird_sighting_data(common_name: str | list[str] = "Ferruginous Hawk",
                           scientific_name: str | list[str] = "Buteo regalis",
                           ebird_species_code: str | list[str] = "ferhaw",
                           region_code: str | list[str] = "CA-AB",
                           ebird_api_key: str = None,
                           output_path: str = None):
    '''
    Fetch bird sighting data from eBird
    :param common_name:
    :param scientific_name:
    :param ebird_species_code:
    :param ebird_api_key: for now hardcoded with my API key
    :return: A list of observations (dictionaries)
    '''

    def print_data(data: list[dict[str]]) -> None:
        for d in data:
            print(f"{d['comName']}\n"
                    f"\tScientific Name: {d['sciName']}\n"
                    f"\tLat: {d['lat']}, Long: {d['lng']}\n"
                    f"\tDate: {d['obsDt']}\n"
                    f"\tCount: {d['howMany']}",
                    "\n")


    def fetch_by_date(date):
        ''' Returns all the observations of the given species for a specific date, filtering out ones with no count '''
        observations = get_historic_observations(token=ebird_api_key, date=date, area=region_code, detail='full')
        ferhaw_obs = [obs for obs in observations if obs['speciesCode'] == ebird_species_code]
        for obs in ferhaw_obs:
            if 'howMany' not in obs.keys():
                obs['howMany'] = 1
                obs['noCount'] = 1
        return ferhaw_obs


    # TODO: implement multi-species functionality
    if [i for i in [common_name, scientific_name, ebird_species_code] if type(i) is list]:
        return "Multi-species functionality is not implemented yet"
    
    # TODO: Find the species code if not provided (use get_taxonomy())
    if ebird_species_code is None:
        pass

    # Load API key
    if ebird_api_key is None:
        load_dotenv()
        ebird_api_key = os.environ["EBIRD_API_KEY"]

    # Get all sightings by date range
    all_sightings = []

    if not output_path or not output_path.endswith(".jsonl"):
        output_path = "raw_bird_sighting_data.jsonl"

    with open(output_path, "w+") as f:

        # 10 year range from March-Oct 2015 to 2024 (when they're in Alberta)
        # Had to do it this way because the eBird API only allows recent data (past 30 days)
        # Or you can get data from a specific day. Hence the awful loop
        for i in range(0, 10):
            year = 2015 + i
            start_date = date(year, 9, 17)
            end_date = date(year, 10, 31)
            delta = timedelta(days=1)
            current_date = start_date

            while current_date <= end_date:
                current_date += delta
                print(current_date.strftime("%Y-%m-%d") + "\n")
                data = fetch_by_date(current_date)
                print_data(data)
                for obs in data:
                    all_sightings.append(obs)

                    # Save data to file
                    json.dump(obs, f)
                    f.write("\n")

    return all_sightings


def get_wind_speed_data(country: str = "CAN",
                        height: int = 100,
                        output_path: str = None):
    ''' fetch wind speed data from Global Wind Atlas 
    Args:
        country: 3-letter country code (e.g. "CAN" for Canada)
        height: Wind turbine hub height in meters (50, 100, or 200)
    Returns:
    '''

    assert len(country) == 3, "Please enter 3 letter ISO code for country"
    assert height in [10, 50, 100, 150, 200], "Height must be 10, 50, 100, 150, or 200 meters"
    assert output_path.endswith(".tif"), "Data should be saved as a .tif file"

    url = f"https://globalwindatlas.info/api/gis/country/{country}/wind-speed/{height}"
    response = requests.get(url)
    response.raise_for_status()

    # Save to file in binary (preserves geoTIFF bytes apparently)
    if output_path:
        with open(output_path, "wb") as f:
            f.write(response.content)

    # with rasterio.open(output_path) as src:
    #     print("CRS:", src.crs)
    #     print("Bounds:", src.bounds)
    #     print("Width, Height:", src.width, src.height)
    #     band1 = src.read(1)  # read the first (and only) band
    #     print("Array shape:", band1.shape)

    return

''' fetch terrain slope data '''



''' fetch protected areas data '''
