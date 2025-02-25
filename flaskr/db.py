import base64
import os
import random
import sqlite3
from collections import namedtuple
from datetime import datetime

import click
import pandas as pd
from flask import current_app, g

from rand_bids import explorer

Review = namedtuple("Review", ["vol_id", "judge_code", "score", "timestamp"])


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


def get_volume_map() -> dict[int, dict[str, str | int]]:
    db = get_db()
    vol_req = db.execute("SELECT id, sub_id, ses_id FROM volume").fetchall()
    return {vol["id"]: vol for vol in vol_req}


def get_all_scores() -> list[any]:

    db = get_db()
    volumes_req = db.execute(
        "SELECT id, vol_id, judge_code, score, created_at FROM review ORDER BY created_at"
    ).fetchall()

    scores = [
        Review(
            vol_id=row["vol_id"],
            judge_code=row["judge_code"],
            score=row["score"],
            timestamp=datetime.strptime(
                row["created_at"], "%Y-%m-%d %H:%M:%S"
            ).timestamp(),
        )
        for row in volumes_req
    ]
    return scores


def get_next_volume_to_review(user_code: str) -> dict[str, str]:
    db = get_db()
    req: list[sqlite3.Row] = db.execute(
        f"""SELECT V.*, R.*
            FROM volume V
            LEFT JOIN review R ON V.id = R.vol_id AND R.judge_code = '{user_code}'
            WHERE R.vol_id IS NULL
            """
    ).fetchall()

    return req[0]


def get_review_status(user_code: str) -> dict[str, str]:
    db = get_db()
    to_do: sqlite3.Row = db.execute(
        """SELECT count(V.id) as n_vol
            FROM volume V"""
    ).fetchone()

    done: sqlite3.Row = db.execute(
        f"""SELECT count(R.vol_id) as n_vol
            FROM review R
            WHERE judge_code = '{user_code}'"""
    ).fetchone()

    kept: sqlite3.Row = db.execute(
        f"""SELECT count(R.vol_id) as n_vol
            FROM review R
            WHERE judge_code = '{user_code}' and (score=0 or score=1)"""
    ).fetchone()
    return to_do["n_vol"], done["n_vol"], kept["n_vol"]


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def create_user(user_email):
    db = get_db()

    if isinstance(db, sqlite3.Connection):
        existing_codes_row: list[sqlite3.Row] = db.execute(
            "SELECT user_code FROM user"
        ).fetchall()
        existing_codes: list[str] = list(
            map(lambda x: x["user_code"], existing_codes_row)
        )
        user_code = base64.b64encode(os.urandom(32))[:8]
        while user_code in existing_codes:
            user_code = base64.b64encode(os.urandom(32))[:8]

        str_user_code = user_code.decode("utf-8")
        db.cursor().execute(
            "INSERT INTO user(user_code,email) VALUES(?,?)", (str_user_code, user_email)
        )
        db.commit()
        return str_user_code
    return ""


@click.command("create-user")
@click.option("--email", type=str)
def create_user_command(email):
    """Create new user and display user_code."""
    user_code = create_user(email)
    click.echo(f"User inserted, code : {user_code} .")


def populate_volume(dataset_path: str) -> int:
    db = get_db()

    if isinstance(db, sqlite3.Connection):
        volumes = explorer.list_volumes(dataset_path)
        random.shuffle(volumes)
        for vol in volumes:
            cur = db.cursor()
            cur.execute(
                "INSERT INTO volume(sub_id,ses_id,volume_path) VALUES(?,?,?)", vol
            )
        db.commit()
        return len(volumes)
    return 0


@click.command("populate-volumes")
@click.option("--dataset_path", type=str)
def populate_volume_command(dataset_path: str):
    """Populate volume table with dataset volumes"""
    nb_volume = populate_volume(dataset_path)
    click.echo(f"Inserted {nb_volume} volumes.")


def export_csv(output: str):
    db = get_db()
    reviews = db.execute(
        """SELECT sub_id, ses_id, volume_path, judge_code, score 
        FROM review R 
        LEFT JOIN volume V ON V.id = R.vol_id  """
    ).fetchall()
    pd.DataFrame.from_records(
        reviews, columns=["sub_id", "ses_id", "volume_path", "judge_code", "score"]
    ).to_csv(output)


@click.command("export-csv")
@click.option("-o", "--output", type=str)
def export_csv_command(output: str):
    """Populate volume table with dataset volumes"""
    export_csv(output)
    click.echo(f"Write at {output}.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_user_command)
    app.cli.add_command(populate_volume_command)
    app.cli.add_command(export_csv_command)
