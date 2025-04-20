import random

import nibabel as nib
import numpy as np
import SimpleITK as sitk


def rescale(vol: np.ndarray) -> np.ndarray:
    return ((vol - vol.min()) * 255.0 / (vol.max() - vol.min())).astype(np.uint8)


def orient(vol: np.ndarray) -> np.ndarray:
    ornt = nib.orientations.axcodes2ornt(("R", "P", "I"))
    return nib.orientations.apply_orientation(vol, ornt)


def crop_image(image, threshold=-1):
    if not isinstance(image, np.ndarray) or image.ndim != 2:
        raise ValueError("Input must be a 2D numpy array.")

    # Find indices where the image exceeds the threshold
    foreground_indices = np.argwhere(image > threshold)

    if foreground_indices.size == 0:
        raise ValueError("No foreground detected with the given threshold.")

    # Calculate the bounding box
    min_row, min_col = foreground_indices.min(axis=0)
    max_row, max_col = (
        foreground_indices.max(axis=0) + 1
    )  # Include max index in the crop

    # Crop the image
    cropped_image = image[min_row:max_row, min_col:max_col]

    return cropped_image


def retrieve_three_slices(
    vol_path: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Retrieve random slice from two volume from the same cut and same slice index
    Both volume should be of same size !
    Args:
        vol_1_path (str): first volume path
        vol_2_path (str): second volume path

    Returns:
        tuple[np.ndarray, np.ndarray]: volume in the order they were provide
    """
    vol: np.ndarray = orient(nib.load(vol_path).get_fdata())

    dim_size = vol.shape

    slice_sagittal = vol.take(indices=max(0, dim_size[0] // 2 - 15), axis=0)
    slice_coronal = vol.take(indices=max(0, dim_size[1] // 2), axis=1)
    slice_axial = vol.take(indices=max(0, dim_size[2] // 2 - 20), axis=2)

    return (
        crop_image(rescale(slice_coronal.T)),
        crop_image(rescale(slice_sagittal.T)),
        crop_image(rescale(slice_axial.T)),
    )
