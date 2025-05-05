"""Module to sample slices from MRI volumes."""

import nibabel as nib
import numpy as np


def rescale(vol: np.ndarray) -> np.ndarray:
    """Rescale pixels values between 0 and 255.

    Args:
        vol (np.ndarray): Numpy array containing the MRI

    Returns:
        np.ndarray: Rescaled MRI
    """
    return ((vol - vol.min()) * 255.0 / (vol.max() - vol.min())).astype(np.uint8)


def orient(vol: np.ndarray, affine: np.ndarray) -> np.ndarray:
    """Orient volumes on the RPI axis.

    This orientation allow us to directly slice using numpy without
    further manipulation.

    Args:
        vol (np.ndarray): volume to orient

    Returns:
        np.ndarray: oriented volume
    """
    current_ornt = nib.orientations.io_orientation(affine)
    target_ornt = nib.orientations.axcodes2ornt(("R", "P", "I"))
    transform = nib.orientations.ornt_transform(current_ornt, target_ornt)
    return nib.orientations.apply_orientation(vol, transform)


def retrieve_three_slices(
    vol_path: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Retrieve three slices from a volume from standard cuts.

    Args:
        vol_path (str): volume path

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: slices
    """
    nib_img = nib.load(vol_path)
    vol: np.ndarray = orient(nib_img.get_fdata(), nib_img.affine)

    dim_size = vol.shape

    slice_sagittal = vol.take(indices=max(0, dim_size[0] // 2 - 15), axis=0)
    slice_coronal = vol.take(indices=max(0, dim_size[1] // 2), axis=1)
    slice_axial = vol.take(indices=max(0, dim_size[2] // 2 - 20), axis=2)

    return (
        rescale(slice_coronal.T),
        rescale(slice_sagittal.T),
        rescale(slice_axial.T),
    )
