# SIM DATA PROVIDER - CUT API

## API
Provides a simple http API with 2 endpoints [POST] /buildings and /streets
that provides the noise simulation input for region of interest. 
The region of interest is defined as geojson like dict.

## Data
### Buildings with heights
All groundfloor geometries of Hamburg buildings (from the LOD2 CityGML) and the building_height for each building
`"building_height": 50,
`

### Streets data for noise simulations
**Geometries of streets in EPSG:4326**
**Traffic counts for cars and trucks plus further properties needed for noise sim**

`"max_speed": 50,
"truck_traffic_daily": 1120,
"car_traffic_daily": 26880,
"traffic_settings_adjustable": True,
"road_type": "street"
`


## Create the app_data from public data sources 
use /create_app_data/make_noise_info_from_geoportal_data.py
The simulation input data is derived from publicly availabe data on the Geoportal. 
See source.txt files in ./geoportal_layers 

This script is supposed to be run once in order to create the noise simulation input from the publicly available streets
data on the geoportal. Can be re-run if street data is updated on portal (happens every few years :D ) 

Download the data manually from the geoportal (or the addresses in source.txt files)
and put them into the folders in the "geoportal_layers" dir.
Then run the script
A ./noise_input_data/noise_input_data.gpkg will be created that serves as basis for the app.


