# perfLens
Gather performance metrics from rundirs.

## Use cases
For the selected mode, a user can:
* Get performance metrics for a set of rundirs
* Get performance metrics for an input file(s) (not implemented yet).

The user can *list*, *show* and/or *save* the results.

## Installation & Usage

Dependencies are managed with [uv](https://docs.astral.sh/uv/):
````bash
git clone https://github.com/correalramos24/perfLens.git
cd perfLens
uv sync              # create .venv and install dependencies
uv run perfLens -h   # run the CLI
uv run pytest        # run the tests
````

Alternatively, add the `bin` folder to your PATH and invoke `perfLens`
directly (it wraps `uv run`), or install it as a global tool with
`uv tool install .`.


## Extend functionalities

### the ParserManager

### the AbstractParser

## Future

Ideas to be included are welcome.
