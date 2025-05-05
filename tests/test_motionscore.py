import base64
import io
import os

import numpy as np
import pytest
from PIL import Image

from motscore import create_app


@pytest.fixture
def client():
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": os.path.join("tests", "test.sqlite"),
        }
    )
    with app.test_client() as client:
        client.post("/auth/login", data={"user_code": "test"})
        yield client


def test_index(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Scoring" in response.data


def test_get_slices(client):
    response = client.get("/get_slices")

    assert response.status_code == 200
    assert isinstance(response.json["vol_id"], int)
    assert response.json["done"] == 0
    assert response.json["to_do"] == 3
    assert response.json["kept"] == 0

    base64_decoded = base64.b64decode(response.json["slice1"])

    image = Image.open(io.BytesIO(base64_decoded))
    image_np = np.array(image)
    assert image_np.shape == (256, 192)


def test_score(client):
    response = client.post(
        "/score", json={"vol_id": 1, "score": 3, "blur": True, "lines": False}
    )

    assert response.status_code == 200
    response = client.get("/get_slices")

    assert response.status_code == 200
    assert response.json["done"] == 1
    assert response.json["to_do"] == 3
    assert response.json["kept"] == 0


def test_score_kept(client):
    response = client.post(
        "/score", json={"vol_id": 1, "score": 0, "blur": False, "lines": False}
    )

    assert response.status_code == 200
    response = client.get("/get_slices")

    assert response.status_code == 200
    assert response.json["done"] == 1
    assert response.json["to_do"] == 3
    assert response.json["kept"] == 1


def test_back(client):
    response_score = client.post(
        "/score", json={"vol_id": 1, "score": 0, "blur": False, "lines": False}
    )
    assert response_score.status_code == 200

    response = client.get("/back")
    assert response.status_code == 200
    assert response.json["done"] == 0
    assert response.json["to_do"] == 3
    assert response.json["kept"] == 0
