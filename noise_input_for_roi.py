import os
import json
from typing import List

import geopandas as gpd
from shapely.geometry import Polygon


noise_input_data_file = f"{os.getcwd()}/noise_input_data/noise_input_data.gpkg"


def get_noise_sim_input_for_roi(roi_coords: List[List[float]]):
    
    pol = Polygon(roi_coords)
    noise_input_gdf = gpd.read_file(
        noise_input_data_file,
        mask=pol
    )
    
    return json.loads(noise_input_gdf.to_json())
