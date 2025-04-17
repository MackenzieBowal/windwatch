from core.map import Map
from config import DATA_DIR
from data_prep.get_data import get_bird_sighting_data, get_wind_speed_data
from data_prep.process_data import process_bird_sighting_data, process_wind_speed_data


proc_path=DATA_DIR+"proc_wind_speed_data.tif"
raw_path=DATA_DIR+"raw_wind_speed_data.tif"
# raw_path=DATA_DIR+"alberta_rawwspd_100m.tif"
map_path=DATA_DIR+"gdf.geojson"

# get_bird_sighting_data(output_path=raw_path)
# get_wind_speed_data(output_path=raw_path)
process_wind_speed_data(input_path=raw_path, proc_output_path=proc_path)
# process_bird_sighting_data(input_path=raw_path, proc_output_path=proc_path)
# gdf = Map(coord_range=[49.0000, 52.833333, -114.0000, -110.0000], grid_size=20000, bird_data_path=proc_path)


print("done")
