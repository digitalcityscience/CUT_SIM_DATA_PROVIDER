from fastapi import FastAPI, HTTPException
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import List

from fixtures.example_input import example_roi_geojson
from noise_input_for_roi import get_noise_sim_input_for_roi

app = FastAPI()


class RegionOfInterest(BaseModel):
    type: str
    features: List[dict]

    class Config:
        schema_extra = {
            "example": example_roi_geojson
        }


app = FastAPI()


@app.post("/noise_sim_input/")
def noise_sim_input(region_of_interest: RegionOfInterest):
    return get_noise_sim_input_for_roi(jsonable_encoder(region_of_interest))
