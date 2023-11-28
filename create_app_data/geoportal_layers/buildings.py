from pathlib import Path
import geopandas as gpd
from matplotlib import pyplot as plt

# read file
blds_path = Path(__file__).parent.parent / "geoportal_layers/buildings_inspire_alkis/buildings.gml"
buildings_raw = gpd.read_file(blds_path, driver='GML', layer="Building", engine='pyogrio', use_arrow=True)

# set building height bas on number of floors
buildings_raw["numberOfFloorsAboveGround"] = buildings_raw["numberOfFloorsAboveGround"].fillna(1)  # min 1 floor
buildings_raw["building_height"] = buildings_raw["numberOfFloorsAboveGround"] * 3  # assume 3m per floor

# drop any features that are not (Multi)Polygons
buildings = buildings_raw[buildings_raw.geometry.type.isin(["MultiPolygon", "Polygon"])]
# print(f"geom types: {buildings.geom_type.unique()}")
# print(buildings["building_height"].describe())

# clean unnecessary cols
cols_to_keep = ["geometry", "building_height"]
cols_to_delete = list(set(list(buildings.columns)) - set(cols_to_keep))
buildings = buildings.drop(columns=cols_to_delete)

# reproject to WGS84
buildings = buildings.set_crs("EPSG:25832", allow_override=True)
buildings = buildings.to_crs("EPSG:4326")

# export file
buildings.to_file("buildings_with_heights.gpkg", driver="GPKG")


# plot
# buildings_raw.plot(column='building_height', legend=True)
# plt.show()