# perfLens
Gather performance metrics from rundirs.

## Use cases
For the selected mode, a user can:
* Get performance metrics for a set of rundirs
* Get performance metrics for an input file(s) (not implemented yet).

The user can *list*, *show* and/or *save* the results.

## Installation

perfLens requires Python >= 3.10 and uses [uv](https://docs.astral.sh/uv/)
to manage its dependencies (pandas, netCDF4, f90nml and
[py-utils](https://github.com/correalramos24/py_utils)).

Install uv if you don't have it yet:
````bash
curl -LsSf https://astral.sh/uv/install.sh | sh
````

Then pick one of the following options.

### Option A: global command (recommended for users)
Install `perfLens` as a standalone tool, available from any folder:
````bash
uv tool install git+https://github.com/correalramos24/perfLens.git@develop
# or, from a local clone:
uv tool install .
````
Upgrade it later with `uv tool upgrade perflens`, or remove it with
`uv tool uninstall perflens`.

### Option B: from a clone (recommended for development)
````bash
git clone https://github.com/correalramos24/perfLens.git
cd perfLens
uv sync                  # create .venv and install all dependencies
uv run perfLens --help   # run the CLI
uv run pytest            # run the tests
````
Optionally, add the `bin` folder to your `PATH` to call `perfLens`
from anywhere: it is a thin wrapper around `uv run` that uses this clone.

## Usage

````
perfLens mode input [input2] [inputN]... [flags]
````

* `mode`: the parser to use: `envparser`, `memparser`, `pidstatparser`,
  `nemo` or `nemo5` (see `perfLens --help`).
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

# Results available for a NEMO5 rundir
perfLens nemo5 inputs/nemo5 --list
````
When running from a clone without installing, prefix the commands
with `uv run` (e.g. `uv run perfLens envparser inputs --explore --list`).


## Extend functionalities

### the ParserManager

### the AbstractParser

## Future

Ideas to be included are welcome.
