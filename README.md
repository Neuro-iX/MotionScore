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

Before starting the server, you will need to: create a database, create a user, and add volumes to score. Fortunately, we provide CLI commands for all three tasks:

To create a new database, simply run:

```bash
flask --app motscore init-db
```

Then, create a user with:

```bash
flask --app motscore create-user --email <your_email>
```

We use a simple user-code-based authentication system, as it is solely for rater identification. This tool is not intended to be deployed outside of local networks.

Finally, you can add your volumes from a BIDS dataset using:

```bash
flask --app motscore populate-volumes --dataset_path <Path_to_BIDS_root>
```

Alternatively, to add multiple BIDS datasets at once, use:

```bash
flask --app motscore populate-volumes --multiple --dataset_path <Path_to_folder_containing_BIDS_roots>
```

### Executing

As this tool relies on Flask, you can run it using:

```bash
flask --app motscore run
```

Upon arriving on the web interface, you will be asked for a user code. Once authenticated, you can start scoring.  
After all volumes have been scored, you can export the labels as a CSV file using:

```bash
flask --app motscore export-csv --output <path_to_output.csv>
```

## Help

For each command, use the `--help` argument to view available options, their purposes, and expected data types.

## Contributing

### Setup

Once the repository is cloned, install the development dependencies with:

```bash
pip install -r dev_requirements.txt
```

### Tests

#### Test Tools

We use:

- `pytest` for unit tests  
- `pytest-cov` for coverage reports (99% test coverage)

Run tests with:

```bash
pytest --cov
```

Other tools for code quality:

- `ruff` for linting and formatting  
- `ssort`, `pydocstyle`, `mypy`, and `pylint` for additional checks

#### Test Data

All test data are extracted from MR-ART:

> Nárai, Á., Hermann, P., Auer, T. et al. Movement-related artefacts (MR-ART) dataset of matched motion-corrupted and clean structural MRI brain scans. *Sci Data* 9, 630 (2022). https://doi.org/10.1038/s41597-022-01694-8

## Authors

Charles Bricout.
