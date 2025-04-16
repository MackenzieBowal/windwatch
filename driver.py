from core.map import Map
from config import DATA_DIR
from data_prep.get_data import get_bird_sighting_data
from data_prep.process_data import process_bird_sighting_data


raw_path=DATA_DIR+"raw_bird_sighting_data.jsonl"
proc_path=DATA_DIR+"proc_bird_sighting_data.jsonl"
map_path=DATA_DIR+"gdf.geojson"

print("Preparing to generate map...")

# get_bird_sighting_data(output_path=raw_path)
# process_bird_sighting_data(input_path=raw_path, proc_output_path=proc_path)
gdf = Map(coord_range=[49.0000, 52.833333, -114.0000, -110.0000], grid_size=20000, bird_data_path=proc_path)



print("Map generation complete.")

