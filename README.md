# MotionScore

Tool used to filter data before generating synthetic motion in our *Imaging Neuroscience* article.  
This repository can be used to train new models and replicate our study.

## Getting Started

### Installation

1. Clone the repository:

    ```bash
    git clone <URL>
    ```

2. Set up a new Python environment using conda, venv, or any other tool (we used Python 3.11).  
3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Setup

Before starting the server, you will need to: create a database, create a user, and add volumes to score. Fortunately, we provide CLI commands for these three tasks:

To create a new database, simply use:

```bash
flask --app motscore init-db
```

Then create a user with:

```bash
flask --app motscore create-user --email <your_email>
```

We use a simple user-code-based authentication system, as it is solely for rater identification. This tool is not intended to be deployed outside of local networks.

Finally, you can add your volume from a BIDS dataset using:

```bash
flask --app motscore populate-volumes --dataset_path <Path_to_BIDS_root>
```

Alternatively, if you want to add multiple BIDS datasets at once, you can use:

```bash
flask --app motscore populate-volumes --multiple --dataset_path <Path_to_folder_containing_BIDS_roots>
```

### Executing

As this tool relies on Flask, you can run it using:

```bash
flask --app motscore run
```

## Help

For each command, use the `--help` argument to see available options, their purposes, and their data types.

## Tools Used for Project Quality

- `ruff`  
- `isort`  
- `ssort`  
- `pylint` (to double-check `ruff` linting)  
- `mypy`  
- `pydocstyle`  

## Authors

Charles Bricout.
