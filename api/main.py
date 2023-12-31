import json
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from api.data import get_buildings_with_heights, get_streets_with_traffic

app = FastAPI()


origins = [
    # "http://localhost",
    # "http://localhost:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_example_roi_geojson():
    path = Path(__file__).parent / "fixtures/example_roi_input.geojson"
    with open(path, "r") as f:
        return json.load(f)


class RegionOfInterest(BaseModel):
    type: str
    features: List[dict]

    class Config:
        schema_extra = {"example": get_example_roi_geojson()}


@app.post("/buildings/")
def buildings_for_roi(region_of_interest: RegionOfInterest):
    return get_buildings_with_heights(jsonable_encoder(region_of_interest))


@app.post("/streets/")
def streets_for_roi(region_of_interest: RegionOfInterest):
    return get_streets_with_traffic(jsonable_encoder(region_of_interest))
