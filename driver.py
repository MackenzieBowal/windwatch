from core.map import Map
from config import DATA_DIR
from data_prep.get_data import get_bird_sighting_data, get_wind_speed_data
from data_prep.process_data import process_bird_sighting_data, process_wind_speed_data


bird_proc_path=DATA_DIR+"proc_bird_sighting_data.jsonl"
bird_raw_path=DATA_DIR+"raw_bird_sighting_data.jsonl"

wind_proc_path=DATA_DIR+"proc_wind_speed_data.jsonl"
wind_raw_path=DATA_DIR+"raw_wind_speed_data.tif"

map_path=DATA_DIR+"gdf.geojson"

# get_bird_sighting_data(ebird_species_code='mcclon', output_path=DATA_DIR+"4_raw_bird_sighting_data.jsonl")
# get_wind_speed_data(output_path=raw_path)
process_bird_sighting_data(input_path=DATA_DIR+"4_raw_bird_sighting_data.jsonl", proc_output_path=DATA_DIR+"4_proc_bird_sighting_data.jsonl")
# process_wind_speed_data(input_path=raw_path, proc_output_path=proc_path)

# gdf = Map(coord_range=[49.0000, 52.833333, -114.0000, -110.0000], 
#           grid_size=20000, 
#           bird_data_path=bird_proc_path,
#           wind_speed_data_path=wind_proc_path,
#           )

print("done")
