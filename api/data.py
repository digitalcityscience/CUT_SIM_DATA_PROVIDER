import json
from pathlib import Path

import geopandas as gpd

buildings_geometries_file = (
    Path(__file__).parent.parent / "app_data/buildings_data/buildings_with_heights.gpkg"
)
streets_with_traffic_file = (
    Path(__file__).parent.parent / "app_data/streets_data/streets_with_traffic.gpkg"
)


def get_buildings_with_heights(roi_geojson):
    roi = gpd.GeoDataFrame.from_features(roi_geojson["features"], crs="EPSG:4326")

    noise_input_gdf = gpd.read_file(buildings_geometries_file, mask=roi)

    return json.loads(noise_input_gdf.to_json())


def get_streets_with_traffic(roi_geojson):
    roi = gpd.GeoDataFrame.from_features(roi_geojson["features"], crs="EPSG:4326")

    noise_input_gdf = gpd.read_file(streets_with_traffic_file, mask=roi)

    return json.loads(noise_input_gdf.to_json())
