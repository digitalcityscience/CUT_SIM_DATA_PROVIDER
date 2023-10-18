import os
import json

import geopandas as gpd


noise_input_data_file = f"{os.getcwd()}/noise_input_data/noise_input_data.gpkg"


def get_noise_sim_input_for_roi(roi_geojson):
    roi = gpd.GeoDataFrame.from_features(roi_geojson["features"], crs="EPSG:4326")

    noise_input_gdf = gpd.read_file(
        noise_input_data_file,
        mask=roi
    )
    
    return json.loads(noise_input_gdf.to_json())
