import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


@pytest.fixture
def sample_roi_input():
    with open(
        Path(__file__).parent.parent / "api/fixtures/example_roi_input.geojson", "r"
    ) as f:
        return json.load(f)


@pytest.fixture
def sample_streets_output():
    with open(
        Path(__file__).parent.parent / "api/fixtures/example_streets_output.geojson",
        "r",
    ) as f:
        return json.load(f)


@pytest.fixture
def sample_buildings_output():
    with open(
        Path(__file__).parent.parent / "api/fixtures/example_buildings_output.geojson",
        "r",
    ) as f:
        return json.load(f)


def test_streets(sample_roi_input, sample_streets_output):
    response = client.post("/streets/", json=sample_roi_input)

    assert response.status_code == 200
    assert response.json() == sample_streets_output


def test_buildings(sample_roi_input, sample_buildings_output):
    response = client.post("/buildings/", json=sample_roi_input)

    assert response.status_code == 200
    assert response.json() == sample_buildings_output
