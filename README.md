# perfLens
Gather performance metrics from rundirs.

## Use cases
For the selected mode, a user can:
* Get performance metrics for a set of rundirs
* Get performance metrics for an input file(s) (not implemented yet).

The user can *list*, *show* and/or *save* the results.

## Installation

perfLens requires Python >= 3.10, pip and git. Its dependencies are
pandas and [py-utils](https://github.com/correalramos24/py_utils), which
pip installs directly from GitHub.

### Option A: global command (recommended for users)
Install `perfLens` into a dedicated virtual environment and expose the
command:
````bash
python3 -m venv ~/.venvs/perfLens
~/.venvs/perfLens/bin/pip install --upgrade pip
~/.venvs/perfLens/bin/pip install git+https://github.com/correalramos24/perfLens.git@overhaul
ln -s ~/.venvs/perfLens/bin/perfLens ~/.local/bin/perfLens   # any folder in your PATH
````
Upgrade it later by re-running the `pip install` command with `--upgrade`.

### Option B: from a clone (recommended for development)
````bash
git clone https://github.com/correalramos24/perfLens.git
cd perfLens
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[test]"   # editable install + test dependencies
perfLens --help            # run the CLI
python -m pytest           # run the tests
````
Optionally, add the `bin` folder to your `PATH` to call `perfLens`
from anywhere without activating the virtual environment: it runs this
clone with `.venv/bin/python` (or `python3` if there is no `.venv`).

## Usage

````
perfLens mode input [input2] [inputN]... [flags]
````

* `mode`: the parser to use: `envparser`, `memparser` or `pidstatparser`
  (see `perfLens --help`).
* `input`: one or more rundirs. With `--explore`, the inputs are root folders
  that are searched recursively for rundirs containing files that the selected
  parser understands.

Main flags:

| Flag | Description |
|------|-------------|
| `--explore` | Search the inputs recursively for rundirs |
| `--list` | List the results available in each rundir |
| `--show KEY [KEY ...]` | Parse and print the given result(s) |
| `--cols COL [COL ...]` | Only show the given columns |
| `--sort COL [COL ...]` | Sort the shown records by the given columns |
| `--silent` / `--log` / `--debug` | Change the verbosity |
| `--version` / `--dev-version` | Print the version (and git info) |

### Examples
Using the sample data in `inputs/`:
````bash
# Find rundirs with a SLURM env.log and list what can be extracted
perfLens envparser inputs --explore --list

# Show the SLURM setup (nodes, mpi, omp, tasks) of every rundir found
perfLens envparser inputs --explore --show slurm_data

# Aggregate memory traces (free output, *.mem) and sort by usage
perfLens memparser inputs/free --show mem-data --cols host total used used_perc --sort used_perc

# CPU usage from pidstat logs (*.pstat)
perfLens pidstatparser inputs/pidstat --show samp.pstat
````


## Extend functionalities

### the ParserManager

### the AbstractParser

## Future

Ideas to be included are welcome.
