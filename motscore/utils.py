"""Nodule defining small utility functions."""

import base64
import io

import numpy as np
from PIL import Image


def array_to_str(array: np.ndarray) -> str:
    """Convert image array base64 string for HTML display.

    Args:
        array (np.ndarray): array to convert

    Returns:
        str: base64  encoding
    """
    img = Image.fromarray(array)
    raw_bytes = io.BytesIO()
    img.save(raw_bytes, "PNG")
    raw_bytes.seek(0)
    img_base64 = base64.b64encode(raw_bytes.read())
    return img_base64.decode("utf-8")
