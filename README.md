# SIM DATA PROVIDER - CUT API

## API
Provides a simple http API with one endpoint [POST] /noise_sim_input
that provides the noise simulation input for region of interest. 
The region of interest is defined as geojson like dict.


## Streets data for noise simulations
**Geometries of streets in EPSG:4326**
**Traffic counts for cars and trucks plus further properties needed for noise sim**

`"max_speed": 50,
"truck_traffic_daily": 1120,
"car_traffic_daily": 26880,
"traffic_settings_adjustable": True,
"road_type": "street"
`


## make_noise_info_from_geoportal_data.py
The simulation input data is derived from publicly availabe data on the Geoportal. 
See source.txt files in ./geoportal_layers 

This script is supposed to be run once in order to create the noise simulation input from the publicly available streets
data on the geoportal. Can be re-run if street data is updated on portal (happens every few years :D ) 

Download the data manually from the geoportal (or the addresses in source.txt files)
and put them into the folders in the "geoportal_layers" dir.
Then run the script
A ./noise_input_data/noise_input_data.gpkg will be created that serves as basis for the app.


