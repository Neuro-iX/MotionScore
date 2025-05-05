"""Main module defining how to create a new flask app."""

import os
from typing import Any

from flask import Flask


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create a new flask app.

    Args:
        test_config (dict[str,Any]|None, optional): dictionnary specifying a config.
         Use only for test. Defaults to None.

    Returns:
        Flask: flask app
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "motscore.sqlite"),
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import motionscore

    app.register_blueprint(motionscore.bp)
    app.add_url_rule("/", endpoint="index")

    return app
