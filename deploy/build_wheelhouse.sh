#!/bin/bash
# Download perfLens and its dependencies as wheels, to install perfLens on
# machines without internet access (e.g. HPC clusters).
#
#   deploy/build_wheelhouse.sh                  # for this machine's python3
#   deploy/build_wheelhouse.sh -t 3.6.8         # for python 3.6.8 on x86_64 Linux
#
# Then copy the clone (or just deploy/ and the wheelhouse) to the target and
# run: deploy/install.sh -w wheelhouse
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON=python3
OUT="$ROOT/wheelhouse"
TARGET=""
PLATFORMS=(manylinux2014_x86_64 manylinux2010_x86_64 manylinux1_x86_64)

usage() {
    cat <<USAGE
Usage: $(basename "$0") [options]
  -p PYTHON    python used to build and download (default: $PYTHON)
  -o DIR       output folder (default: $OUT)
  -t VERSION   full target python version (e.g. 3.6.8), when it differs
               from PYTHON
  -P PLATFORM  target platform with -t (default: ${PLATFORMS[*]}),
               can be repeated, e.g. -P manylinux2014_aarch64
  -h           show this help
USAGE
}

CUSTOM_PLATFORMS=()
while getopts "p:o:t:P:h" opt; do
    case $opt in
        p) PYTHON=$OPTARG ;;
        o) OUT=$OPTARG ;;
        t) TARGET=$OPTARG ;;
        P) CUSTOM_PLATFORMS+=("$OPTARG") ;;
        h) usage; exit 0 ;;
        *) usage >&2; exit 1 ;;
    esac
done
if [ ${#CUSTOM_PLATFORMS[@]} -gt 0 ]; then
    PLATFORMS=("${CUSTOM_PLATFORMS[@]}")
fi

mkdir -p "$OUT"
PIP=("$PYTHON" -m pip --disable-pip-version-check)

echo "Building the perfLens wheel"
"${PIP[@]}" wheel -q --no-deps -w "$OUT" "$ROOT"
WHEEL=$(ls -t "$OUT"/perflens-*.whl | head -1)

# pip itself is included so install.sh can upgrade the venv's (old) pip
if [ -z "$TARGET" ]; then
    echo "Downloading dependencies for $("$PYTHON" --version 2>&1)"
    "${PIP[@]}" download -q -d "$OUT" "$WHEEL" pip
else
    echo "Downloading dependencies for python $TARGET (${PLATFORMS[*]})"
    PLATFORM_ARGS=()
    for p in "${PLATFORMS[@]}"; do PLATFORM_ARGS+=(--platform "$p"); done
    "${PIP[@]}" download -q -d "$OUT" --only-binary=:all: \
        --python-version "$TARGET" --implementation cp "${PLATFORM_ARGS[@]}" \
        "$WHEEL" pip
fi

echo "Wheelhouse ready at $OUT:"
ls -1 "$OUT"
