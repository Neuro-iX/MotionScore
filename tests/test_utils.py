import base64
import io

import numpy as np
from PIL import Image

from motscore.utils import array_to_str


def test_array_to_str():
    img = np.zeros((10, 10), dtype=np.int32)
    img[5, 5] = 255
    img[9, 9] = 1

    encoded = array_to_str(img)

    base64_decoded = base64.b64decode(encoded)

    image = Image.open(io.BytesIO(base64_decoded))
    image_np = np.array(image)

    assert np.allclose(img, image_np)
    assert image_np[5, 5] == 255
    assert image_np[9, 9] == 1
