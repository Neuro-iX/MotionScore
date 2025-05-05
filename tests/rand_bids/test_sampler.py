import numpy as np

from motscore.rand_bids import sampler
from tests import conftest as testconfig


def test_rescale_changes_axes():
    vol = np.zeros((3, 4, 5))
    vol[0, 0, 0] = -1
    vol[1, 1, 1] = 1

    rescaled = sampler.rescale(vol)

    assert rescaled.max() == 255
    assert rescaled.min() == 0
    assert rescaled[1, 0, 1] == 255 // 2


def test_orient_changes_axes():
    vol = np.zeros((3, 4, 5))
    for i in range(3):
        vol[i, :, :] = i
    affine = np.diag([-1, 1, -1, 1])
    result = sampler.orient(vol, affine)
    assert result.shape != vol.shape or not np.allclose(result, vol)


def test_retrieve_three_slices():
    slices = sampler.retrieve_three_slices(testconfig.TEST_VOL_PATH)

    assert len(slices) == 3
    assert slices[0].ndim == 2
    assert slices[0].max() == 255 and slices[0].min() == 0
