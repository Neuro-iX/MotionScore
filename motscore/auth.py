"""Module handling the authentification process."""

import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from motscore.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.before_app_request
def load_logged_in_user():
    """Check for logged user in session."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Define login route."""
    if request.method == "POST":
        user_code = request.form["user_code"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE user_code = ?", (user_code,)
        ).fetchone()

        if user is None:
            error = "Incorrect User Code."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            session["user_code"] = user["user_code"]

            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear session and redirect to base."""
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    """Guard routes to guarantee logged user."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        """Define decorator."""
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
