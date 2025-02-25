from rand_bids.explorer import list_volumes
from tests import config as testconfig


def test_list_volumes():
    path = testconfig.TEST_SYNTETHIC_PATH
    volumes = list_volumes(path)

    assert len(volumes) == 10
