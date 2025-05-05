import os

import pytest
from click.testing import CliRunner

from motscore import create_app


@pytest.fixture(autouse=True, scope="function")
def fixt_init_test_db():
    if os.path.exists("tests/test.sqlite"):
        os.remove("tests/test.sqlite")


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": os.path.join("tests", "test.sqlite"),
        }
    )
    return app


def test_init_db(runner, app):
    assert not os.path.exists("tests/test.sqlite")
    with app.test_request_context("/", method="POST"):
        response = runner.invoke(app.cli, ["init-db"])
        assert "Initialized the database." in response.output
        assert os.path.exists("tests/test.sqlite")


def test_create_user(runner, app):
    assert not os.path.exists("tests/test.sqlite")
    with app.test_request_context("/", method="POST"):
        runner.invoke(app.cli, ["init-db"])

        response = runner.invoke(app.cli, ["create-user", "--email", "auser@email.com"])
        assert "User inserted, code" in response.output


def test_populate_volume(runner, app):
    assert not os.path.exists("tests/test.sqlite")
    with app.test_request_context("/", method="POST"):
        runner.invoke(app.cli, ["init-db"])

        response = runner.invoke(
            app.cli, ["populate-volumes", "--dataset_path", "tests/data/bids_sub_ses"]
        )
        assert "Inserted 3 volumes." in response.output
        assert os.path.exists("tests/test.sqlite")


def test_populate_volume_multiple(runner, app):
    assert not os.path.exists("tests/test.sqlite")
    with app.test_request_context("/", method="POST"):
        runner.invoke(app.cli, ["init-db"])

        response = runner.invoke(
            app.cli,
            ["populate-volumes", "--dataset_path", "tests/data/multiple", "--multiple"],
        )
        assert "Inserted 1 volumes." in response.output
        assert "Inserted 2 volumes." in response.output

        assert os.path.exists("tests/test.sqlite")


def test_export_csv(runner, app):
    assert not os.path.exists("tests/test.sqlite")

    if os.path.exists("tests/tmp_out/out.csv"):
        os.remove("tests/tmp_out/out.csv")

    with app.test_request_context("/", method="POST"):
        runner.invoke(app.cli, ["init-db"])

        response = runner.invoke(
            app.cli, ["export-csv", "--output", "tests/tmp_out/out.csv"]
        )
        assert "Write at tests/tmp_out/out.csv." in response.output
        assert os.path.exists("tests/tmp_out/out.csv")

        assert os.path.exists("tests/test.sqlite")
