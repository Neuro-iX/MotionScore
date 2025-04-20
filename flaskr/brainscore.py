from flask import Blueprint, jsonify, render_template, request, session

from flaskr.auth import login_required
from flaskr.db import get_db, get_last_reviewed_volume, get_next_volume_to_review, get_review_status, remove_review
from flaskr.utils import array_to_str
from rand_bids import sampler

bp = Blueprint("brainscore", __name__)


@bp.route("/")
@login_required
def index():
    return render_template(
        "brainscore/index.html",
    )


@bp.route("/get_slices", methods=["GET"])
@login_required
def get_slices():

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
def score():
    vol_id = int(request.json.get("vol_id"))
    score = int(request.json.get("score"))
    blur = bool(request.json.get("blur"))
    lines = bool(request.json.get("lines"))


    judge_code = session.get("user_code")

    db = get_db()
    cur = db.cursor()
    # Insert vote into the database
    cur.execute(
        "INSERT INTO review(judge_code, vol_id, score,blur,lines) VALUES (?, ?, ?, ?, ?)",
        (judge_code, vol_id, score, blur, lines),
    )
    db.commit()

    return jsonify({"success": True})


@bp.route("/back", methods=["GET"])
@login_required
def back():

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
