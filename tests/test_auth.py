import os

import pytest

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
        yield client


def test_login(client):
    response = client.get("/auth/login")

    assert response.status_code == 200
    assert b"Log In" in response.data
    assert b"User Code" in response.data

    with client.session_transaction() as session:
        assert "user_code" not in session


def test_login_post(client):
    response = client.post("/auth/login", data={"user_code": "test"})

    assert response.status_code == 302
    assert b"Redirecting" in response.data

    with client.session_transaction() as session:
        assert session["user_code"] == "test"


def test_login_post_fail(client):
    response = client.post("/auth/login", data={"user_code": "Failed"})

    assert response.status_code == 200
    assert b"Incorrect User Code." in response.data

    with client.session_transaction() as session:
        assert "user_code" not in session


def test_logout(client):
    client.post("/auth/login", data={"user_code": "test"})
    with client.session_transaction() as session:
        assert session["user_code"] == "test"

    response = client.get("/auth/logout")

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert "user_code" not in session


def test_redirected(client):
    response = client.get("/")

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert "user_code" not in session
