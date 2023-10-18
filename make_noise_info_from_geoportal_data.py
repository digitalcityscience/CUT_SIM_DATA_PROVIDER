import os
import geopandas as gpd
import pandas as pd
import re
from typing import Optional

"""
This script is supposed to be run once in order to create the noise simulation input from the publicly available streets
data on the geoportal. Can be re-run if street data is updated on portal (happens every few years :D ) 
Download the data from the geoportal and put it into the folders in the "geoportal_layers" dir.
Lots of duplications in the code. However the input data varies at different points slighty, that would make a 
more streamlined code with central functions quite hard to keep concise. 
Script runs only once anyway. For now I'll leave it like this.
"""


def read_file_as_gdf(file_path: str, force_crs_to: Optional[str] = None):
    gdf = gpd.read_file(file_path)
    if force_crs_to:
        gdf = gdf.set_crs(force_crs_to, allow_override=True)

    gdf = gdf[gdf.geometry.is_valid]

    return gdf


def extract_residential_streets_and_motorways_to_files():
    """
    the geoportal dataset strategisches_strassennetz does not specify the street type as a property
    more specific than "motorway" and "street"
    however other files with matching properties and geometries (exactly??) are published and contain only
    main streets and district streets. Properties can be used to create a unique identifier.
    Substract main, district streets and motorways from all streets to get the remaining residential streets.
    """
    all_streets = read_file_as_gdf(
        "geoportal_layers/strategisches_strassennetz_json/app:strategisches_strassennetz_EPSG:25832.json",
        "EPSG:25832"
    )

    motorways_only = all_streets[all_streets["strassenname"].str.contains("BAB")]
    motorways_only.to_file(
        "geoportal_layers/strategisches_strassennetz_json/motorways_EPSG:25832.gpkg",
        driver="GPKG",
    )

    # continue with all streets without motorways to filter down to residential streets only
    all_streets = all_streets[~all_streets["strassenname"].str.contains("BAB")]
    main_streets = read_file_as_gdf(
        "geoportal_layers/hauptverkehrsstrassen/app:hauptverkehrsstrassen_EPSG:25832.json",
        "EPSG:25832"
    )
    district_streets = read_file_as_gdf(
        "geoportal_layers/bezirksstrassen/app:bezirksstrassen_EPSG:25832.json",
        "EPSG:25832"
    )

    # Creating a unique key in each DataFrame
    for gdf in [all_streets, main_streets, district_streets]:
        gdf['unique_key'] = gdf['strassenschluessel'].astype(str) + gdf['von_station'].astype(str) + \
                            gdf['bis_station'].astype(str)

    all_streets['is_in_others'] = all_streets['unique_key'].isin(main_streets['unique_key']) | all_streets[
        'unique_key'].isin(district_streets['unique_key'])

    residential_streets = all_streets[~all_streets["is_in_others"]]
    residential_streets.to_file(
        "geoportal_layers/strategisches_strassennetz_json/residential_streets_EPSG:25832.gpkg",
        driver="GPKG"
    )


def extract_max_speed(max_speed_info):
    # Convert to string
    str_value = str(max_speed_info)

    # Use regex to find the int pattern
    match = re.search(r'(\d+)', str_value)

    # If found, return the float, otherwise return None
    return float(match[0]) if match else 50


def make_noise_data_for_main_streets():
    TRAFFIC_COUNTS_JSON_STREETS = (
        f"{os.getcwd()}/geoportal_layers/verkehrsmengen_json/de_hh_up:verkehrsmengen_dtv_hvs_2019_EPSG:25832.json"
    )

    traffic_counts_gdf = read_file_as_gdf(TRAFFIC_COUNTS_JSON_STREETS, "EPSG:25832")
    main_streets_gdf = gpd.read_file(
        "geoportal_layers/hauptverkehrsstrassen/app:hauptverkehrsstrassen_EPSG:25832.json",
        "EPSG:25832"
    )

    # the traffic counts gdf has slightly offset geometries from the main_streets geometries. Match these by nearest.
    traffic_counts_gdf["geometry"] = traffic_counts_gdf["geometry"].centroid
    main_streets_gdf = main_streets_gdf.sjoin_nearest(traffic_counts_gdf, how="inner")

    # extract first integer from strings like '30 km/h (Mo-Fr 6-19 h, sonst 50km/h)|50 km/h',
    # returns NaN for str not starting with a number
    main_streets_gdf["max_speed"] = main_streets_gdf["geschwindigkeit"].apply(lambda x: extract_max_speed(x))

    # add traffic values
    main_streets_gdf["truck_traffic_daily"] = round(main_streets_gdf["dtv"] * (main_streets_gdf["sv"] / 100))
    main_streets_gdf["car_traffic_daily"] = round(main_streets_gdf["dtv"] - main_streets_gdf["truck_traffic_daily"])

    # add fixed settings
    main_streets_gdf["traffic_settings_adjustable"] = True
    main_streets_gdf["road_type"] = "street"  # fixed

    # drop all cols unncessary for noise
    cols_to_keep = ["geometry", "max_speed", "truck_traffic_daily", "car_traffic_daily", "traffic_settings_adjustable",
                    "road_type"]
    cols_to_drop = list(set(list(main_streets_gdf.columns)) - set(cols_to_keep))
    main_streets_gdf = main_streets_gdf.drop(columns=cols_to_drop)

    # reproject to EPSG:4326
    main_streets_gdf = main_streets_gdf.to_crs("EPSG:4326")

    return main_streets_gdf


