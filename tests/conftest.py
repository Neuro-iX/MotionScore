import os

import pytest

from motscore import create_app
from motscore.db import create_user, init_db, populate_volume

TEST_SYNTETHIC_PATH = "tests/data/bids_sub_ses"
TEST_VOL_PATH = "tests/data/bids_sub_ses/sub-000103/ses-headmotion2/anat/sub-000103_ses-headmotion2_T1w.nii.gz"


@pytest.fixture(autouse=True, scope="function")
def fixt_init_test_db():
    if os.path.exists("tests/test.sqlite"):
        os.remove("tests/test.sqlite")

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": os.path.join("tests", "test.sqlite"),
        }
    )
    with app.test_request_context("/", method="POST"):
        init_db()
        create_user("fake@email.com", "test")
        populate_volume("tests/data/bids_sub_ses")
