from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import List
import json
from pathlib import Path

from api.data import get_buildings_with_heights, get_streets_with_traffic

app = FastAPI()

def get_example_roi_geojson():
    path = Path(__file__).parent / "fixtures/example_roi_input.geojson"
    print(str(path))
    with open(path, "r") as f:
        return json.load(f)

class RegionOfInterest(BaseModel):
    type: str
    features: List[dict]

    class Config:
        schema_extra = {
            "example": get_example_roi_geojson()
        }


@app.post("/buildings/")
def buildings_for_roi(region_of_interest: RegionOfInterest):
    return get_buildings_with_heights(jsonable_encoder(region_of_interest))


@app.post("/streets_data/")
def streets_for_roi(region_of_interest: RegionOfInterest):
    return get_streets_with_traffic(jsonable_encoder(region_of_interest))