def make_noise_data_for_motorways():
    TRAFFIC_COUNTS_JSON_MOTORWAYS = (
        f"{os.getcwd()}/geoportal_layers/verkehrsmengen_json/de_hh_up:verkehrsmengen_dtv_hvs_2019_EPSG:25832.json"
    )
    traffic_counts_gdf = gpd.read_file(TRAFFIC_COUNTS_JSON_MOTORWAYS, "EPSG:25832")

    motorways = read_file_as_gdf(
        "geoportal_layers/strategisches_strassennetz_json/app:motorways_EPSG:25832.json",
        "EPSG:25832"
    )

    # the traffic counts gdf has slightly offset geometries from the main_streets geometries. Match these by nearest.
    traffic_counts_gdf["geometry"] = traffic_counts_gdf["geometry"].centroid
    motorways = motorways.sjoin_nearest(traffic_counts_gdf, how="inner")

    # extract first integer from strings like '30 km/h (Mo-Fr 6-19 h, sonst 50km/h)|50 km/h',
    # returns NaN for str not starting with a number
    motorways["max_speed"] = 90  # real max_speed is variable

    # add traffic values
    motorways["truck_traffic_daily"] = round(motorways["dtv"] * (motorways["sv"] / 100))
    motorways["car_traffic_daily"] = round(motorways["dtv"] - motorways["truck_traffic_daily"])

    # add fixed settings
    motorways["traffic_settings_adjustable"] = False
    motorways["road_type"] = "street"  # fixed only other option is "railway"

    # drop all cols unncessary for noise
    cols_to_keep = ["geometry", "max_speed", "truck_traffic_daily", "car_traffic_daily", "traffic_settings_adjustable",
                    "road_type"]
    cols_to_drop = list(set(list(motorways.columns)) - set(cols_to_keep))
    motorways = motorways.drop(columns=cols_to_drop)

    # reproject to EPSG:4326
    motorways = motorways.to_crs("EPSG:4326")

    return motorways


def make_noise_data_for_district_streets():

    district_streets_gdf = read_file_as_gdf("geoportal_layers/bezirksstrassen/app:bezirksstrassen_EPSG:4326.json")

    # extract first integer from strings like '30 km/h (Mo-Fr 6-19 h, sonst 50km/h)|50 km/h',
    # returns NaN for str not starting with a number
    district_streets_gdf["max_speed"] = district_streets_gdf["geschwindigkeit"].apply(lambda x: extract_max_speed(x))

    """ 
    add traffic values
    # standard values for district streets according to UBA , p. 32, Tabelle 3.1
    # https: // www.umweltbundesamt.de / sites / default / files / medien / publikation / long / 1933.
    pdf
    dtv = 300 
    percentage trucks = 6%
    """
    district_streets_gdf["truck_traffic_daily"] = round(300 * 0.06)
    district_streets_gdf["car_traffic_daily"] = round(300 - district_streets_gdf["truck_traffic_daily"])

    # add fixed settings
    district_streets_gdf["traffic_settings_adjustable"] = True
    district_streets_gdf["road_type"] = "street"  # fixed

    # drop all cols unncessary for noise
    cols_to_keep = ["geometry", "max_speed", "truck_traffic_daily", "car_traffic_daily", "traffic_settings_adjustable",
                    "road_type"]
    cols_to_drop = list(set(list(district_streets_gdf.columns)) - set(cols_to_keep))
    district_streets_gdf = district_streets_gdf.drop(columns=cols_to_drop)

    return district_streets_gdf


def make_noise_data_for_residential_streets():

    residential_streets_gdf= read_file_as_gdf(
        "geoportal_layers/strategisches_strassennetz_json/residential_streets_EPSG:25832.gpkg",
        "EPSG:25832"
    )

    # extract first integer from strings like '30 km/h (Mo-Fr 6-19 h, sonst 50km/h)|50 km/h',
    # returns NaN for str not starting with a number
    residential_streets_gdf["max_speed"] = residential_streets_gdf["geschwindigkeit"].apply(lambda x: extract_max_speed(x))

    """ 
    add traffic values
    # standard values for district streets according to UBA , p. 32, Tabelle 3.1
    # https: // www.umweltbundesamt.de / sites / default / files / medien / publikation / long / 1933.
    pdf
    dtv = 100 
    percentage trucks = 3%
    """
    residential_streets_gdf["truck_traffic_daily"] = round(100 * 0.03)
    residential_streets_gdf["car_traffic_daily"] = round(100 - residential_streets_gdf["truck_traffic_daily"])

    # add fixed settings
    residential_streets_gdf["traffic_settings_adjustable"] = True
    residential_streets_gdf["road_type"] = "street"  # fixed

    # drop all cols unncessary for noise
    cols_to_keep = ["geometry", "max_speed", "truck_traffic_daily", "car_traffic_daily", "traffic_settings_adjustable",
                    "road_type"]
    cols_to_drop = list(set(list(residential_streets_gdf.columns)) - set(cols_to_keep))
    residential_streets_gdf = residential_streets_gdf.drop(columns=cols_to_drop)

    # reproject to EPSG:4326
    residential_streets_gdf = residential_streets_gdf.to_crs("EPSG:4326")

    return residential_streets_gdf


if __name__ == "__main__":

    # extract residential streets from geoportal data.
    extract_residential_streets_and_motorways_to_files()

    # make noise input data
    print("motorways")
    motorways_gdf = make_noise_data_for_motorways()
    print("residential streets")
    residential = make_noise_data_for_residential_streets()
    print("district streets")
    district = make_noise_data_for_district_streets()
    print("main streets")
    main = make_noise_data_for_main_streets()

    # TODO traffic counts to railways

    all_input = pd.concat([motorways_gdf, residential, district, main])
    all_input.to_file("noise_input_data/noise_input_data.gpkg", driver="GPKG")






