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

    buildings_gdf = gpd.read_file(buildings_geometries_file, mask=roi)
    buildings_gdf = buildings_gdf.explode()
    buildings_gdf = buildings_gdf.reset_index()
    buildings_gdf["id"] = buildings_gdf.index

    return json.loads(buildings_gdf.to_json())


def get_streets_with_traffic(roi_geojson):
    roi = gpd.GeoDataFrame.from_features(roi_geojson["features"], crs="EPSG:4326")

    streets_gdf = gpd.read_file(streets_with_traffic_file, mask=roi)
    streets_gdf = streets_gdf.explode()
    streets_gdf = streets_gdf.reset_index()
    streets_gdf["id"] = streets_gdf.index

    return json.loads(streets_gdf.to_json())
