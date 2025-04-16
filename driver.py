from data_prep.generate_map import generate_map
from config import DATA_DIR
from data_prep.get_data import get_bird_sighting_data
from data_prep.process_data import process_bird_sighting_data
from data_prep.generate_map import generate_map


raw_path=DATA_DIR+"raw_bird_sighting_data.jsonl"
proc_path=DATA_DIR+"proc_bird_sighting_data.jsonl"
map_path=DATA_DIR+"gdf.geojson"

print("Preparing to generate map...")

# get_bird_sighting_data(output_path=raw_path)
# process_bird_sighting_data(input_path=raw_path, proc_output_path=proc_path)
gdf = generate_map(bird_data_path=proc_path, map_output_path=map_path)

print("Map generation complete.")

