import base64
import io
from typing import Callable

import numpy as np
import pandas as pd
import seaborn as sb
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image

from flaskr import config, db


def array_to_str(array: np.ndarray) -> str:
    img = Image.fromarray(array)
    rawBytes = io.BytesIO()
    img.save(rawBytes, "PNG")
    rawBytes.seek(0)
    img_base64 = base64.b64encode(rawBytes.read())
    return img_base64.decode("utf-8")


def extract_sub(bids_name):
    # sub is the first 10 characters of the bids name
    return bids_name[4:10]


def extract_ses(bids_name):
    if "standard" in bids_name:
        return "standard"
    elif "headmotion1" in bids_name:
        return "headmotion1"
    else:
        return "headmotion2"


def scores_df() -> pd.DataFrame:
    score = pd.read_csv("./flaskr/static/scores.tsv", sep="\t")
    score["sub_id"] = score["bids_name"].apply(extract_sub).astype(int)
    score["ses_id"] = score["bids_name"].apply(extract_ses)
    return score


def load_scores() -> Callable[[int, str], int]:
    score = scores_df()

    def get_score(sub_id: int, ses_id: str):
        return score[(score["sub_id"] == int(sub_id)) & (score["ses_id"] == ses_id)][
            "score"
        ].iloc[0]

    return get_score
