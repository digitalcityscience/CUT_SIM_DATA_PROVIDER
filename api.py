from fastapi import FastAPI, HTTPException
from typing import List

from noise_input_for_roi import get_noise_sim_input_for_roi

app = FastAPI()


@app.get("/noise_sim_input")
async def noise_sim_input(region_of_interest: List[List[float]]):
    return get_noise_sim_input_for_roi(region_of_interest)
