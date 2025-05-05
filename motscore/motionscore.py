"""Module defining the main logique of MotionScore."""

from flask import Blueprint, jsonify, render_template, request, session

from motscore.auth import login_required
from motscore.db import (
    get_last_reviewed_volume,
    get_next_volume_to_review,
    get_review_status,
    remove_review,
    score_volume,
)
from motscore.rand_bids import sampler
from motscore.utils import array_to_str

bp = Blueprint("motionscore", __name__)


@bp.route("/")
@login_required
def index():
    """Render three volume page."""
    return render_template(
        "motionscore/index.html",
    )


@bp.route("/get_slices", methods=["GET"])
@login_required
def get_slices():
    """Retrieve and return slices from an unscored volumes."""
    volume = get_next_volume_to_review(session["user_code"])
    to_do, done, kept = get_review_status(session["user_code"])
    slice1, slice2, slice3 = sampler.retrieve_three_slices(volume["volume_path"])
    # Return slices as JSON response
    return jsonify(
        {
            "vol_id": volume["id"],
            "slice1": array_to_str(slice1),
            "slice2": array_to_str(slice2),
            "slice3": array_to_str(slice3),
            "done": done,
            "to_do": to_do,
            "kept": kept,
        }
    )


@bp.route("/score", methods=["POST"])
@login_required
def apply_score():
    """Apply a score on a volume."""
    vol_id = int(request.json.get("vol_id"))
    score = int(request.json.get("score"))
    blur = bool(request.json.get("blur"))
    lines = bool(request.json.get("lines"))

    judge_code = session.get("user_code")

    score_volume(judge_code, vol_id, score, blur, lines)

    return jsonify({"success": True})


@bp.route("/back", methods=["GET"])
@login_required
def back():
    """Remove review and resend previous slices."""
    volume = get_last_reviewed_volume(session["user_code"])
    remove_review(volume["id"], session["user_code"])
    to_do, done, kept = get_review_status(session["user_code"])
    slice1, slice2, slice3 = sampler.retrieve_three_slices(volume["volume_path"])
    # Return slices as JSON response
    return jsonify(
        {
            "vol_id": volume["id"],
            "slice1": array_to_str(slice1),
            "slice2": array_to_str(slice2),
            "slice3": array_to_str(slice3),
            "done": done,
            "to_do": to_do,
            "kept": kept,
        }
    )
