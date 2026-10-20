# perfLens
Gather performance metrics from rundirs.

perfLens finds the rundirs of a job (or receives them directly), parses the
files it knows about and merges the results of all the rundirs into tables
that can be printed, saved to CSV or used from Python.

| Mode | Files | Result | Content |
|------|-------|--------|---------|
| `env` | `env.log` | `slurm` | SLURM setup of the job: nodes, mpi (tasks per node), omp (cpus per task), tasks |
| `mem` | `*.mem` | `mem` | Memory usage sampled with `free` (GiB and % used, one row per sample and host) |
| `pidstat` | `*.pstat` | `cpu` | Per-process CPU usage from `pidstat` |
| `jsonl` | `*.jsonl`, `*.ndjson` | `records` | One row per JSON object (one object per line); nested objects become dotted columns (`mem.rss_mb`) |

## Installation

Requirements: Python >= 3.6. The only dependency is pandas.
The `deploy/` scripts install perfLens into a virtual environment.

### With internet access
````bash
git clone https://github.com/correalramos24/perfLens.git
cd perfLens
deploy/install.sh                                  # venv in .venv
deploy/install.sh -d ~/venvs/perfLens -l ~/.local/bin   # custom venv + perfLens in PATH
````
Options: `-p PYTHON` interpreter for the venv, `-d DIR` venv folder,
`-l DIR` link the `perfLens` command into DIR, `-e` editable install for
development. Re-run it to upgrade perfLens.

### Without internet access (e.g. HPC clusters)
On a machine with internet, download perfLens and its dependencies into a
`wheelhouse/` folder, for the Python version of the target machine:
````bash
deploy/build_wheelhouse.sh -t 3.6.8      # full version of the target python
````
Copy the clone (including `wheelhouse/`) to the target machine and run:
````bash
deploy/install.sh -w wheelhouse -l ~/.local/bin
````
Without `-t`, the wheelhouse targets the python used to build it (`-p`).
`-P PLATFORM` selects another platform (default: x86_64 Linux).

### Running from the clone
`bin/perfLens` runs the clone with `.venv/bin/python` (as created by
`deploy/install.sh`), or with `python3` when there is no `.venv`.
Add the `bin` folder to your `PATH` to call it from anywhere.

## Usage

````
perfLens MODE INPUT [INPUT ...] [options]
````
The inputs are rundirs or, with `--explore`, root folders that are searched
recursively for rundirs containing files of the selected mode. By default,
every result is printed; messages go to stderr, so stdout can be redirected.

| Option | Description |
|--------|-------------|
| `-e`, `--explore` | Search the inputs recursively for rundirs |
| `-l`, `--list` | List the rundirs found and their available results |
| `-s`, `--show KEY [KEY ...]` | Only show these results |
| `-c`, `--cols COL [COL ...]` | Only show these columns |
| `--sort COL [COL ...]` | Sort the rows by these columns (`--desc` for descending) |
| `-o`, `--save DIR` | Also save each result to `DIR/<key>.csv` |
| `-q`, `--quiet` / `-d`, `--debug` | Less / more messages |
| `-V`, `--version` | Print the version |

### Examples
Using the sample data in `inputs/`:
````bash
# Rundirs with an env.log and what can be extracted from them
perfLens env inputs --explore --list

# SLURM setup of every rundir found
perfLens env inputs --explore

# Memory usage per host, highest usage first, also saved to results/mem.csv
perfLens mem inputs/free --cols host time used used_perc --sort used_perc --desc --save results

# Processes with the highest CPU usage
perfLens pidstat inputs/pidstat --cols time PID %CPU Command --sort %CPU --desc

# Steps with the highest memory peak, from JSON Lines logs (one per rank)
perfLens jsonl inputs/jsonl --cols file step elapsed_s mem.peak_mb --sort mem.peak_mb --desc
````

### From Python
````python
import perfLens

results = perfLens.collect("mem", ["inputs"], explore=True)  # {key: DataFrame}
df = results["mem"]
````
See the notebooks in `notebooks/`.

## Development

````bash
.venv/bin/python -m unittest     # run the tests
````

Project layout:
````
perfLens/
  cli.py          command line interface
  core.py         find rundirs, run the parsers and merge their results
  utils.py        logging and file helpers
  parsers/        one module per mode, based on parsers/base.py
tests/            unit tests and their data
inputs/           sample rundirs
````

### Adding a parser
1. Create `perfLens/parsers/<name>.py` with a subclass of `Parser` that sets
   `name` (the mode), `patterns` (files that identify a rundir) and `results`
   (the keys it produces), and implements `parse()`, returning
   `{key: DataFrame}`. Use `self.files()` to get the matching files.
2. Register it in `PARSERS` in `perfLens/parsers/__init__.py`.

perfLens adds the `rundir` column and merges the tables of all rundirs.
