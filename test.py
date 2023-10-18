from fastapi.testclient import TestClient
from api import app
from fixtures.example_input import example_roi_geojson
from fixtures.example_output import example_api_output

client = TestClient(app)


def test_noise_sim_input():

    response = client.post("/noise_sim_input/", json=example_roi_geojson)

    assert response.status_code == 200
    assert response.json() == example_api_output
