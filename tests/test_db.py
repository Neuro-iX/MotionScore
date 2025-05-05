import os
import sqlite3

import pandas as pd
import pytest

from motscore import create_app
from motscore.db import (
    create_user,
    export_csv,
    get_db,
    get_last_reviewed_volume,
    get_next_volume_to_review,
    get_review_status,
    init_db,
    populate_volume,
    remove_review,
    score_volume,
)


@pytest.fixture
def fixt_init_test_db():
    if os.path.exists("tests/test.sqlite"):
        os.remove("tests/test.sqlite")


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": os.path.join("tests", "test.sqlite"),
        }
    )
    yield app


@pytest.fixture
def init_app(app):
    with app.test_request_context("/", method="POST"):
        init_db()
        create_user("fake@email.com", "test")
        n = populate_volume("tests/data/bids_sub_ses")
        print(f"populated {n}")
    yield app


def test_get_db(fixt_init_test_db, app):
    assert not os.path.exists("tests/test.sqlite")

    with app.test_request_context("/", method="POST"):
        db = get_db()
        assert isinstance(db, sqlite3.Connection)
    assert os.path.exists("tests/test.sqlite")


def test_init_db(fixt_init_test_db, app):
    assert not os.path.exists("tests/test.sqlite")

    expected_tables = {"user", "volume", "review"}
    with app.test_request_context("/", method="POST"):
        init_db()

        db = get_db()
        cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row["name"] for row in cursor.fetchall()}

    assert expected_tables.issubset(tables)


def test_get_next_volume_to_review(init_app):
    with init_app.test_request_context("/", method="POST"):
        next_vol = get_next_volume_to_review("test")
        keys = next_vol.keys()
        assert "id" in keys
        assert "volume_path" in keys
        assert "sub_id" in keys
        assert "ses_id" in keys
        assert "dataset" in keys


def test_score_volume(init_app):
    with init_app.test_request_context("/", method="POST"):
        scored = score_volume("test", 1, 0, False, False)
        assert scored is None

        db = get_db()
        cursor = db.execute("SELECT * FROM review")
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0]["vol_id"] == 1
        assert rows[0]["judge_code"] == "test"
        assert rows[0]["score"] == 0
        assert not rows[0]["blur"]
        assert not rows[0]["lines"]


def test_get_last_reviewed_volume(init_app):
    with init_app.test_request_context("/", method="POST"):
        score_volume("test", 1, 0, False, False)

        last_vol = get_last_reviewed_volume("test")
        keys = last_vol.keys()
        assert last_vol["id"] == 1
        assert "volume_path" in keys
        assert "sub_id" in keys
        assert "ses_id" in keys
        assert "dataset" in keys


def test_remove_review(init_app):
    with init_app.test_request_context("/", method="POST"):
        score_volume("test", 1, 0, False, False)
        remove_review(1, "test")

        db = get_db()
        cursor = db.execute("SELECT * FROM review")
        rows = cursor.fetchall()
        assert len(rows) == 0


def test_get_review_status_clear(init_app):
    with init_app.test_request_context("/", method="POST"):
        todo, done, kept = get_review_status("test")

        assert todo == 3
        assert done == 0
        assert kept == 0


def test_get_review_status_nokept(init_app):
    with init_app.test_request_context("/", method="POST"):
        score_volume("test", 1, 4, False, False)
        todo, done, kept = get_review_status("test")

        assert todo == 3
        assert done == 1
        assert kept == 0


def test_get_review_status_kept(init_app):
    with init_app.test_request_context("/", method="POST"):
        score_volume("test", 1, 0, False, False)
        todo, done, kept = get_review_status("test")

        assert todo == 3
        assert done == 1
        assert kept == 1


def test_create_user_rand(init_app):
    with init_app.test_request_context("/", method="POST"):
        code = create_user("email@test.com")
        db = get_db()
        cursor = db.execute("SELECT * FROM user")
        rows = cursor.fetchall()
        assert len(rows) == 2
        user = rows[1]
        assert user["email"] == "email@test.com"
        assert user["user_code"] == code


def test_create_user_force(init_app):
    with init_app.test_request_context("/", method="POST"):
        code = create_user("email@test.com", force_code="forced")
        db = get_db()
        cursor = db.execute("SELECT * FROM user")
        rows = cursor.fetchall()
        assert len(rows) == 2
        user = rows[1]
        assert user["email"] == "email@test.com"
        assert user["user_code"] == "forced"
        assert code == "forced"


def test_populate_volumes(fixt_init_test_db, app):
    with app.test_request_context("/", method="POST"):
        init_db()

        n_volumes = populate_volume("tests/data/bids_sub_ses")
        db = get_db()
        cursor = db.execute("SELECT * FROM volume ORDER BY sub_id DESC")
        rows = cursor.fetchall()
        assert n_volumes == 3
        assert len(rows) == n_volumes
        vol = rows[0]
        assert vol["sub_id"] == "000148"
        assert vol["ses_id"] == "headmotion2"
        assert vol["dataset"] == "bids_sub_ses"
        assert (
            "/tests/data/bids_sub_ses/sub-000148/ses-headmotion2/anat/"
            "sub-000148_ses-headmotion2_T1w.nii.gz"
        ) in vol["volume_path"]


def test_export_csv(init_app):
    with init_app.test_request_context("/", method="POST"):
        score_volume("test", 1, 0, False, False)
        score_volume("test", 2, 6, False, False)
        score_volume("test", 3, 3, True, True)

        export_csv("tests/tmp_out/tmp_export.csv")

        csv = pd.read_csv("tests/tmp_out/tmp_export.csv", index_col=0)
        assert {
            "sub_id",
            "ses_id",
            "volume_path",
            "judge_code",
            "score",
            "blur",
            "lines",
            "dataset",
        } == set(csv.columns)
        assert len(csv) == 3
        assert csv["score"][0] == 0
        assert csv["blur"][1] == 0
        assert csv["lines"][2] == 1

        os.remove("tests/tmp_out/tmp_export.csv")
