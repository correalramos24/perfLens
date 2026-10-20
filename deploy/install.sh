#!/bin/bash
# Install perfLens into a virtual environment.
#
#   deploy/install.sh                     # .venv in the clone, from the sources
#   deploy/install.sh -d ~/venvs/perfLens -l ~/.local/bin
#   deploy/install.sh -w wheelhouse       # offline, see build_wheelhouse.sh
#
# Re-running it upgrades perfLens in the existing venv.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON=python3
VENV="$ROOT/.venv"
WHEELS=""
LINK_DIR=""
EDITABLE=0

usage() {
    cat <<USAGE
Usage: $(basename "$0") [options]
  -p PYTHON   python interpreter used to create the venv (default: $PYTHON)
  -d DIR      venv folder (default: $VENV)
  -w DIR      install offline from a wheelhouse built with build_wheelhouse.sh
  -l DIR      link the perfLens command into DIR (e.g. ~/.local/bin)
  -e          editable install (changes in the clone apply without reinstalling)
  -h          show this help
USAGE
}

while getopts "p:d:w:l:eh" opt; do
    case $opt in
        p) PYTHON=$OPTARG ;;
        d) VENV=$OPTARG ;;
        w) WHEELS=$(cd "$OPTARG" && pwd) ;;
        l) LINK_DIR=$OPTARG ;;
        e) EDITABLE=1 ;;
        h) usage; exit 0 ;;
        *) usage >&2; exit 1 ;;
    esac
done

if ! "$PYTHON" -c 'import sys; sys.exit(sys.version_info < (3, 6))' 2>/dev/null; then
    echo "ERROR: $PYTHON not found or older than python 3.6" >&2
    exit 1
fi
if [ -n "$WHEELS" ] && [ "$EDITABLE" = 1 ]; then
    echo "ERROR: -e can't be combined with -w" >&2
    exit 1
fi

if [ -x "$VENV/bin/python" ]; then
    echo "Using existing venv $VENV"
else
    echo "Creating venv $VENV with $("$PYTHON" --version 2>&1)"
    "$PYTHON" -m venv "$VENV"
fi
PIP=("$VENV/bin/python" -m pip --disable-pip-version-check)

if [ -n "$WHEELS" ]; then
    echo "Installing perfLens from $WHEELS (offline)"
    if ls "$WHEELS"/pip-*.whl >/dev/null 2>&1; then
        "${PIP[@]}" install -q --no-index --find-links "$WHEELS" --upgrade pip
    fi
    "${PIP[@]}" install -q --no-index --find-links "$WHEELS" --upgrade perflens
else
    echo "Installing perfLens from $ROOT"
    "${PIP[@]}" install -q --upgrade pip
    if [ "$EDITABLE" = 1 ]; then
        "${PIP[@]}" install -q -e "$ROOT"
    else
        "${PIP[@]}" install -q --upgrade "$ROOT"
    fi
fi

if [ -n "$LINK_DIR" ]; then
    mkdir -p "$LINK_DIR"
    ln -sf "$VENV/bin/perfLens" "$LINK_DIR/perfLens"
    echo "Linked $LINK_DIR/perfLens"
fi

echo "Installed $("$VENV/bin/perfLens" --version) in $VENV"
if [ -z "$LINK_DIR" ]; then
    echo "Run it with $VENV/bin/perfLens, or add $VENV/bin to your PATH"
fi
