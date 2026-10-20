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

## Installation

Requirements: Python >= 3.6 and pip. The only dependency is pandas.

### From a clone
````bash
git clone https://github.com/correalramos24/perfLens.git
cd perfLens
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
.venv/bin/perfLens --help
````
Add the `bin` folder to your `PATH` to call `perfLens` from anywhere: it
runs the clone with `.venv/bin/python`, or with `python3` when there is no
`.venv` (pandas must be installed for that interpreter then).

### Directly from GitHub
````bash
python3 -m venv ~/.venvs/perfLens
~/.venvs/perfLens/bin/pip install git+https://github.com/correalramos24/perfLens.git@overhaul
ln -s ~/.venvs/perfLens/bin/perfLens ~/.local/bin/perfLens   # any folder in your PATH
````

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
