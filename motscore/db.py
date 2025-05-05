"""Module defining db related functions and commands."""

import base64
import os
import random
import sqlite3
from collections import namedtuple
from typing import Any

import click
import pandas as pd
from flask import current_app, g

from motscore.rand_bids import explorer

Review = namedtuple("Review", ["vol_id", "judge_code", "score", "timestamp"])


def get_db():
    """Fetch db object."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """Close db."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Create a new db following schema."""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


def get_next_volume_to_review(user_code: str) -> sqlite3.Row:
    """Retrieve a random volume not yet reviewed by user.

    Args:
        user_code (str): User code to use

    Returns:
        sqlite3.Row: volume informations
    """
    db = get_db()
    req: list[sqlite3.Row] = db.execute(
        f"""SELECT V.*, R.*
            FROM volume V
            LEFT JOIN review R ON V.id = R.vol_id AND R.judge_code = '{user_code}'
            WHERE R.vol_id IS NULL
            ORDER BY RANDOM()
            """
    ).fetchall()

    return req[0]


def score_volume(
    judge_code: str, vol_id: int, score: int, blur: bool, lines: bool
) -> None | Any:
    """Add score to db.

    Args:
        judge_code (str): current user code
        vol_id (int): volume scored
        score (int): score
        blur (bool): true if blurred
        lines (bool): true if contains lines

    Returns:
        None|Any: commit results
    """
    db = get_db()
    cur = db.cursor()
    # Insert vote into the database
    cur.execute(
        "INSERT INTO review(judge_code, vol_id, score,blur,lines) VALUES (?, ?, ?, ?, ?)",
        (judge_code, vol_id, score, blur, lines),
    )
    return db.commit()


def get_last_reviewed_volume(user_code: str) -> sqlite3.Row:
    """Retrieve a user's last reviewed volume.

    Args:
        user_code (str): user code to use

    Returns:
        sqlite3.Row: last reviewed volume
    """
    db = get_db()
    req: list[sqlite3.Row] = db.execute(
        f"""SELECT V.*, R.*
            FROM volume V
            LEFT JOIN review R ON V.id = R.vol_id AND R.judge_code = '{user_code}'
            WHERE R.vol_id IS NOT NULL
            """
    ).fetchall()

    return req[-1]


def remove_review(volume_id: int, user_code: str):
    """Remove a review identified by volume id and user's code.

    Args:
        volume_id (int): volume reviewed
        user_code (str): user reviewing
    """
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "DELETE FROM review WHERE vol_id=? AND judge_code = ?", (volume_id, user_code)
    )
    db.commit()


def get_review_status(user_code: str) -> tuple[int, int, int]:
    """Get review statistics for a user.

    Args:
        user_code (str): user on which we compute stats

    Returns:
        dict[str, str]: returns three number for volume :
            - Todo : total volumes
            - Done : volume reviewed
            - Kept : volume with sufficient score
    """
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


def create_user(user_email, force_code: None | str = None) -> str:
    """Insert a new user in db.

    Args:
        user_email (_type_): User's email
        force_code (None | str, optional): Option to force a user code. Defaults to None.

    Returns:
        str: new user's code, either forced or randomized
    """
    db = get_db()

    if isinstance(db, sqlite3.Connection):
        if force_code is None:
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
        else:
            str_user_code = force_code
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
    """Populate database with volume inside dataset.

    Args:
        dataset_path (str): path to BIDS dataset

    Returns:
        int: Number of volume inserted
    """
    db = get_db()

    if isinstance(db, sqlite3.Connection):
        volumes = explorer.list_volumes(dataset_path)
        random.shuffle(volumes)
        for vol in volumes:
            cur = db.cursor()
            cur.execute(
                "INSERT INTO volume(sub_id,ses_id,volume_path,dataset) VALUES(?,?,?,?)",
                vol,
            )
        db.commit()
        return len(volumes)
    return 0


@click.command("populate-volumes")
@click.option("--dataset_path", type=str)
@click.option(
    "-m",
    "--multiple",
    help="Toggle when dataset_path is a parent folder that contain multiple dataset",
    is_flag=True,
    type=bool,
)
def populate_volume_command(dataset_path: str, multiple: bool):
    """Populate volume table with dataset volumes."""
    if multiple:
        for ds in os.listdir(dataset_path):
            nb_volume = populate_volume(os.path.join(dataset_path, ds))
            click.echo(f"Inserted {nb_volume} volumes.")
    else:
        nb_volume = populate_volume(dataset_path)
        click.echo(f"Inserted {nb_volume} volumes.")


def export_csv(output: str):
    """Export current review as a csv file.

    Args:
        output (str): csv file path
    """
    db = get_db()
    reviews = db.execute(
        """SELECT sub_id, ses_id, volume_path, judge_code, score, blur, lines, dataset
        FROM review R 
        LEFT JOIN volume V ON V.id = R.vol_id  """
    ).fetchall()
    pd.DataFrame.from_records(
        reviews,
        columns=[
            "sub_id",
            "ses_id",
            "volume_path",
            "judge_code",
            "score",
            "blur",
            "lines",
            "dataset",
        ],
    ).to_csv(output)


@click.command("export-csv")
@click.option("-o", "--output", type=str)
def export_csv_command(output: str):
    """Populate volume table with dataset volumes."""
    export_csv(output)
    click.echo(f"Write at {output}.")


def init_app(app):
    """Add commands to app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_user_command)
    app.cli.add_command(populate_volume_command)
    app.cli.add_command(export_csv_command)
