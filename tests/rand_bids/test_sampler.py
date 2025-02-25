import numpy as np
from rand_bids import sampler
from tests import config as testconfig


def test_list_volumes():
    vol1, vol2 = sampler.retrieve_random_slices(
        testconfig.TEST_VOL1_PATH, testconfig.TEST_VOL2_PATH
    )

    assert isinstance(vol1, np.ndarray)
    assert isinstance(vol2, np.ndarray)
    assert len(vol1.shape) == 2
    assert len(vol2.shape) == 2
