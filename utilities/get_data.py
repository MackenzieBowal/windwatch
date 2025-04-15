from ebird.api import get_species_observations
import os
from dotenv import load_dotenv


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

    # TODO: implement multi-species functionality
    if [i for i in [common_name, scientific_name, ebird_species_code] if type(i) is list]:
        return "Multi-species functionality is not implemented yet"
    
    # TODO: Find the species code if not provided (use get_taxonomy())
    if ebird_species_code is None:
        pass

    if ebird_api_key is None:
        load_dotenv()
        ebird_api_key = os.environ["EBIRD_API_KEY"]

    observations = get_species_observations(token=ebird_api_key, species=ebird_species_code, area=region_code, back=30)

    return observations


''' fetch wind speed and direction data '''


''' fetch terrain slope data '''



''' fetch protected areas data '''
